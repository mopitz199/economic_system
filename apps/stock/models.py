from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.asset.models import Asset

from constants import DilutedEPSDecimalPlaces, DilutedEPSMaxDigits
from apps.stock.constants import (
    DILUTED_EPS_CHOICES,
    DILUTED_EPS_CHOICES_LENGTH,
)


class DilutedEPS(models.Model):

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    value = models.DecimalField(
        max_digits=DilutedEPSMaxDigits,
        decimal_places=DilutedEPSDecimalPlaces
    )
    time_frames = ArrayField(
        models.CharField(
            max_length=DILUTED_EPS_CHOICES_LENGTH,
            choices=DILUTED_EPS_CHOICES,
        ),
        blank=True,
        null=True,
    )
    diluted_eps_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
