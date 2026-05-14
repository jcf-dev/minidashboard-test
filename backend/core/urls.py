from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from dashboard.views import dashboard_api


def healthz(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    path("api/dashboard/", dashboard_api, name="dashboard_api"),
]
