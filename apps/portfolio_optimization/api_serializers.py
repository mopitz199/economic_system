from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.chart.constants import MILESTONE_TYPES

from apps.asset.api_serializers import AssetFullSerializer
from apps.portfolio_optimization.models import (
    PortfolioOptimization,
    AssetOptimization,
)
from constants import PriceDecimalPlaces, PriceMaxDigits
from utils import price_to_show


class AssetOptimizationSerializer(serializers.ModelSerializer):

    asset = AssetFullSerializer()
    amount_to_invest = serializers.SerializerMethodField()

    class Meta:
        model = AssetOptimization
        fields = '__all__'

    def get_amount_to_invest(self, obj):
        if obj.amount_to_invest:
            return price_to_show(obj.amount_to_invest)
        else:
            return obj.amount_to_invest


class PortfolioOptimizationSerializer(serializers.ModelSerializer):

    assetoptimization_set = AssetOptimizationSerializer(
        read_only=True,
        many=True
    )
    total_amount_to_invest = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioOptimization
        fields = '__all__'

    def get_total_amount_to_invest(self, obj):
        if obj.total_amount_to_invest:
            return price_to_show(obj.total_amount_to_invest)
        else:
            return obj.total_amount_to_invest


class RequestCreateAssetOptimization(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)

    class Meta:
        model = AssetOptimization
        fields = (
            'id',
            'asset',
            'min_to_invest',
            'max_to_invest',
            'amount_to_invest'
        )


class RequestCreatePortfolioOptimizationSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    asset_optimizations = RequestCreateAssetOptimization(many=True)
    min_disposed_to_lose = serializers.FloatField(max_value=100, min_value=0)
    total_amount_to_invest = serializers.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces,
        required=False,
    )
    optimism = serializers.FloatField(max_value=100, min_value=0)
    user = serializers.IntegerField()
    name = serializers.CharField()


class RequestOptimizationSerializer(serializers.Serializer):

    class AssetSimulateOptimizationRequest(serializers.Serializer):
        asset_id = serializers.IntegerField()
        min_to_invest = serializers.FloatField(max_value=100, min_value=0)
        max_to_invest = serializers.FloatField(max_value=100, min_value=0)
        amount_to_invest = serializers.DecimalField(
            max_digits=PriceMaxDigits,
            decimal_places=PriceDecimalPlaces,
            required=False,
        )

    optimism = serializers.FloatField(max_value=100, min_value=0)
    total_amount_to_invest = serializers.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces,
        required=False,
    )
    min_disposed_to_lose = serializers.FloatField(
        max_value=100,
        min_value=0,
        required=True,
    )
    asset_optimizations = AssetSimulateOptimizationRequest(many=True)

    def custom_validate_asset_optimizations(self, data):
        total_amount_to_invest = data.get('total_amount_to_invest')
        for asset_optimization in data['asset_optimizations']:
            amount_to_invest = asset_optimization.get('amount_to_invest')
            if amount_to_invest is not None and total_amount_to_invest is None:
                return False
        return True

    def validate(self, data):
        if not self.custom_validate_asset_optimizations(data):
            raise ValidationError({
                "error": "It's mandatory the total amount to invest"
            })
        return data
