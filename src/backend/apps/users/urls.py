from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import (
    BankAccountDetailView,
    BankAccountListCreateView,
    BanksListView,
    RegisterView,
    UserProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("me/", UserProfileView.as_view(), name="auth-me"),
    path("me/bank-accounts/", BankAccountListCreateView.as_view(), name="bank-account-list"),
    path(
        "me/bank-accounts/<uuid:pk>/",
        BankAccountDetailView.as_view(),
        name="bank-account-detail",
    ),
    path("banks/", BanksListView.as_view(), name="banks-list"),
]
