import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="payments.check_direct_debit_statuses")
def check_direct_debit_statuses():
    """
    Poll Nomba for the status of PENDING direct debit mandates.
    Handles the case where Nomba's activation webhook was missed.
    Runs every hour via Celery beat.
    """
    from apps.payments.models import DirectDebitMandate

    pending = DirectDebitMandate.objects.filter(
        status=DirectDebitMandate.Status.PENDING
    ).select_related("membership__user")

    for mandate in pending:
        try:
            # Nomba doesn't have a mandate status endpoint yet in sandbox —
            # this is a placeholder for when the live API exposes it.
            # result = provider.get_mandate_status(mandate.nomba_mandate_id)
            # if result.get("status") == "active":
            #     mandate.status = DirectDebitMandate.Status.ACTIVE
            #     mandate.save(update_fields=["status", "updated_at"])
            pass
        except Exception:
            logger.exception(
                "Error checking mandate status for %s", mandate.nomba_mandate_id
            )
