from rest_framework import serializers

from apps.asset.api_serializers import AssetSerializer
from apps.asset.models import Asset, AssetDetail
from apps.portfolio.models import AssetPortfolio

from apps.asset.services import get_current_asset_price
from apps.portfolio.services import (
    get_asset_portfolio_performance,
    get_asset_portfolio_earning,
)
from utils import price_to_show


class AssetPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetPortfolio
        fields = '__all__'


class AssetPortfolioViewSerializer(serializers.ModelSerializer):

    asset = AssetSerializer()
    current_price = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()
    purchase_price = serializers.SerializerMethodField()
    earnings = serializers.SerializerMethodField()

    def get_earnings(self, obj):
        earning = get_asset_portfolio_earning(obj)
        if earning:
            earning = price_to_show(earning)
        return earning

    def get_purchase_price(self, obj):
        return price_to_show(obj.purchase_price)

    def get_current_price(self, obj):
        val = get_current_asset_price(obj.asset)
        if not val:
            return ""
        else:
            return price_to_show(val)

    def get_performance(self, obj):
        val = get_asset_portfolio_performance(obj)
        if not val:
            return ""
        else:
            return round(price_to_show(val), 2)

    class Meta:
        model = AssetPortfolio
        fields = '__all__'