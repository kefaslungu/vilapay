import uuid

from django.conf import settings
from django.db import models


class Payout(models.Model):
    """
    Disbursement of the collected pot to the cycle winner.
    Initiated automatically by Celery after all contributions are collected.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cycle = models.OneToOneField(
        "groups.GroupCycle",
        on_delete=models.PROTECT,
        related_name="payout",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payouts_received",
    )
    bank_account = models.ForeignKey(
        "users.UserBankAccount",
        on_delete=models.PROTECT,
        related_name="payouts",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    nomba_transfer_id = models.CharField(max_length=255, blank=True, db_index=True)
    nomba_reference = models.CharField(max_length=255, blank=True, db_index=True)
    failure_reason = models.TextField(blank=True)
    initiated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Payout {self.cycle} → {self.recipient.email} "
            f"₦{self.amount} [{self.get_status_display()}]"
        )
