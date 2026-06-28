from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "name": "Vilapay API",
        "version": "1.0.0",
        "description": "Community rotating savings platform",
        "docs": request.build_absolute_uri("/v1/docs/"),
        "status": "operational",
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    # Root
    path("", api_root, name="api-root"),
    path("v1/", api_root, name="api-root-v1"),
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
