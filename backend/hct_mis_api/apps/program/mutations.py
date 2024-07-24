from datetime import datetime
from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.db import transaction

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    decode_id_string_required,
    get_program_id_from_headers,
)
from hct_mis_api.apps.core.validators import (
    CommonValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
)
from hct_mis_api.apps.program.celery_tasks import copy_program_task
from hct_mis_api.apps.program.inputs import (
    CopyProgramInput,
    CreateProgramCycleInput,
    CreateProgramInput,
    UpdateProgramCycleInput,
    UpdateProgramInput,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.program.schema import ProgramNode
from hct_mis_api.apps.program.utils import (
    copy_program_object,
    create_program_partner_access,
    remove_program_partner_access,
)
from hct_mis_api.apps.program.validators import (
    ProgramCycleDeletionValidator,
    ProgramCycleValidator,
    ProgramDeletionValidator,
    ProgrammeCodeValidator,
    ProgramValidator,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin


class CreateProgram(
    CommonValidator,
    ProgrammeCodeValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
    PermissionMutation,
    ValidationErrorMutationMixin,
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CreateProgram":
        business_area_slug = program_data.pop("business_area_slug", None)
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.has_permission(info, Permissions.PROGRAMME_CREATE, business_area)

        if not (data_collecting_type_code := program_data.pop("data_collecting_type_code", None)):
            raise ValidationError("DataCollectingType is required for creating new Program")
        data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)
        partner_access = program_data.get("partner_access", [])
        partners_data = program_data.pop("partners", [])
        programme_code = program_data.get("programme_code", "")
        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code

        partner = info.context.user.partner

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
            data_collecting_type=data_collecting_type,
            business_area=business_area,
            programme_code=programme_code,
            partners_data=partners_data,
            partner_access=partner_access,
            partner=partner,
        )

        program = Program(
            **program_data, status=Program.DRAFT, business_area=business_area, data_collecting_type=data_collecting_type
        )
        program.full_clean()
        program.save()
        ProgramCycle.objects.create(
            program=program,
            start_date=program.start_date,
            end_date=None,
            status=ProgramCycle.DRAFT,
        )
        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, partner_access)

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)
        return CreateProgram(program=program)


class UpdateProgram(
    ProgramValidator,
    ProgrammeCodeValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
    PermissionMutation,
    ValidationErrorMutationMixin,
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict, **kwargs: Any) -> "UpdateProgram":
        program_id = decode_id_string(program_data.pop("id", None))
        program = Program.objects.select_for_update().get(id=program_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), program)
        old_program = Program.objects.get(id=program_id)
        business_area = program.business_area
        partners_data = program_data.pop("partners", [])
        partner = info.context.user.partner
        partner_access = program_data.get("partner_access", program.partner_access)
        programme_code = program_data.get("programme_code", "")

        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code

        # status update permissions if status is passed
        status_to_set = program_data.get("status")
        if status_to_set and program.status != status_to_set:
            if status_to_set == Program.ACTIVE:
                cls.has_permission(info, Permissions.PROGRAMME_ACTIVATE, business_area)
            elif status_to_set == Program.FINISHED:
                cls.has_permission(info, Permissions.PROGRAMME_FINISH, business_area)

                # check if all cycles are finished
                if program.cycles.exclude(status=ProgramCycle.FINISHED).count() > 0:
                    raise ValidationError("You cannot finish program if program has not finished cycles")

        if status_to_set not in [Program.ACTIVE, Program.FINISHED]:
            cls.validate_partners_data(
                partners_data=partners_data,
                partner_access=partner_access,
                partner=partner,
            )
        data_collecting_type_code = program_data.pop("data_collecting_type_code", None)
        data_collecting_type = old_program.data_collecting_type
        if data_collecting_type_code and data_collecting_type_code != data_collecting_type.code:
            data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)

        # permission if updating any other fields
        if [k for k, v in program_data.items() if k != "status"]:
            cls.has_permission(info, Permissions.PROGRAMME_UPDATE, business_area)
        cls.validate(
            program_data=program_data,
            program=program,
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
            data_collecting_type=data_collecting_type,
            business_area=business_area,
            programme_code=programme_code,
            excluded_validators="validate_partners_data",
        )
        if program.status == Program.FINISHED:
            # Only reactivation is possible
            status = program_data.get("status")
            if status != Program.ACTIVE or len(program_data) > 1:
                raise ValidationError("You cannot change finished program")

        if data_collecting_type_code:
            program.data_collecting_type = data_collecting_type

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)
        program.full_clean()
        # update partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if (
            status_to_set not in [Program.ACTIVE, Program.FINISHED]
            and partner_access == Program.SELECTED_PARTNERS_ACCESS
        ):
            partners_data = create_program_partner_access(partners_data, program, partner_access)
            remove_program_partner_access(partners_data, program)
        program.save()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, old_program, program)
        return UpdateProgram(program=program)


