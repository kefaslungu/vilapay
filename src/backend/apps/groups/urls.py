from django.urls import path

from apps.groups.views import (
    ActivateGroupView,
    CancelGroupView,
    GroupCyclesView,
    GroupDetailView,
    GroupListCreateView,
    GroupMembersView,
    JoinByCodeView,
    JoinGroupView,
)

urlpatterns = [
    path("", GroupListCreateView.as_view(), name="group-list-create"),
    path("join-by-code/", JoinByCodeView.as_view(), name="group-join-by-code"),
    path("<uuid:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("<uuid:pk>/join/", JoinGroupView.as_view(), name="group-join"),
    path("<uuid:pk>/activate/", ActivateGroupView.as_view(), name="group-activate"),
    path("<uuid:pk>/cancel/", CancelGroupView.as_view(), name="group-cancel"),
    path("<uuid:pk>/members/", GroupMembersView.as_view(), name="group-members"),
    path("<uuid:pk>/cycles/", GroupCyclesView.as_view(), name="group-cycles"),
]
