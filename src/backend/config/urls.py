from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Apps
    path("api/auth/", include("apps.users.urls")),
    path("api/groups/", include("apps.groups.urls")),
    path("api/wallets/", include("apps.wallets.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/payouts/", include("apps.payouts.urls")),
    # Prometheus metrics
    path("", include("django_prometheus.urls")),
]
