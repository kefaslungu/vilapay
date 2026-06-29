"""
Group service — lifecycle management for ajo groups.

Responsibilities:
- Create groups (DRAFT state).
- Add members to slots.
- Activate a group: validate readiness, provision a Nomba VA, generate cycles.
- Cancel a group.

Activation is the key transition: it locks in membership, provisions the
shared virtual account, and pre-generates the full cycle schedule.
"""

import logging
from datetime import date

from django.db import transaction

from apps.groups.models import Group, GroupMembership
from services.exceptions import (
    GroupFullError,
    InvalidGroupStateError,
    PaymentProviderError,
    SlotTakenError,
)

logger = logging.getLogger(__name__)


# ── Group creation ────────────────────────────────────────────────────────────


def create_group(
    creator,
    name: str,
    slot_count: int,
    contribution_amount,
    frequency: str,
    start_date: date,
) -> Group:
    """
    Create a new ajo group in DRAFT state.
    The creator is automatically added as slot #1.
    """
    group = Group.objects.create(
        created_by=creator,
        name=name,
        slot_count=slot_count,
        contribution_amount=contribution_amount,
        frequency=frequency,
        start_date=start_date,
        status=Group.Status.DRAFT,
    )
    # Creator always gets slot #1
    GroupMembership.objects.create(
        group=group,
        user=creator,
        slot_number=1,
        status=GroupMembership.Status.ACTIVE,
    )
    logger.info("Group '%s' created by %s (id=%s)", name, creator.email, group.id)
    return group


# ── Membership ────────────────────────────────────────────────────────────────


def join_group(group: Group, user, slot_number: int | None = None) -> GroupMembership:
    """
    Add a user to a DRAFT group.

    If `slot_number` is None the next available slot is assigned automatically.
    Raises: GroupFullError, SlotTakenError, InvalidGroupStateError.
    """
    if group.status != Group.Status.DRAFT:
        raise InvalidGroupStateError(
            f"Cannot join '{group.name}' — group is {group.get_status_display()}."
        )

    taken = set(
        group.memberships.filter(status=GroupMembership.Status.ACTIVE).values_list(
            "slot_number", flat=True
        )
    )

    if slot_number is None:
        for n in range(1, group.slot_count + 1):
            if n not in taken:
                slot_number = n
                break
        else:
            raise GroupFullError(
                f"All {group.slot_count} slots in '{group.name}' are taken."
            )
    else:
        if not (1 <= slot_number <= group.slot_count):
            raise ValueError(f"slot_number must be between 1 and {group.slot_count}.")
        if slot_number in taken:
            raise SlotTakenError(
                f"Slot #{slot_number} in '{group.name}' is already taken."
            )

    membership = GroupMembership.objects.create(
        group=group,
        user=user,
        slot_number=slot_number,
        status=GroupMembership.Status.ACTIVE,
    )
    logger.info("%s joined group '%s' as slot #%d", user.email, group.name, slot_number)
    return membership


# ── Activation ────────────────────────────────────────────────────────────────


@transaction.atomic
def activate_group(group: Group) -> Group:
    """
    Activate a group:
    1. Validates all slots are filled.
    2. Provisions a Nomba virtual account for the group.
    3. Pre-generates the full cycle schedule.

    Raises InvalidGroupStateError, PaymentProviderError.
    """
    if group.status != Group.Status.DRAFT:
        raise InvalidGroupStateError(
            f"Only DRAFT groups can be activated (current: {group.get_status_display()})."
        )

    filled = group.memberships.filter(status=GroupMembership.Status.ACTIVE).count()
    if filled < group.slot_count:
        raise InvalidGroupStateError(
            f"'{group.name}' needs {group.slot_count} members; "
            f"only {filled} have joined."
        )

    _provision_group_va(group)

    group.status = Group.Status.ACTIVE
    group.current_cycle = 1
    group.save(
        update_fields=[
            "status",
            "current_cycle",
            "nomba_virtual_account_id",
            "nomba_virtual_account_number",
            "nomba_virtual_account_bank",
            "updated_at",
        ]
    )

    # Deferred import — cycles has no dependency on groups, safe to call here
    from services.cycles import generate_cycles

    generate_cycles(group)

    logger.info(
        "Group '%s' activated. VA: %s (%s)",
        group.name,
        group.nomba_virtual_account_number,
        group.nomba_virtual_account_bank,
    )
    return group


def _provision_group_va(group: Group) -> None:
    """
    Provision a Nomba virtual account for the group.
    Writes VA details directly onto the group instance (caller saves).
    Raises PaymentProviderError on failure.
    """
    from services.providers import get_payment_provider

    provider = get_payment_provider()
    account_ref = f"vilapay-grp-{group.id.hex}"
    account_name = f"{group.name[:40]} (Vilapay)"

    try:
        va = provider.create_virtual_account(account_ref, account_name)
    except Exception as exc:
        logger.exception("VA provisioning failed for group %s: %s", group.id, exc)
        raise PaymentProviderError(
            f"Could not provision virtual account: {exc}"
        ) from exc

    group.nomba_virtual_account_id = va.get("accountRef", "")
    group.nomba_virtual_account_number = va.get("bankAccountNumber", "")
    group.nomba_virtual_account_bank = va.get("bankName", "")


# ── Cancellation ──────────────────────────────────────────────────────────────


@transaction.atomic
def cancel_group(group: Group, reason: str = "") -> Group:
    """
    Cancel a DRAFT or ACTIVE group.
    COMPLETED groups cannot be cancelled.
    """
    if group.status == Group.Status.COMPLETED:
        raise InvalidGroupStateError("Completed groups cannot be cancelled.")
    if group.status == Group.Status.CANCELLED:
        raise InvalidGroupStateError("Group is already cancelled.")

    group.status = Group.Status.CANCELLED
    group.save(update_fields=["status", "updated_at"])
    logger.info("Group '%s' cancelled. Reason: %s", group.name, reason or "none given")
    return group
