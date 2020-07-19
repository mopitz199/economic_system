from rest_framework import serializers

from apps.stock.models import DilutedEPS
from constants import DilutedEPSDecimalPlaces, DilutedEPSMaxDigits


class CreateMultipleDilutedEPSRequestSerializer(serializers.Serializer):

    class DilutedEPSData(serializers.Serializer):
        symbol = serializers.CharField(max_length=20)
        diluted_eps_date = serializers.DateField()
        value = serializers.DecimalField(
            max_digits=DilutedEPSMaxDigits,
            decimal_places=DilutedEPSDecimalPlaces
        )

    diluted_eps_data = DilutedEPSData(many=True)
