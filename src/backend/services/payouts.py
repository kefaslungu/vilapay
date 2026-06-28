"""
Payout service — disbursing the pot to the cycle winner.

Responsibilities:
- Initiate a bank transfer to the cycle recipient via the payment provider.
- Record the transfer in the ledger.
- On success, advance the group to the next cycle.
- On failure, mark the payout as FAILED for retry.

Called exclusively from the async Celery task (apps/payouts/tasks.py),
never synchronously from a request handler.
"""

import logging
import time

from django.db import transaction
from django.utils import timezone

from apps.groups.models import GroupCycle
from apps.payouts.models import Payout
from services.exceptions import InvalidGroupStateError, PaymentProviderError
from services.ledger import record_entry
from services.metrics import payout_duration

logger = logging.getLogger(__name__)


@transaction.atomic
def initiate_payout(cycle: GroupCycle) -> Payout:
    """
    Transfer the collected pot to the cycle's recipient bank account.

    Flow:
    1. Validate cycle status and recipient bank account.
    2. Create a Payout record in PROCESSING state.
    3. Call the payment provider.
    4. On success: update ledger, advance cycle.
    5. On failure: mark payout FAILED (task will retry).

    Raises: InvalidGroupStateError, PaymentProviderError.
    """
    # Re-fetch inside the transaction to guard against stale data
    cycle = GroupCycle.objects.select_related("group", "recipient__user").get(
        pk=cycle.pk
    )

    if cycle.status != GroupCycle.Status.PAYOUT_PENDING:
        raise InvalidGroupStateError(
            f"Cycle #{cycle.cycle_number} is not in PAYOUT_PENDING "
            f"(current: {cycle.get_status_display()})."
        )

    recipient = cycle.recipient.user
    bank_account = recipient.bank_accounts.filter(is_default=True).first()
    if bank_account is None:
        raise InvalidGroupStateError(
            f"Recipient {recipient.email} has no default bank account. "
            "They must add one before a payout can proceed."
        )

    payout = Payout.objects.create(
        cycle=cycle,
        recipient=recipient,
        bank_account=bank_account,
        amount=cycle.total_collected,
        status=Payout.Status.PROCESSING,
        initiated_at=timezone.now(),
    )

    reference = f"vp-payout-{payout.id.hex[:12]}"
    start = time.monotonic()

    try:
        from services.providers import get_payment_provider

        provider = get_payment_provider()

        result = provider.transfer_to_bank(
            bank_code=bank_account.bank_code,
            account_number=bank_account.account_number,
            amount=payout.amount,
            narration=(
                f"Vilapay ajo payout — {cycle.group.name} cycle #{cycle.cycle_number}"
            ),
            reference=reference,
        )

        payout.nomba_transfer_id = result.get("id", "")
        payout.nomba_reference = reference
        payout.status = Payout.Status.COMPLETED
        payout.completed_at = timezone.now()
        payout.save(
            update_fields=[
                "nomba_transfer_id",
                "nomba_reference",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        record_entry(
            entry_type="payout",
            amount=payout.amount,
            group=cycle.group,
            nomba_transaction_ref=reference,
            description=(
                f"Payout to {recipient.email} "
                f"— {cycle.group.name} cycle #{cycle.cycle_number}"
            ),
        )

        # Advance to next cycle (or close the group if this was the last)
        from services.cycles import advance_cycle

        advance_cycle(cycle.group)

        logger.info(
            "Payout completed: ₦%s to %s for '%s' cycle #%d (ref: %s)",
            payout.amount,
            recipient.email,
            cycle.group.name,
            cycle.cycle_number,
            reference,
        )

    except Exception as exc:
        payout.status = Payout.Status.FAILED
        payout.failure_reason = str(exc)
        payout.save(update_fields=["status", "failure_reason", "updated_at"])
        logger.exception(
            "Payout failed for cycle #%d of '%s': %s",
            cycle.cycle_number,
            cycle.group.name,
            exc,
        )
        raise PaymentProviderError(f"Payout failed: {exc}") from exc

    finally:
        payout_duration.observe(time.monotonic() - start)

    return payout
