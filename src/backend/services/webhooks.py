"""
Webhook dispatcher — the entry point for all inbound Nomba events.

Responsibilities:
- Verify the HMAC-SHA512 signature before processing anything.
- Route the event to the correct handler based on event type.
- Identify whether an incoming payment is for a group VA or a wallet VA.
- Keep handlers thin: they resolve the target object and delegate to
  contributions.py or wallets.py.

Member identification from a group VA payment:
  Because all members send to the same group VA, we cannot identify the
  sender from the VA number alone. We match on the Nomba transaction
  reference, which members include when making a transfer (the API returns
  this in the webhook payload as `merchantTxRef` or `narration`).

  For the hackathon/sandbox, if no reference is matched, we fall back to
  the first outstanding member — but this is clearly flagged in the code
  so it can be tightened before production.
"""

import json
import logging
import time

from services.exceptions import WebhookVerificationError
from services.metrics import webhook_processing_time

logger = logging.getLogger(__name__)


# ── Public entry point ────────────────────────────────────────────────────────


def handle_nomba_webhook(payload: bytes, signature: str) -> dict:
    """
    Verify and dispatch a Nomba webhook.

    Args:
        payload:   Raw request body bytes.
        signature: Value of the nomba-signature header.

    Returns:
        A dict with at least a 'status' key ('ok' | 'ignored' | 'error').

    Raises:
        WebhookVerificationError if the signature is invalid.
    """
    data = json.loads(payload)
    _verify_signature(data, signature)

    event_type = data.get("event") or data.get("eventType", "unknown")

    start = time.monotonic()
    try:
        return _dispatch(event_type, data)
    finally:
        webhook_processing_time.labels(event_type=event_type).observe(
            time.monotonic() - start
        )


# ── Signature verification ────────────────────────────────────────────────────


def _verify_signature(data: dict, signature: str) -> None:
    from services.providers import get_payment_provider

    provider = get_payment_provider()
    if not provider.verify_webhook(data, signature):
        raise WebhookVerificationError("Webhook signature verification failed.")


# ── Event dispatcher ──────────────────────────────────────────────────────────


def _dispatch(event_type: str, data: dict) -> dict:
    HANDLERS = {
        "virtualaccount.credit": _handle_incoming_payment,
        "transfer.credit": _handle_incoming_payment,
        "transfer.debit": _handle_outgoing_payment,
        "directdebit.charge.success": _handle_direct_debit_success,
        "directdebit.charge.failed": _handle_direct_debit_failure,
    }
    handler = HANDLERS.get(event_type)
    if handler is None:
        logger.info("Unhandled webhook event type: %s", event_type)
        return {"status": "ignored", "event": event_type}
    return handler(data)


# ── Handlers ──────────────────────────────────────────────────────────────────


def _handle_incoming_payment(data: dict) -> dict:
    """
    Money arrived at one of our virtual accounts.
    Route to group contribution or wallet deposit based on the VA number.
    """
    from apps.groups.models import Group, GroupCycle
    from apps.wallets.models import SaveAheadWallet
    from services import contributions as contribution_svc
    from services import wallets as wallet_svc

    account_number = data.get("accountNumber") or data.get(
        "destinationAccountNumber", ""
    )
    amount = data.get("amount", 0)
    transaction_id = data.get("transactionId", "")
    reference = data.get("merchantTxRef") or data.get("reference", "")

    # ── Try group VA ──────────────────────────────────────────────────────────
    try:
        group = Group.objects.get(
            nomba_virtual_account_number=account_number,
            status=Group.Status.ACTIVE,
        )
        cycle = GroupCycle.objects.filter(
            group=group,
            status=GroupCycle.Status.COLLECTING,
        ).first()

        if cycle is None:
            logger.error(
                "Payment to group VA but no collecting cycle: group %s", group.id
            )
            return {"status": "error", "reason": "no_active_cycle"}

        membership = _resolve_member(cycle, reference, data)
        if membership is None:
            logger.warning(
                "Cannot identify member for payment to group '%s' VA (ref: %s)",
                group.name,
                reference,
            )
            return {"status": "error", "reason": "member_unidentifiable"}

        contribution_svc.record_contribution(
            cycle=cycle,
            membership=membership,
            amount=amount,
            payment_method="va_transfer",
            nomba_transaction_id=transaction_id,
            nomba_reference=reference,
        )
        return {"status": "ok", "type": "group_contribution"}

    except Group.DoesNotExist:
        pass

    # ── Try wallet VA ─────────────────────────────────────────────────────────
    try:
        wallet = SaveAheadWallet.objects.select_related("membership__user").get(
            nomba_virtual_account_number=account_number
        )
        wallet_svc.deposit(wallet, amount, nomba_transaction_ref=reference)
        return {"status": "ok", "type": "wallet_deposit"}

    except SaveAheadWallet.DoesNotExist:
        pass

    logger.warning("Incoming payment for unknown VA: %s", account_number)
    return {"status": "ignored", "reason": "unknown_va"}


