import uuid

from django.conf import settings
from django.db import models


class Group(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Frequency(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_groups",
    )
    slot_count = models.PositiveSmallIntegerField(
        help_text="Total number of members/slots"
    )
    contribution_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount each member contributes per cycle (NGN)",
    )
    frequency = models.CharField(
        max_length=10, choices=Frequency.choices, default=Frequency.MONTHLY
    )
    start_date = models.DateField()
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.DRAFT
    )

    # Nomba sub-account & virtual account for fund isolation
    nomba_sub_account_id = models.CharField(max_length=255, blank=True)
    nomba_virtual_account_id = models.CharField(max_length=255, blank=True)
    nomba_virtual_account_number = models.CharField(max_length=20, blank=True)
    nomba_virtual_account_bank = models.CharField(max_length=100, blank=True)

    current_cycle = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def pot_amount(self):
        """Total amount in the pot per cycle."""
        return self.contribution_amount * self.slot_count


class GroupMembership(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        LEFT = "left", "Left"
        REMOVED = "removed", "Removed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="group_memberships",
    )
    slot_number = models.PositiveSmallIntegerField(
        help_text="Position in the rotation (1-based)"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("group", "slot_number"), ("group", "user")]
        ordering = ["slot_number"]

    def __str__(self):
        return f"{self.user.email} — {self.group.name} slot #{self.slot_number}"


class GroupCycle(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COLLECTING = "collecting", "Collecting"
        PAYOUT_PENDING = "payout_pending", "Payout Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="cycles")
    cycle_number = models.PositiveSmallIntegerField()
    recipient = models.ForeignKey(
        GroupMembership,
        on_delete=models.PROTECT,
        related_name="receiving_cycles",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    payout_date = models.DateField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    total_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("group", "cycle_number")
        ordering = ["cycle_number"]

    def __str__(self):
        return f"{self.group.name} — Cycle #{self.cycle_number}"
