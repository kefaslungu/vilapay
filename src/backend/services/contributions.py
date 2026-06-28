"""
Contribution service — recording payments and checking cycle completion.

Responsibilities:
- Record a confirmed contribution (from webhook or direct debit).
- Update the group ledger and cycle total.
- Detect when all members have paid and dispatch an async payout task.
- Query outstanding members for reminders and wallet sweeps.

When a cycle becomes fully paid, this service dispatches a Celery task
(instead of calling payouts.py directly) to keep the two domains decoupled
and to make payout retries easy.
"""

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.groups.models import GroupCycle, GroupMembership
from apps.payments.models import Contribution
from services.exceptions import AlreadyPaidError, InvalidGroupStateError
from services.ledger import record_entry
from services.metrics import payment_failure, payment_success

logger = logging.getLogger(__name__)


# ── Recording contributions ───────────────────────────────────────────────────


@transaction.atomic
def record_contribution(
    cycle: GroupCycle,
    membership: GroupMembership,
    amount,
    payment_method: str,
    nomba_transaction_id: str = "",
    nomba_reference: str = "",
) -> Contribution:
    """
    Persist a confirmed contribution, update the ledger, and check if the
    cycle is now fully paid.

    - Uses select_for_update on the membership row to prevent double-payment
      in concurrent requests.
    - Dispatches an async payout task if the cycle becomes fully paid.

    Raises: AlreadyPaidError, InvalidGroupStateError.
    """
    # Lock the membership row for this transaction
    membership = GroupMembership.objects.select_for_update().get(pk=membership.pk)

    if cycle.status != GroupCycle.Status.COLLECTING:
        raise InvalidGroupStateError(
            f"Cycle #{cycle.cycle_number} is not accepting contributions "
            f"(status: {cycle.get_status_display()})."
        )

    already_paid = Contribution.objects.filter(
        cycle=cycle,
        member=membership,
        status=Contribution.Status.COMPLETED,
    ).exists()
    if already_paid:
        raise AlreadyPaidError(
            f"{membership.user.email} has already paid for cycle #{cycle.cycle_number}."
        )

    contribution = Contribution.objects.create(
        cycle=cycle,
        member=membership,
        amount=amount,
        status=Contribution.Status.COMPLETED,
        payment_method=payment_method,
        nomba_transaction_id=nomba_transaction_id,
        nomba_reference=nomba_reference,
        paid_at=timezone.now(),
    )

    # Atomic increment — safe under concurrent updates
    GroupCycle.objects.filter(pk=cycle.pk).update(
        total_collected=F("total_collected") + amount
    )
    cycle.refresh_from_db(fields=["total_collected"])

    record_entry(
        entry_type="deposit",
        amount=amount,
        group=cycle.group,
        membership=membership,
        nomba_transaction_ref=nomba_reference,
        description=(
            f"Contribution from {membership.user.email} "
            f"— {cycle.group.name} cycle #{cycle.cycle_number}"
        ),
    )

    payment_success.labels(
        payment_method=payment_method,
        tier=membership.user.tier,
    ).inc()

    logger.info(
        "Contribution recorded: %s paid ₦%s for '%s' cycle #%d",
        membership.user.email,
        amount,
        cycle.group.name,
        cycle.cycle_number,
    )

    if is_cycle_fully_paid(cycle):
        _trigger_payout(cycle)

    return contribution


def record_failed_contribution(membership: GroupMembership, reason: str) -> None:
    """Increment the failure metric. Called by the direct debit task on charge failure."""
    payment_failure.labels(reason=reason).inc()
    logger.warning("Contribution failed for %s: %s", membership.user.email, reason)


# ── Cycle completion check ────────────────────────────────────────────────────


def is_cycle_fully_paid(cycle: GroupCycle) -> bool:
    """True when every active member has a completed contribution this cycle."""
    active_count = cycle.group.memberships.filter(
        status=GroupMembership.Status.ACTIVE
    ).count()
    paid_count = cycle.contributions.filter(
        status=Contribution.Status.COMPLETED
    ).count()
    return paid_count >= active_count


def get_outstanding_members(cycle: GroupCycle):
    """
    Return active memberships that have NOT yet paid for this cycle.
    Used by reminders and wallet-sweep tasks.
    """
    paid_ids = cycle.contributions.filter(
        status=Contribution.Status.COMPLETED
    ).values_list("member_id", flat=True)
    return (
        cycle.group.memberships.filter(status=GroupMembership.Status.ACTIVE)
        .exclude(id__in=paid_ids)
        .select_related("user")
    )


# ── Internal helpers ──────────────────────────────────────────────────────────


def _trigger_payout(cycle: GroupCycle) -> None:
    """
    Mark cycle as PAYOUT_PENDING and dispatch the async payout task.
    Deferred import of the task breaks the contributions ↔ payouts cycle.
    """
    GroupCycle.objects.filter(pk=cycle.pk).update(
        status=GroupCycle.Status.PAYOUT_PENDING
    )
    logger.info(
        "Cycle #%d of '%s' fully paid — dispatching payout task.",
        cycle.cycle_number,
        cycle.group.name,
    )
    # Import here to avoid circular: contributions → tasks → payouts → (nothing)
    from apps.payouts.tasks import initiate_payout_task

    initiate_payout_task.delay(str(cycle.id))
