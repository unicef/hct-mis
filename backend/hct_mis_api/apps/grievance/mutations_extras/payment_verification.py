from typing import Any

from django.utils import timezone

import graphene

from hct_mis_api.apps.payment.models import PaymentVerification

if TYPE_CHECKING:
    from hct_mis_api.apps.grievance.models import GrievanceTicket


class PaymentVerificationTicketExtras(graphene.InputObjectType):
    pass


def save_payment_verification_extras(grievance_ticket: GrievanceTicket, info: Any) -> None:
    payment_verification_details = grievance_ticket.payment_verification_ticket_details
    payment_verification = payment_verification_details.payment_verification
    if not (
        payment_verification_details.approve_status
        and payment_verification
        and not payment_verification_details.has_multiple_payment_verifications
    ):
        return
    # update PaymentVerification status
    if (
        payment_verification.payment_record
        and not payment_verification_details.new_status == PaymentVerification.STATUS_NOT_RECEIVED
    ):
        if payment_verification_details.new_received_amount >= payment_verification.payment_record.delivered_quantity:
            status = PaymentVerification.STATUS_RECEIVED
        else:
            status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    else:
        # set 'NOT_RECEIVED' status
        status = payment_verification_details.new_status

    payment_verification.status = status
    payment_verification.status_date = timezone.now()
    payment_verification.received_amount = payment_verification_details.new_received_amount

    payment_verification.save()
