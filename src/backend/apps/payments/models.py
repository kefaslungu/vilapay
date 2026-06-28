import uuid

from django.db import models


class Contribution(models.Model):
    """A single member's contribution to a group cycle."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class PaymentMethod(models.TextChoices):
        VA_TRANSFER = "va_transfer", "Bank Transfer to VA"
        DIRECT_DEBIT = "direct_debit", "Direct Debit"
        SAVE_AHEAD = "save_ahead", "Save-Ahead Wallet"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cycle = models.ForeignKey(
        "groups.GroupCycle",
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    member = models.ForeignKey(
        "groups.GroupMembership",
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    payment_method = models.CharField(
        max_length=14, choices=PaymentMethod.choices, default=PaymentMethod.VA_TRANSFER
    )
    nomba_transaction_id = models.CharField(max_length=255, blank=True, db_index=True)
    nomba_reference = models.CharField(max_length=255, blank=True, db_index=True)
    failure_reason = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cycle", "member")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.member.user.email} → {self.cycle} "
            f"₦{self.amount} [{self.get_status_display()}]"
        )


class DirectDebitMandate(models.Model):
    """Nomba direct debit mandate: auto-collects contributions on schedule."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Activation"
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    membership = models.ForeignKey(
        "groups.GroupMembership",
        on_delete=models.CASCADE,
        related_name="direct_debit_mandates",
    )
    nomba_mandate_id = models.CharField(max_length=255, unique=True, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=10)  # mirrors Group.Frequency
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Mandate {self.nomba_mandate_id or 'PENDING'} — "
            f"{self.membership.user.email} [{self.get_status_display()}]"
        )