def _handle_outgoing_payment(data: dict) -> dict:
    """
    Confirmation that a transfer we initiated (payout) was debited.
    Currently informational — the payout record is already updated
    synchronously in payouts.py. Log and acknowledge.
    """
    reference = data.get("merchantTxRef") or data.get("reference", "")
    logger.info("Outgoing transfer confirmed by webhook: ref=%s", reference)
    return {"status": "ok", "type": "outgoing_confirmed"}


def _handle_direct_debit_success(data: dict) -> dict:
    """
    Nomba successfully charged a member via direct debit mandate.
    Record as a completed contribution.
    """
    from apps.payments.models import DirectDebitMandate
    from services import contributions as contribution_svc

    mandate_id = data.get("mandateId", "")
    amount = data.get("amount", 0)
    transaction_id = data.get("transactionId", "")
    reference = data.get("reference", "")

    try:
        mandate = DirectDebitMandate.objects.select_related(
            "membership__group", "membership__user"
        ).get(nomba_mandate_id=mandate_id)
    except DirectDebitMandate.DoesNotExist:
        logger.error("Direct debit success for unknown mandate: %s", mandate_id)
        return {"status": "error", "reason": "unknown_mandate"}

    from apps.groups.models import GroupCycle

    cycle = GroupCycle.objects.filter(
        group=mandate.membership.group,
        status=GroupCycle.Status.COLLECTING,
    ).first()

    if cycle is None:
        logger.warning(
            "Direct debit success but no collecting cycle for mandate %s", mandate_id
        )
        return {"status": "ignored", "reason": "no_active_cycle"}

    contribution_svc.record_contribution(
        cycle=cycle,
        membership=mandate.membership,
        amount=amount,
        payment_method="direct_debit",
        nomba_transaction_id=transaction_id,
        nomba_reference=reference,
    )
    return {"status": "ok", "type": "direct_debit_contribution"}


def _handle_direct_debit_failure(data: dict) -> dict:
    """
    A direct debit charge failed. Log and notify the member (via Celery task).
    """
    from apps.payments.models import DirectDebitMandate
    from services.contributions import record_failed_contribution

    mandate_id = data.get("mandateId", "")
    reason = data.get("reason") or data.get("description", "unknown")

    try:
        mandate = DirectDebitMandate.objects.select_related("membership__user").get(
            nomba_mandate_id=mandate_id
        )
        record_failed_contribution(mandate.membership, reason=reason)
    except DirectDebitMandate.DoesNotExist:
        logger.error("Direct debit failure for unknown mandate: %s", mandate_id)

    return {"status": "ok", "type": "direct_debit_failure_logged"}


# ── Member resolution ─────────────────────────────────────────────────────────


def _resolve_member(cycle, reference: str, data: dict):
    """
    Identify which member made a payment to the shared group VA.

    Strategy (in order):
    1. Match `reference` against a pending Contribution record whose
       nomba_reference was set when the member was given a payment link.
    2. Fall back to the first outstanding member.
       ⚠ This fallback is acceptable in the sandbox but must be replaced
       by a proper reference-based flow (or individual VAs per member)
       before production at scale.
    """
    from apps.payments.models import Contribution
    from services.contributions import get_outstanding_members

    # Strategy 1: match by reference
    if reference:
        pending = (
            Contribution.objects.filter(
                cycle=cycle,
                nomba_reference=reference,
                status=Contribution.Status.PENDING,
            )
            .select_related("member")
            .first()
        )
        if pending:
            return pending.member

    # Strategy 2: first outstanding member (sandbox fallback)
    outstanding = get_outstanding_members(cycle)
    first = outstanding.first()
    if first:
        logger.warning(
            "Member resolved by fallback (first outstanding) for cycle #%d "
            "— production should use per-member references.",
            cycle.cycle_number,
        )
    return first
