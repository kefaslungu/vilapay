import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="groups.send_contribution_reminders")
def send_contribution_reminders():
    """
    Notify members who haven't paid for cycles ending within 3 days.
    Runs daily via Celery beat.

    Actual notification dispatch (email / push) is handled by the
    notifications app — this task just identifies who to notify.
    """
    from apps.groups.models import GroupCycle
    from services.contributions import get_outstanding_members

    warning_date = timezone.now().date() + timedelta(days=3)

    due_cycles = GroupCycle.objects.filter(
        status=GroupCycle.Status.COLLECTING,
        end_date__lte=warning_date,
    ).select_related("group")

    for cycle in due_cycles:
        outstanding = get_outstanding_members(cycle)
        for membership in outstanding:
            logger.info(
                "Reminder needed: %s owes ₦%s for '%s' cycle #%d (due %s)",
                membership.user.email,
                cycle.group.contribution_amount,
                cycle.group.name,
                cycle.cycle_number,
                cycle.end_date,
            )
            # TODO: dispatch notifications.tasks.send_reminder(membership.user.id, cycle.id)


@shared_task(name="groups.sweep_wallets_for_contributions")
def sweep_wallets_for_contributions():
    """
    On contribution day: automatically use save-ahead wallet balances to
    pay any outstanding contributions.
    Runs daily via Celery beat (after business hours so members have had
    time to top up their wallets).
    """
    from apps.groups.models import GroupCycle
    from apps.wallets.models import SaveAheadWallet
    from services.contributions import get_outstanding_members
    from services.wallets import sweep_for_contribution

    today = timezone.now().date()

    due_cycles = GroupCycle.objects.filter(
        status=GroupCycle.Status.COLLECTING,
        end_date__lte=today,
    ).select_related("group")

    for cycle in due_cycles:
        for membership in get_outstanding_members(cycle):
            try:
                wallet = SaveAheadWallet.objects.get(membership=membership)
                swept = sweep_for_contribution(wallet, cycle)
                if not swept:
                    logger.info(
                        "Insufficient wallet balance for %s — '%s' cycle #%d",
                        membership.user.email, cycle.group.name, cycle.cycle_number,
                    )
            except SaveAheadWallet.DoesNotExist:
                pass  # Member has no wallet — they must pay manually
            except Exception:
                logger.exception(
                    "Error sweeping wallet for %s in cycle %s",
                    membership.user.email, cycle.id,
                )
