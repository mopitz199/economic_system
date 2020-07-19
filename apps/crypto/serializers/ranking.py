from rest_framework import serializers

from apps.crypto.models import Ranking
from constants import (
    PriceDecimalPlaces,
    PriceMaxDigits,
    SymbolMaxLength,
    AssetNameMaxLength
)


# Serializers define the API representation.
class RankingSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Ranking
        fields = '__all__'


class RankingFromSymbolSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=SymbolMaxLength)
    ranking_date = serializers.CharField()
    slug = serializers.CharField()
    ranking = serializers.IntegerField()
    marketcap = serializers.IntegerField()
    price = serializers.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
