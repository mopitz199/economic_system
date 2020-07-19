from rest_framework import serializers

from apps.chart.models import Point, Chart
from apps.chart.constants import (
    AVAILABLE_TIME_FRAMES,
    SAVED_CHART_TYPE_CHOICES,
)
from apps.asset.api_serializers import AssetSerializer
from constants import ASSET_TYPES, PriceDecimalPlaces, PriceMaxDigits


class ChartSerializer(serializers.ModelSerializer):

    asset = AssetSerializer()

    class Meta:
        model = Chart
        fields = '__all__'


class CreateChartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = '__all__'


class GetChartRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20)
    asset_type = serializers.ChoiceField(choices=ASSET_TYPES)
    time_frame = serializers.ChoiceField(choices=AVAILABLE_TIME_FRAMES)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()


class BulkPointsRequest(serializers.Serializer):

    class PointRequestSerializer(serializers.ModelSerializer):
        class Meta:
            model = Point
            fields = ['chart', 'price', 'volume', 'source', 'point_date']

    points = PointRequestSerializer(many=True)


class BulkPointsWithoutChartRequest(serializers.Serializer):

    class PointRequestWithoutChartSerializer(serializers.Serializer):
        symbol = serializers.CharField(max_length=20)
        asset_type = serializers.ChoiceField(choices=ASSET_TYPES)
        time_frame = serializers.ChoiceField(choices=AVAILABLE_TIME_FRAMES)
        price = serializers.DecimalField(
            max_digits=PriceMaxDigits,
            decimal_places=PriceDecimalPlaces
        )
        point_date = serializers.DateTimeField()

    points = PointRequestWithoutChartSerializer(many=True)


class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = '__all__'
