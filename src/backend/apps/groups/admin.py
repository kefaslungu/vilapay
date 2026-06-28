from django.contrib import admin

from .models import Group, GroupCycle, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    readonly_fields = ("id", "joined_at")
    fields = ("user", "slot_number", "status", "joined_at")


class GroupCycleInline(admin.TabularInline):
    model = GroupCycle
    extra = 0
    readonly_fields = ("id", "created_at")
    fields = (
        "cycle_number",
        "recipient",
        "start_date",
        "end_date",
        "payout_date",
        "status",
        "total_collected",
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_by",
        "slot_count",
        "contribution_amount",
        "frequency",
        "status",
        "current_cycle",
        "created_at",
    )
    list_filter = ("status", "frequency")
    search_fields = ("name", "created_by__email")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [GroupMembershipInline, GroupCycleInline]

    fieldsets = (
        (None, {"fields": ("id", "name", "created_by", "status")}),
        (
            "Configuration",
            {
                "fields": (
                    "slot_count",
                    "contribution_amount",
                    "frequency",
                    "start_date",
                )
            },
        ),
        (
            "Nomba",
            {
                "fields": (
                    "nomba_sub_account_id",
                    "nomba_virtual_account_id",
                    "nomba_virtual_account_number",
                    "nomba_virtual_account_bank",
                )
            },
        ),
        ("Progress", {"fields": ("current_cycle",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "slot_number", "status", "joined_at")
    list_filter = ("status",)
    search_fields = ("user__email", "group__name")
    readonly_fields = ("id", "joined_at")


@admin.register(GroupCycle)
class GroupCycleAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "cycle_number",
        "recipient",
        "start_date",
        "end_date",
        "status",
        "total_collected",
    )
    list_filter = ("status",)
    search_fields = ("group__name",)
    readonly_fields = ("id", "created_at", "updated_at")
