"""
Save-Ahead Wallet service.

Responsibilities:
- Create a wallet (and optionally provision a dedicated Nomba VA) for a
  group membership slot.
- Accept deposits into the wallet (triggered by webhook).
- Sweep wallet balance toward a contribution when contribution day arrives.

The wallet is a convenience layer on top of the contribution system:
sweeping a wallet simply calls record_contribution with payment_method='save_ahead'.
"""

import logging

from django.db import transaction
from django.db.models import F

from apps.wallets.models import SaveAheadWallet
from services.exceptions import WalletLimitExceededError
from services.ledger import record_entry

logger = logging.getLogger(__name__)


# ── Wallet creation ───────────────────────────────────────────────────────────


_TIER_WALLET_LIMITS = {
    "free": 1,
    "individual_pro": 5,
    "collector_pro": None,  # unlimited
}


def create_wallet(membership) -> SaveAheadWallet:
    """
    Create a Save-Ahead wallet for a group membership slot and attempt to
    provision a dedicated Nomba VA so the member can deposit directly.

    VA provisioning failure is non-fatal: the wallet is still created and
    the member can pay directly to the group VA instead.

    Raises WalletLimitExceededError if the user has reached their tier limit.
    """
    user = membership.user
    limit = _TIER_WALLET_LIMITS.get(user.tier)
    if limit is not None:
        current_count = user.save_ahead_wallets.count()
        if current_count >= limit:
            raise WalletLimitExceededError(
                f"Your {user.get_tier_display()} plan allows up to {limit} "
                f"Save-Ahead wallet{'s' if limit != 1 else ''}. "
                "Upgrade your plan to join more groups."
            )

    wallet = SaveAheadWallet.objects.create(
        user=membership.user,
        membership=membership,
    )
    _try_provision_wallet_va(wallet)
    logger.info(
        "Save-Ahead wallet created for %s in group '%s'",
        membership.user.email,
        membership.group.name,
    )
    return wallet


def _try_provision_wallet_va(wallet: SaveAheadWallet) -> None:
    """Attempt VA provisioning; log and continue on failure."""
    try:
        from services.providers import get_payment_provider

        provider = get_payment_provider()
        account_ref = f"vilapay-wlt-{wallet.id.hex}"
        account_name = f"{wallet.user.full_name[:40]} (Save-Ahead)"
        va = provider.create_virtual_account(account_ref, account_name)
        wallet.nomba_virtual_account_id = va.get("accountRef", "")
        wallet.nomba_virtual_account_number = va.get("bankAccountNumber", "")
        wallet.nomba_virtual_account_bank = va.get("bankName", "")
        wallet.save(
            update_fields=[
                "nomba_virtual_account_id",
                "nomba_virtual_account_number",
                "nomba_virtual_account_bank",
            ]
        )
    except Exception as exc:
        logger.warning(
            "Could not provision VA for wallet %s (member %s): %s — "
            "wallet created without dedicated VA.",
            wallet.id,
            wallet.user.email,
            exc,
        )


# ── Deposits ──────────────────────────────────────────────────────────────────


@transaction.atomic
def deposit(
    wallet: SaveAheadWallet,
    amount,
    nomba_transaction_ref: str = "",
) -> None:
    """
    Credit the wallet balance and record the movement in the ledger.
    Called by the webhook handler when money arrives at the wallet VA.
    """
    SaveAheadWallet.objects.filter(pk=wallet.pk).update(balance=F("balance") + amount)
    wallet.refresh_from_db(fields=["balance"])

    record_entry(
        entry_type="deposit",
        amount=amount,
        wallet=wallet,
        membership=wallet.membership,
        nomba_transaction_ref=nomba_transaction_ref,
        description="Save-Ahead deposit",
    )
    logger.info(
        "Wallet deposit: ₦%s for %s (new balance: ₦%s)",
        amount,
        wallet.user.email,
        wallet.balance,
    )


# ── Sweep ─────────────────────────────────────────────────────────────────────


@transaction.atomic
def sweep_for_contribution(wallet: SaveAheadWallet, cycle) -> bool:
    """
    If the wallet has enough balance, use it to pay the member's
    contribution for the given cycle.

    Returns True if the sweep succeeded, False if balance was insufficient.
    Called by the Celery sweep task on contribution day.
    """
    from services.contributions import AlreadyPaidError, record_contribution

    wallet.refresh_from_db(fields=["balance"])
    required = cycle.group.contribution_amount

    if wallet.balance < required:
        logger.info(
            "Wallet balance ₦%s < required ₦%s — skipping sweep for %s",
            wallet.balance,
            required,
            wallet.user.email,
        )
        return False

    # Deduct from wallet first (inside the same transaction as record_contribution)
    SaveAheadWallet.objects.filter(pk=wallet.pk).update(balance=F("balance") - required)
    record_entry(
        entry_type="withdrawal",
        amount=required,
        wallet=wallet,
        membership=wallet.membership,
        description=(
            f"Swept toward '{cycle.group.name}' "
            f"cycle #{cycle.cycle_number} contribution"
        ),
    )

    try:
        record_contribution(
            cycle=cycle,
            membership=wallet.membership,
            amount=required,
            payment_method="save_ahead",
        )
    except AlreadyPaidError:
        # Race condition: already paid elsewhere — refund the deduction
        SaveAheadWallet.objects.filter(pk=wallet.pk).update(
            balance=F("balance") + required
        )
        logger.info(
            "Sweep aborted — %s already paid for cycle #%d.",
            wallet.user.email,
            cycle.cycle_number,
        )
        return False

    logger.info(
        "Wallet sweep succeeded: ₦%s for %s — '%s' cycle #%d",
        required,
        wallet.user.email,
        cycle.group.name,
        cycle.cycle_number,
    )
    return True
