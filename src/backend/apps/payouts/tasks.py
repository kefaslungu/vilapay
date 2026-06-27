import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=120,  # 2 minutes between retries
    name="payouts.initiate_payout",
)
def initiate_payout_task(self, cycle_id: str):
    """
    Async task: initiate the payout for a fully-paid cycle.

    Retries up to 5 times with 2-minute delays so transient Nomba
    API errors are recovered automatically.
    """
    from apps.groups.models import GroupCycle
    from services.exceptions import PaymentProviderError
    from services.payouts import initiate_payout

    try:
        cycle = (
            GroupCycle.objects
            .select_related("group", "recipient__user")
            .get(id=cycle_id)
        )
        initiate_payout(cycle)

    except GroupCycle.DoesNotExist:
        logger.error("initiate_payout_task: cycle %s not found", cycle_id)

    except PaymentProviderError as exc:
        logger.warning(
            "Payout failed for cycle %s (attempt %d/%d): %s",
            cycle_id, self.request.retries + 1, self.max_retries, exc,
        )
        raise self.retry(exc=exc) from exc

    except Exception as exc:
        logger.exception("Unexpected error in payout task for cycle %s", cycle_id)
        raise self.retry(exc=exc) from exc
