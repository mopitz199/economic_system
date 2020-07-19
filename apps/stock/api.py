from datetime import datetime, timedelta
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status, viewsets

from apps.chart.api_serializers import GetChartRequestSerializer
from apps.chart.factory import GenerateChartFactory
from apps.stock.api_serializers import (
    CreateMultipleDilutedEPSRequestSerializer,
)
from apps.stock.factory import DilutedEPSFactory
from apps.stock.services import DilutedEPSServices


class CreateMultipleDilutedEPS(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = CreateMultipleDilutedEPSRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        data_list = validated_data['diluted_eps_data']
        DilutedEPSFactory.create_multiple_diluted_eps(data_list)
        return Response(
            {},
            status=status.HTTP_201_CREATED
        )


class GetPER(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        end = datetime.today()
        start = end - timedelta(days=365)
        symbol = request.query_params['symbol']
        data = {
            'symbol': symbol,
            'asset_type': 'stocks',
            'time_frame': '1m',
            'start': start,
            'end': end,
        }
        serializer = GetChartRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        chart_data = GenerateChartFactory.generate_chart(
            **validated_data
        )
        response_data = {
            'results': []
        }
        for point_data in chart_data:
            date_obj = point_data['date']
            eps = DilutedEPSServices.get_eps(symbol, date_obj)
            if eps:
                per = point_data['price']/eps.value
            else:
                per = None
            response_data['results'].append({
                'date': date_obj,
                'per': per
            })
        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
