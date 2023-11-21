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
)
from hct_mis_api.apps.core.validators import (
    CommonValidator,
    DataCollectingTypeValidator,
)
from hct_mis_api.apps.program.celery_tasks import copy_program_task
from hct_mis_api.apps.program.inputs import (
    CopyProgramInput,
    CreateProgramInput,
    UpdateProgramInput,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.program.schema import ProgramNode
from hct_mis_api.apps.program.utils import copy_program_object
from hct_mis_api.apps.program.validators import (
    ProgramDeletionValidator,
    ProgramValidator,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin


class CreateProgram(CommonValidator, DataCollectingTypeValidator, PermissionMutation, ValidationErrorMutationMixin):
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

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
            data_collecting_type=data_collecting_type,
            business_area=business_area,
        )

        program = Program(
            **program_data, status=Program.DRAFT, business_area=business_area, data_collecting_type=data_collecting_type
        )
        program.full_clean()
        program.save()
        ProgramCycle.objects.create(
            program=program,
            start_date=program.start_date,
            end_date=program.end_date,
            status=ProgramCycle.ACTIVE,
        )
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)
        return CreateProgram(program=program)


class UpdateProgram(ProgramValidator, DataCollectingTypeValidator, PermissionMutation, ValidationErrorMutationMixin):
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

        # status update permissions if status is passed
        status_to_set = program_data.get("status")
        if status_to_set and program.status != status_to_set:
            if status_to_set == Program.ACTIVE:
                cls.has_permission(info, Permissions.PROGRAMME_ACTIVATE, business_area)
            elif status_to_set == Program.FINISHED:
                cls.has_permission(info, Permissions.PROGRAMME_FINISH, business_area)

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


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
    copy_program = CopyProgram.Field()
