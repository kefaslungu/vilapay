from django.contrib import admin

from .models import Contribution, DirectDebitMandate


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("member", "cycle", "amount", "status", "payment_method", "paid_at", "created_at")
    list_filter = ("status", "payment_method")
    search_fields = ("member__user__email", "nomba_transaction_id", "nomba_reference")
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "cycle", "member", "amount", "status")}),
        ("Payment", {"fields": ("payment_method", "nomba_transaction_id", "nomba_reference", "failure_reason", "paid_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(DirectDebitMandate)
class DirectDebitMandateAdmin(admin.ModelAdmin):
    list_display = ("membership", "nomba_mandate_id", "status", "amount", "frequency", "start_date", "end_date")
    list_filter = ("status", "frequency")
    search_fields = ("membership__user__email", "nomba_mandate_id")
    readonly_fields = ("id", "created_at", "updated_at")
