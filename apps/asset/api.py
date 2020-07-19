import json
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.shortcuts import render

from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status, viewsets

from apps.asset.api_serializers import (
    AssetSerializer,
    GetCoinmatketcapIdsResponse,
    AssetFullSerializer,
)
from apps.asset.models import AssetDetail, Asset
from apps.asset.services import (
    get_asset_search_result,
    get_24_hour_asset_performance,
    get_weekly_asset_performance,
    get_monthly_asset_performance,
    get_max_price,
    get_current_asset_price,
)
from apps.chart.services import build_asset_milestones, create_chart
from apps.portfolio.models import AssetPortfolio, Portfolio

from utils import price_to_show, num_integer_part


class GetCoinmatketcapIds(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(responses={201: GetCoinmatketcapIdsResponse})
    def get(self, request, format=None):
        coinmarketcap_ids = list(
            AssetDetail.objects.filter(
                name='coinmarketcap'
            ).values_list('data__coinmarketcap_id', flat=True)
        )

        serializer = GetCoinmatketcapIdsResponse(
            data={'ids': coinmarketcap_ids}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED
        )


class CreateCompleteCryptoAsset(APIView):

    @transaction.atomic
    def post(self, request, format=None):
        data = request.data
        asset = Asset(
            name=data['name'],
            slug=data['slug'],
            symbol=data['symbol'],
            asset_type='cryptos'
        )
        asset.save()
        build_asset_milestones(asset)
        create_chart(asset, '1d', 'candle')

        generic_asset_detail = AssetDetail(
            asset=asset,
            name='generic',
            data={
                "chat": data['chat'],
                "logo": data['logo'],
                "tags": data['tags'],
                "reddit": data['reddit'],
                "twitter": data['twitter'],
                "website": data['website'],
                "category": data['category'],
                "explorer": data['explorer'],
                "description": data['description'],
                "source_code": data['source_code'],
                "announcement": data['announcement'],
                "message_board": data['message_board'],
                "technical_doc": data['technical_doc']
            }
        )
        generic_asset_detail.save()

        coinmarketcap_asset_detail = AssetDetail(
            name='coinmarketcap',
            asset=asset,
            data={
                "coinmarketcap_id": data['id'],
                "first_historical_data": data['first_historical_data']
            }
        )
        coinmarketcap_asset_detail.save()
        return Response(
            AssetSerializer(asset).data,
            status.HTTP_201_CREATED
        )


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_fields = ('symbol', 'asset_type')

    def get_serializer_class(self):
        req = self.request
        detail = req.query_params.get('detail')
        if detail:
            return AssetFullSerializer
        return super().get_serializer_class()


class AssetSearch(APIView):

    def get(self, request):
        query = request.query_params.get('q')
        return Response(
            {
                'results': get_asset_search_result(query)
            },
            status.HTTP_200_OK
        )


class AssetProfile(APIView):

    def get(self, request):
        asset_id = request.query_params.get('asset_id')
        asset = Asset.objects.get(id=asset_id)
        performance_24_hours = get_24_hour_asset_performance(asset)
        performance_weekly = get_weekly_asset_performance(asset)
        performance_monthly = get_monthly_asset_performance(asset)
        max_price = price_to_show(get_max_price(asset))
        price = price_to_show(get_current_asset_price(asset))
        serializer = AssetFullSerializer(asset)

        day_performance_num_integers = None
        if performance_24_hours:
            day_performance_num_integers = num_integer_part(
                performance_24_hours
            )

        weekly_performance_num_integers = None
        if performance_weekly:
            weekly_performance_num_integers = num_integer_part(
                performance_weekly
            )

        monthly_performance_num_integers = None
        if performance_monthly:
            monthly_performance_num_integers = num_integer_part(
                performance_monthly
            )

        performance = {
            'num_decimals': price.as_tuple().exponent*-1,
            'price': price,
            'historical_max_price': max_price,
            'day_performance': performance_24_hours,
            'day_performance_num_integers': day_performance_num_integers,
            'weekly_performance': performance_weekly,
            'weekly_performance_num_integers': weekly_performance_num_integers,
            'monthly_performance': performance_monthly,
            'monthly_performance_num_integers': monthly_performance_num_integers,
        }

        return Response(
            {
                'results': {
                    'asset': serializer.data,
                    'performance': performance,
                }
            },
            status.HTTP_200_OK
        )
