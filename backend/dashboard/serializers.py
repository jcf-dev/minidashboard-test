from decimal import Decimal

from rest_framework import serializers

from .models import Client, Sale


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "email"]


class SaleSerializer(serializers.ModelSerializer):
    soldAt = serializers.DateField(source="sold_at")
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Sale
        fields = ["id", "label", "amount", "soldAt"]


class DashboardSerializer(serializers.Serializer):
    client = ClientSerializer()
    month = serializers.DateField()
    monthlyGoal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )
    monthlyTotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )
    sales = SaleSerializer(many=True)


class TargetUpdateSerializer(serializers.Serializer):
    monthlyGoal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        coerce_to_string=False,
    )
