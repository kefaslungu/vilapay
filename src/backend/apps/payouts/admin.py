from django.contrib import admin

from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("recipient", "cycle", "amount", "status", "bank_account", "initiated_at", "completed_at")
    list_filter = ("status",)
    search_fields = ("recipient__email", "nomba_transfer_id", "nomba_reference")
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "cycle", "recipient", "bank_account", "amount", "status")}),
        ("Nomba", {"fields": ("nomba_transfer_id", "nomba_reference", "failure_reason")}),
        ("Timeline", {"fields": ("initiated_at", "completed_at", "created_at", "updated_at")}),
    )
