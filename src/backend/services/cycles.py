"""
Cycle service — schedule generation and lifecycle transitions.

Responsibilities:
- Pre-generate all N cycles when a group activates.
- Calculate per-cycle date ranges from the group's start date and frequency.
- Advance the group to the next cycle after a payout completes.

This module is intentionally thin: it only knows about Group and
GroupCycle models and has no knowledge of payments or providers.
"""
import calendar
import logging
from datetime import date, timedelta

from django.db import transaction

from apps.groups.models import Group, GroupCycle, GroupMembership
from services.exceptions import InvalidGroupStateError

logger = logging.getLogger(__name__)


# ── Date math ─────────────────────────────────────────────────────────────────

def _add_months(d: date, months: int) -> date:
    """
    Add `months` to date `d`, clamping to the last valid day of the
    resulting month (e.g. Jan 31 + 1 month = Feb 28/29).
    """
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _cycle_date_range(start_date: date, cycle_index: int, frequency: str):
    """
    Return (cycle_start, cycle_end, payout_date) for a zero-indexed cycle.

    Payout is always on the last day of the cycle window so members have
    the full period to contribute before the pot is disbursed.
    """
    if frequency == Group.Frequency.WEEKLY:
        cycle_start = start_date + timedelta(weeks=cycle_index)
        cycle_end = cycle_start + timedelta(days=6)
    elif frequency == Group.Frequency.BIWEEKLY:
        cycle_start = start_date + timedelta(weeks=2 * cycle_index)
        cycle_end = cycle_start + timedelta(days=13)
    else:  # monthly (default)
        cycle_start = _add_months(start_date, cycle_index)
        cycle_end = _add_months(start_date, cycle_index + 1) - timedelta(days=1)

    return cycle_start, cycle_end, cycle_end  # payout_date == cycle_end


# ── Cycle generation ──────────────────────────────────────────────────────────

@transaction.atomic
def generate_cycles(group: Group) -> list[GroupCycle]:
    """
    Pre-generate all N cycles for a group (called once on activation).

    Slot order determines who receives the pot each cycle:
    slot #1 gets cycle 1, slot #2 gets cycle 2, etc.
    Cycle 1 is immediately set to COLLECTING; the rest start as PENDING.
    """
    memberships = list(
        group.memberships
        .filter(status=GroupMembership.Status.ACTIVE)
        .order_by("slot_number")
    )

    cycles_to_create = []
    for i, membership in enumerate(memberships):
        cycle_number = i + 1
        start, end, payout = _cycle_date_range(group.start_date, i, group.frequency)
        status = (
            GroupCycle.Status.COLLECTING if cycle_number == 1 else GroupCycle.Status.PENDING
        )
        cycles_to_create.append(
            GroupCycle(
                group=group,
                cycle_number=cycle_number,
                recipient=membership,
                start_date=start,
                end_date=end,
                payout_date=payout,
                status=status,
            )
        )

    GroupCycle.objects.bulk_create(cycles_to_create)
    logger.info("Generated %d cycles for group %s", len(cycles_to_create), group.id)
    return cycles_to_create


# ── Cycle queries ─────────────────────────────────────────────────────────────

def get_current_cycle(group: Group) -> GroupCycle | None:
    """Return the group's current cycle, with recipient user pre-fetched."""
    return (
        GroupCycle.objects
        .filter(group=group, cycle_number=group.current_cycle)
        .select_related("recipient__user")
        .first()
    )


# ── Cycle advancement ─────────────────────────────────────────────────────────

@transaction.atomic
def advance_cycle(group: Group) -> GroupCycle | None:
    """
    Close the current cycle and activate the next one.

    Returns the new current GroupCycle, or None if all cycles are now
    complete (in which case the group is also marked COMPLETED).

    Raises InvalidGroupStateError if called with no active cycle.
    """
    current = get_current_cycle(group)
    if current is None:
        raise InvalidGroupStateError(
            f"No cycle #{group.current_cycle} found for group {group.id}."
        )

    current.status = GroupCycle.Status.COMPLETED
    current.save(update_fields=["status", "updated_at"])

    next_number = group.current_cycle + 1
    try:
        next_cycle = GroupCycle.objects.get(group=group, cycle_number=next_number)
        next_cycle.status = GroupCycle.Status.COLLECTING
        next_cycle.save(update_fields=["status", "updated_at"])
        group.current_cycle = next_number
        group.save(update_fields=["current_cycle", "updated_at"])
        logger.info("Group %s advanced to cycle #%d", group.id, next_number)
        return next_cycle
    except GroupCycle.DoesNotExist:
        # Final cycle completed — close the group
        group.status = Group.Status.COMPLETED
        group.save(update_fields=["status", "updated_at"])
        logger.info("Group %s completed all cycles.", group.id)
        return None
