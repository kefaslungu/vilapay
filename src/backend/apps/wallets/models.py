import uuid

from django.conf import settings
from django.db import models


class SaveAheadWallet(models.Model):
    """
    Personal pre-saving wallet tied to a group membership slot.
    Members deposit here ahead of their contribution deadline; the
    automated collection job sweeps from this wallet on the due date.
    Free tier: 1 wallet; Individual Pro: up to 5.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="save_ahead_wallets",
    )
    membership = models.OneToOneField(
        "groups.GroupMembership",
        on_delete=models.CASCADE,
        related_name="save_ahead_wallet",
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Nomba VA for this wallet — members send money here to pre-save
    nomba_virtual_account_id = models.CharField(max_length=255, blank=True)
    nomba_virtual_account_number = models.CharField(max_length=20, blank=True)
    nomba_virtual_account_bank = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.membership.group.name} wallet (₦{self.balance})"


class LedgerEntry(models.Model):
    """
    Immutable audit trail of every credit and debit across groups and wallets.
    Provides the transparency guarantee: no admin can hide fund movements.
    """

    class EntryType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        PAYOUT = "payout", "Payout"
        REFUND = "refund", "Refund"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # A ledger entry belongs to either a group OR a wallet (or both)
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )
    wallet = models.ForeignKey(
        SaveAheadWallet,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )
    membership = models.ForeignKey(
        "groups.GroupMembership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )

    entry_type = models.CharField(max_length=12, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    nomba_transaction_ref = models.CharField(max_length=255, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        target = self.group or self.wallet
        return f"{self.get_entry_type_display()} ₦{self.amount} → {target}"
