from django.contrib.auth.models import User
from django.db import models

from apps.asset.models import Asset

from constants import (
    PriceMaxDigits,
    PriceDecimalPlaces,
)


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class AssetPortfolio(models.Model):

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        null=True
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.FloatField()
    purchase_price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
