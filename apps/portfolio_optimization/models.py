from django.contrib.auth.models import User
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.db import models

from apps.asset.models import Asset

from constants import (
    SymbolMaxLength,
    AssetNameMaxLength,
    CURRENCY_LENGTH,
    ASSET_TYPES,
    PriceMaxDigits,
    PriceDecimalPlaces,
)


class PortfolioOptimization(models.Model):

    name = models.CharField(max_length=256)
    min_disposed_to_lose = models.FloatField()
    total_amount_to_invest = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    optimism = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AssetOptimization(models.Model):

    min_to_invest = models.FloatField()
    max_to_invest = models.FloatField()
    portfolio_optimization = models.ForeignKey(
        PortfolioOptimization,
        on_delete=models.CASCADE
    )
    amount_to_invest = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces,
        null=True,
        blank=True,
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
