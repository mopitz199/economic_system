from django.db import models

from apps.asset.models import Asset


class Ranking(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    marketcap = models.BigIntegerField()
    ranking = models.IntegerField()
    ranking_date = models.DateField()
    price = models.DecimalField(max_digits=30, decimal_places=10)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
