import logging
from typing import TYPE_CHECKING, Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType

logger = logging.getLogger(__name__)


class ProgramValidator(BaseValidator):
    @classmethod
    def validate_status_change(cls, *args: Any, **kwargs: Any) -> Optional[None]:
        status_to_set = kwargs.get("program_data").get("status")
        program = kwargs.get("program")
        current_status = program.status
        if status_to_set is None or status_to_set == current_status:
            return None
        if status_to_set not in dict(Program.STATUS_CHOICE):
            logger.error(f"Wrong status: {status_to_set}")
            raise ValidationError("Wrong status")
        if current_status == Program.DRAFT and status_to_set != Program.ACTIVE:
            logger.error("Draft status can only be changed to Active")
            raise ValidationError("Draft status can only be changed to Active")
        elif current_status == Program.ACTIVE and status_to_set != Program.FINISHED:
            logger.error("Active status can only be changed to Finished")
            raise ValidationError("Active status can only be changed to Finished")
        elif current_status == Program.FINISHED and status_to_set != Program.ACTIVE:
            logger.error("Finished status can only be changed to Active")
            raise ValidationError("Finished status can only be changed to Active")


class ProgramDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.DRAFT:
            logger.error("Only Draft Program can be deleted.")
            raise ValidationError("Only Draft Program can be deleted.")


class CashPlanValidator(BaseValidator):
    pass


def validate_data_collecting_type(
    program_data_collecting_type: "DataCollectingType",
    data_collecting_type: "DataCollectingType",
    business_area: "BusinessArea",
) -> None:
    if business_area not in data_collecting_type.limit_to.all():
        raise ValidationError("This Data Collection Type is not assigned to the Program's Business Area")

    if (
        data_collecting_type != program_data_collecting_type
    ) and data_collecting_type not in program_data_collecting_type.compatible_types.all():
        raise ValidationError("The Data Collection Type must match or be compatible with the original Programme.")
