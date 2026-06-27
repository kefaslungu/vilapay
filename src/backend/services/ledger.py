"""
Ledger service — immutable audit trail for all fund movements.

Every debit and credit across groups and save-ahead wallets goes through
here. The running balance is stored on each entry so any point-in-time
balance can be read without summing the full history.

Rules:
- A ledger entry belongs to a group, a wallet, or both (for sweeps).
- Balance is tracked separately per group and per wallet.
- This module has no imports from other services — it is the foundation.
"""
from decimal import Decimal


def record_entry(
    entry_type: str,
    amount,
    *,
    group=None,
    wallet=None,
    membership=None,
    nomba_transaction_ref: str = "",
    description: str = "",
):
    """
    Create an immutable ledger entry.

    Args:
        entry_type: One of LedgerEntry.EntryType values ('deposit',
                    'withdrawal', 'payout', 'refund').
        amount:     Monetary amount (Decimal or numeric string).
        group:      Group instance this entry belongs to (optional).
        wallet:     SaveAheadWallet instance (optional).
        membership: GroupMembership that triggered the entry (optional).
        nomba_transaction_ref: External transaction reference.
        description: Human-readable note for the audit trail.

    Either `group` or `wallet` must be provided.
    """
    from apps.wallets.models import LedgerEntry  # deferred — avoids app-loading issues

    if group is None and wallet is None:
        raise ValueError("record_entry requires either group or wallet.")

    # Compute running balance scoped to group or wallet
    qs = LedgerEntry.objects.all()
    if group is not None:
        qs = qs.filter(group=group)
    else:
        qs = qs.filter(wallet=wallet)

    last_entry = qs.order_by("-created_at").first()
    previous_balance = last_entry.balance_after if last_entry else Decimal("0.00")
    amount = Decimal(str(amount))

    CREDIT_TYPES = {LedgerEntry.EntryType.DEPOSIT, LedgerEntry.EntryType.REFUND}
    if entry_type in CREDIT_TYPES:
        balance_after = previous_balance + amount
    else:
        balance_after = previous_balance - amount

    return LedgerEntry.objects.create(
        group=group,
        wallet=wallet,
        membership=membership,
        entry_type=entry_type,
        amount=amount,
        balance_after=balance_after,
        nomba_transaction_ref=nomba_transaction_ref,
        description=description,
    )


def get_group_balance(group) -> Decimal:
    """Current ledger balance for a group."""
    from apps.wallets.models import LedgerEntry

    last = LedgerEntry.objects.filter(group=group).order_by("-created_at").first()
    return last.balance_after if last else Decimal("0.00")


def get_wallet_balance(wallet) -> Decimal:
    """Current ledger balance for a save-ahead wallet."""
    from apps.wallets.models import LedgerEntry

    last = LedgerEntry.objects.filter(wallet=wallet).order_by("-created_at").first()
    return last.balance_after if last else Decimal("0.00")
