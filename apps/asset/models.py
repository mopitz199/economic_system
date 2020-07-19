from django.contrib.auth.models import User
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.db import models

from constants import (
    SymbolMaxLength,
    AssetNameMaxLength,
    CURRENCY_LENGTH,
    ASSET_TYPES,
    PriceMaxDigits,
    PriceDecimalPlaces,
)


class Asset(models.Model):

    name = models.CharField(max_length=AssetNameMaxLength)
    slug = models.CharField(max_length=256)
    symbol = models.CharField(max_length=SymbolMaxLength)
    currency = models.CharField(
        max_length=CURRENCY_LENGTH,
        null=True,
        blank=True
    )
    enabled = models.BooleanField(default=True)
    asset_type = models.CharField(
        max_length=50,
        choices=ASSET_TYPES,
        null=True,
        blank=True
    )
    health = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol}"


class AssetDetail(models.Model):

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    data = HStoreField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
