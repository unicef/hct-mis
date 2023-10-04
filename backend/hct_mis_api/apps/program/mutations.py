from datetime import datetime
from typing import Any, Dict

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
)
from hct_mis_api.apps.core.validators import CommonValidator
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
    get_program_id_from_headers,
)
from hct_mis_api.apps.program.validators import (
    ProgramCycleDeletionValidator,
    ProgramCycleValidator,
    ProgramDeletionValidator,
    ProgramValidator,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin


class CreateProgram(CommonValidator, PermissionMutation, ValidationErrorMutationMixin):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CreateProgram":
        business_area_slug = program_data.pop("business_area_slug", None)
        business_area = BusinessArea.objects.get(slug=business_area_slug)
        data_collecting_type_code = program_data.pop("data_collecting_type_code", None)
        data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)
        cls.has_permission(info, Permissions.PROGRAMME_CREATE, business_area)

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
        )

        program = Program(
            **program_data, status=Program.DRAFT, business_area=business_area, data_collecting_type=data_collecting_type
        )
        program.full_clean()
        program.save()
        ProgramCycle.objects.create(
            name="Default Program Cycle",
            program=program,
            start_date=program.start_date,
            end_date=None,
            status=ProgramCycle.DRAFT,
        )
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)
        return CreateProgram(program=program)


class UpdateProgram(ProgramValidator, PermissionMutation, ValidationErrorMutationMixin):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict, **kwargs: Any) -> "UpdateProgram":
        # When a Program is Finished, no changes can be applied to the Program and its children (Payment Plan, Follow-Up Payment Plan).

        program_id = decode_id_string(program_data.pop("id", None))

        program = Program.objects.select_for_update().get(id=program_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), program)
        old_program = Program.objects.get(id=program_id)
        business_area = program.business_area
        finish_all_program_cycles = False

        # status update permissions if status is passed
        status_to_set = program_data.get("status")
        if status_to_set and program.status != status_to_set:
            if status_to_set == Program.ACTIVE:
                cls.has_permission(info, Permissions.PROGRAMME_ACTIVATE, business_area)
            elif status_to_set == Program.FINISHED:
                cls.has_permission(info, Permissions.PROGRAMME_FINISH, business_area)
                finish_all_program_cycles = True

        # permission if updating any other fields
        if [k for k, v in program_data.items() if k != "status"]:
            cls.has_permission(info, Permissions.PROGRAMME_UPDATE, business_area)
        cls.validate(
            program_data=program_data,
            program=program,
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
        )

        data_collecting_type_code = program_data.pop("data_collecting_type_code", None)
        if data_collecting_type_code and data_collecting_type_code != old_program.data_collecting_type.code:
            program.data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)

        program.full_clean()
        program.save()

        if finish_all_program_cycles:
            program.cycles.update(status=ProgramCycle.FINISHED)

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


class CopyProgram(CommonValidator, PermissionMutation, ValidationErrorMutationMixin):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CopyProgramInput(required=True)

    @classmethod
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CopyProgram":
        program_id = decode_id_string_required(program_data.pop("id"))
        business_area = Program.objects.get(id=program_id).business_area
        cls.has_permission(info, Permissions.PROGRAMME_DUPLICATE, business_area)

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
        )
        program = copy_program_object(program_id, program_data)

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
        program_id = get_program_id_from_headers(info)
        program = Program.objects.get(id=program_id)

        cls.has_permission(info, Permissions.PM_PROGRAMME_CYCLE_CREATE, program.business_area)

        cls.validate(
            start_date=program_cycle_data["start_date"],
            end_date=program_cycle_data.get("end_date"),
            name=program_cycle_data["name"],
            program=program,
            is_create_action=True,
        )

        ProgramCycle.objects.create(
            name=program_cycle_data["name"],
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
        input_fields = ["name", "start_date", "end_date"]
        for input_field in input_fields:
            if input_field in program_cycle_data:
                validation_kwargs_dict.update({input_field: program_cycle_data.get(input_field)})

        cls.validate(**validation_kwargs_dict)

        if start_date := program_cycle_data.get("start_date"):
            program_cycle.start_date = start_date

        if end_date := program_cycle_data.get("end_date"):
            program_cycle.end_date = end_date

        if name := program_cycle_data.get("name"):
            program_cycle.name = name

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

        cls.has_permission(info, Permissions.PM_PROGRAMME_CYCLE_REMOVE, program.business_area)

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
