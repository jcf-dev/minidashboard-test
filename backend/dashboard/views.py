from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils.crypto import constant_time_compare
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Client, MonthlyTarget, Sale
from .serializers import DashboardSerializer, TargetUpdateSerializer


def _month_start(value=None):
    today = value or date.today()
    return date(today.year, today.month, 1)


def _month_end(month):
    return date(month.year, month.month, monthrange(month.year, month.month)[1])


def _is_authorized(request):
    api_key = request.headers.get("X-API-Key", "")
    return constant_time_compare(api_key, settings.DASHBOARD_API_KEY)


class DashboardAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ["get", "patch", "options"]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = settings.CORS_ALLOWED_ORIGIN
        response["Access-Control-Allow-Methods"] = "GET, PATCH, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Client-Id"
        return response

    def options(self, request, *args, **kwargs):
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request):
        client_response = self._authorized_client_response(request)
        if isinstance(client_response, Response):
            return client_response

        return Response(self._payload_for_client(client_response))

    def patch(self, request):
        client_response = self._authorized_client_response(request)
        if isinstance(client_response, Response):
            return client_response

        serializer = TargetUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return self._error(
                "Request body must include a numeric monthlyGoal zero or greater.",
                status.HTTP_400_BAD_REQUEST,
            )

        MonthlyTarget.objects.update_or_create(
            client=client_response,
            month=_month_start(),
            defaults={"goal": serializer.validated_data["monthlyGoal"]},
        )
        return Response(self._payload_for_client(client_response))

    def _authorized_client_response(self, request):
        if not _is_authorized(request):
            return self._error("Invalid or missing API key.", status.HTTP_401_UNAUTHORIZED)

        client_id = request.headers.get("X-Client-Id")
        if not client_id:
            return self._error("X-Client-Id header is required.", status.HTTP_400_BAD_REQUEST)

        try:
            client_id = int(client_id)
        except ValueError:
            return self._error("X-Client-Id must be an integer.", status.HTTP_400_BAD_REQUEST)

        return get_object_or_404(Client, id=client_id)

    def _payload_for_client(self, client):
        month = _month_start()
        target, _ = MonthlyTarget.objects.get_or_create(
            client=client,
            month=month,
            defaults={"goal": Decimal("0")},
        )
        month_sales = Sale.objects.filter(
            client=client,
            sold_at__gte=month,
            sold_at__lte=_month_end(month),
        )
        all_sales = Sale.objects.filter(client=client)
        month_total = month_sales.aggregate(total=Sum("amount"))["total"] or Decimal("0")

        serializer = DashboardSerializer(
            {
                "client": client,
                "month": month,
                "monthlyGoal": target.goal,
                "monthlyTotal": month_total,
                "sales": all_sales,
            }
        )
        return serializer.data

    def _error(self, message, response_status):
        return Response({"error": message}, status=response_status)


dashboard_api = DashboardAPIView.as_view()
