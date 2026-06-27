from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API docs
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Apps
    path("v1/auth/", include("apps.users.urls")),
    path("v1/groups/", include("apps.groups.urls")),
    path("v1/wallets/", include("apps.wallets.urls")),
    path("v1/payments/", include("apps.payments.urls")),
    path("v1/payouts/", include("apps.payouts.urls")),
    # Prometheus metrics
    path("", include("django_prometheus.urls")),
]
