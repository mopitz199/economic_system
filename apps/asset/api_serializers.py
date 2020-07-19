from rest_framework import serializers

from apps.asset.models import Asset, AssetDetail
from apps.portfolio.models import AssetPortfolio

from apps.asset.services import get_current_asset_price
from apps.portfolio.services import (
    get_asset_portfolio_performance,
    get_asset_portfolio_earning,
)
from utils import price_to_show


class AssetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDetail
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


class AssetFullSerializer(serializers.ModelSerializer):

    detail = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id',
            'name',
            'symbol',
            'slug',
            'asset_type',
            'detail',
        ]

    def get_detail(self, obj):
        detail = obj.assetdetail_set.filter(name='generic').first()
        if detail:
            return detail.data
        else:
            return None


class GetCoinmatketcapIdsResponse(serializers.Serializer):

    ids = serializers.ListField(allow_empty=True)
