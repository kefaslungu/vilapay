from decimal import Decimal


def record_entry(
    group, entry_type, amount, nomba_transaction_ref="", description="", membership=None
):
    from apps.wallets.models import LedgerEntry

    last_entry = LedgerEntry.objects.filter(group=group).order_by("-created_at").first()
    previous_balance = last_entry.balance_after if last_entry else Decimal("0.00")

    if entry_type == "deposit":
        balance_after = previous_balance + Decimal(str(amount))
    else:
        balance_after = previous_balance - Decimal(str(amount))

    return LedgerEntry.objects.create(
        group=group,
        membership=membership,
        entry_type=entry_type,
        amount=Decimal(str(amount)),
        balance_after=balance_after,
        nomba_transaction_ref=nomba_transaction_ref,
        description=description,
    )


def get_group_balance(group):
    from apps.wallets.models import LedgerEntry

    last_entry = LedgerEntry.objects.filter(group=group).order_by("-created_at").first()
    return last_entry.balance_after if last_entry else Decimal("0.00")