class DeleteProgram(ProgramDeletionValidator, PermissionMutation):
    ok = graphene.Boolean()

    class Arguments:
        program_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "DeleteProgram":
        decoded_id = decode_id_string(kwargs.get("program_id"))
        program = Program.objects.get(id=decoded_id)
        old_program = Program.objects.get(id=decoded_id)

        cls.has_permission(info, Permissions.PROGRAMME_REMOVE, program.business_area)

        cls.validate(program=program)

        program.delete()
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, old_program, program)
        return cls(ok=True)


class CopyProgram(
    CommonValidator, ProgrammeCodeValidator, PartnersDataValidator, PermissionMutation, ValidationErrorMutationMixin
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CopyProgramInput(required=True)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CopyProgram":
        program_id = decode_id_string_required(program_data.pop("id"))
        partners_data = program_data.pop("partners", [])
        partner_access = program_data.get("partner_access", [])
        business_area = Program.objects.get(id=program_id).business_area
        programme_code = program_data.get("programme_code", "")
        partner = info.context.user.partner
        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code
        cls.has_permission(info, Permissions.PROGRAMME_DUPLICATE, business_area)

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
            programme_code=programme_code,
            business_area=business_area,
            partners_data=partners_data,
            partner_access=partner_access,
            partner=partner,
        )
        program = copy_program_object(program_id, program_data)

        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, partner_access)
        copy_program_task.delay(copy_from_program_id=program_id, new_program_id=program.id)
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)

        return CopyProgram(program=program)


class CreateProgramCycle(ProgramCycleValidator, PermissionMutation, ValidationErrorMutationMixin):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_cycle_data = CreateProgramCycleInput(required=True)

    @classmethod
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_cycle_data: Dict) -> "CreateProgramCycle":
        program_id = get_program_id_from_headers(info.context.headers)
        program = Program.objects.get(id=program_id)

        cls.has_permission(info, Permissions.PM_PROGRAMME_CYCLE_CREATE, program.business_area)

        cls.validate(
            start_date=program_cycle_data["start_date"],
            end_date=program_cycle_data.get("end_date"),
            title=program_cycle_data["title"],
            program=program,
            is_create_action=True,
        )

        ProgramCycle.objects.create(
            title=program_cycle_data["title"],
            program=program,
            start_date=program_cycle_data["start_date"],
            end_date=program_cycle_data.get("end_date"),
            status=ProgramCycle.DRAFT,
        )
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)
        return CreateProgramCycle(program=program)


class UpdateProgramCycle(ProgramCycleValidator, PermissionMutation, ValidationErrorMutationMixin):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_cycle_data = UpdateProgramCycleInput()
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_cycle_data: Dict, **kwargs: Any) -> "UpdateProgramCycle":
        program_cycle_id = decode_id_string(program_cycle_data.pop("program_cycle_id", None))

        program_cycle = ProgramCycle.objects.select_for_update().get(id=program_cycle_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), program_cycle)
        program = program_cycle.program
        business_area = program.business_area

        cls.has_permission(info, Permissions.PM_PROGRAMME_CYCLE_UPDATE, business_area)

        validation_kwargs_dict = {"program": program, "program_cycle": program_cycle}
        input_fields = ["title", "start_date", "end_date"]
        for input_field in input_fields:
            if input_field in program_cycle_data:
                validation_kwargs_dict.update({input_field: program_cycle_data.get(input_field)})

        cls.validate(**validation_kwargs_dict)

        if start_date := program_cycle_data.get("start_date"):
            program_cycle.start_date = start_date

        if end_date := program_cycle_data.get("end_date"):
            program_cycle.end_date = end_date

        if title := program_cycle_data.get("title"):
            program_cycle.title = title

        program_cycle.save()
        # TODO: do we need logs for Program Cycle?
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, program, program)
        return UpdateProgramCycle(program=program)


class DeleteProgramCycle(ProgramCycleDeletionValidator, PermissionMutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_cycle_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "DeleteProgramCycle":
        decoded_id = decode_id_string(kwargs.get("program_cycle_id"))
        program_cycle = ProgramCycle.objects.get(id=decoded_id)
        old_program_cycle = ProgramCycle.objects.get(id=decoded_id)
        program = old_program_cycle.program

        cls.has_permission(info, Permissions.PM_PROGRAMME_CYCLE_DELETE, program.business_area)

        cls.validate(program_cycle=program_cycle)

        program_cycle.delete()
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, program, program)
        return cls(program=program)


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
    copy_program = CopyProgram.Field()

    # program cycle
    create_program_cycle = CreateProgramCycle.Field()
    update_program_cycle = UpdateProgramCycle.Field()
    delete_program_cycle = DeleteProgramCycle.Field()
