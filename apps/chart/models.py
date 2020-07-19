from django.db import models

from apps.asset.models import Asset
from apps.chart.constants import (
    SAVED_CHART_TYPE_CHOICES,
    PER_HOUR,
    PER_DAY,
    CANDLE_CHART_TYPE,
    POINT_CHART_TYPE,
    MILESTONE_TYPES,
)
from constants import PriceDecimalPlaces, PriceMaxDigits


class Chart(models.Model):

    TIME_FRAME_CHOICES = [
        (PER_DAY, '1 day'),
        (PER_HOUR, '1 hour'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    time_frame = models.CharField(max_length=10, choices=TIME_FRAME_CHOICES)
    chart_type = models.CharField(
        max_length=10,
        choices=SAVED_CHART_TYPE_CHOICES,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.chart_type == CANDLE_CHART_TYPE:
            num = self.candle_set.all().count()
        elif self.chart_type == POINT_CHART_TYPE:
            num = self.point_set.all().count()
        return f"{self.time_frame}->{self.asset}->({num})"


class Candle(models.Model):

    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)
    open_price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
    high_price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
    low_price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
    close_price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
    volume = models.BigIntegerField()
    source = models.CharField(max_length=50)
    candle_date = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"H: {self.high_price}, L:{self.low_price}->"
            f"{self.candle_date}->{self.chart}"
        )


class Point(models.Model):

    id = models.BigAutoField(primary_key=True)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=PriceMaxDigits,
        decimal_places=PriceDecimalPlaces
    )
    volume = models.BigIntegerField(blank=True, null=True)
    source = models.CharField(max_length=50)
    point_date = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"P: {self.price}->{self.point_date}->{self.chart}"
        )


class Milestone(models.Model):
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=256)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    milestone_type = models.CharField(
        choices=MILESTONE_TYPES,
        max_length=100,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AssetMilestone(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    deepest_down = models.FloatField(null=True, blank=True)
    biggest_up = models.FloatField(null=True, blank=True)
    total_performance = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AssetMilestoneComparision(models.Model):

    asset_milestone_1 = models.ForeignKey(
        AssetMilestone,
        on_delete=models.CASCADE,
        related_name='comparisions_1',
    )
    asset_milestone_2 = models.ForeignKey(
        AssetMilestone,
        on_delete=models.CASCADE,
        related_name='comparisions_2',
    )
    correlation = models.FloatField(null=True, blank=True)
