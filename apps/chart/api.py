import json
import matplotlib.pyplot as plt
import pandas
from datetime import datetime
from typing import List

from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse

from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status, viewsets

from apps.chart.api_serializers import (
    BulkPointsRequest,
    PointSerializer,
    ChartSerializer,
    CreateChartSerializer,
    GetChartRequestSerializer,
    BulkPointsWithoutChartRequest,
)
from apps.asset.models import Asset, AssetDetail
from apps.chart.constants import POINT_CHART_TYPE
from apps.chart.factory import GenerateChartFactory
from apps.chart.models import Point, Chart, Candle, Milestone
from apps.chart.services import get_percentage, create_milestone_table


class ChartViewSet(viewsets.ModelViewSet):

    queryset = Chart.objects.all()
    serializer_class = ChartSerializer
    filter_fields = (
        'chart_type',
        'asset__symbol',
        'time_frame',
        'asset__asset_type',
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChartSerializer
        else:
            return ChartSerializer


class GetChart(APIView):

    def post(self, request, format=None):
        request_serializer = GetChartRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        simulated_chart_data = GenerateChartFactory.generate_chart(**data)
        return Response(
            {'results': simulated_chart_data},
            status=status.HTTP_201_CREATED
        )


class BulkPoints(APIView):

    @swagger_auto_schema(
        request_body=BulkPointsRequest,
        responses={
            201: PointSerializer(many=True)
        }
    )
    def post(self, request, format=None):
        request_serializer = BulkPointsRequest(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        new_points = []
        for point_data in data['points']:
            point = Point(**point_data)
            new_points.append(point)

        points = Point.objects.bulk_create(new_points)
        response_serializer = PointSerializer(points, many=True)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class BulkPointsWithoutChart(APIView):

    @swagger_auto_schema(
        request_body=BulkPointsWithoutChartRequest,
        responses={
            201: PointSerializer(many=True)
        }
    )
    def post(self, request, format=None):
        request_serializer = BulkPointsWithoutChartRequest(
            data=request.data
        )
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        new_points = []
        for point_data in data['points']:
            symbol = point_data.pop('symbol')
            asset_type = point_data.pop('asset_type')
            time_frame = point_data.pop('time_frame')

            chart = Chart.objects.filter(
                asset__symbol=symbol,
                asset__asset_type=asset_type,
                time_frame=time_frame,
                chart_type=POINT_CHART_TYPE
            ).first()

            if chart:
                point_data['chart'] = chart
                point = Point(**point_data)
                new_points.append(point)

        points = Point.objects.bulk_create(new_points)
        response_serializer = PointSerializer(points, many=True)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class GetMilestoneData(APIView):

    def filter_function(self, row, filter_value, filter_type):
        for idx, index in enumerate(filter_type):
            index = int(index)
            if row[index] != filter_value[idx]:
                return False
        return True

    def sort_function(self, value, sort_by):
        mapping = [int, str, str, str, str, str]
        propper_type = None
        if sort_by >= len(mapping):
            propper_type = int
        else:
            propper_type = mapping[sort_by]

        if value is None:
            if propper_type == str:
                return ""
            if propper_type == int:
                return -999999999
            else:
                raise Exception('Unknown type')
        else:
            return value

    def apply_filters(
        self,
        milestone_table,
        filter_value,
        filter_type,
    ) -> List:
        if filter_type and filter_value:
            milestone_table = filter(
                lambda row: self.filter_function(
                    row,
                    filter_value,
                    filter_type
                ),
                milestone_table
            )
            milestone_table = list(milestone_table)
        return milestone_table

    def apply_search(self, milestone_table, search):
        if search:
            milestone_table = filter(
                lambda row: search.lower() in row[1].lower(),
                milestone_table
            )
            milestone_table = list(milestone_table)
        return milestone_table

    def apply_sort(self, milestone_table, sort_by, sort_type):
        if sort_by and sort_type:
            sort_by = int(sort_by)
            if sort_type == 'ascending':
                milestone_table = sorted(
                    milestone_table,
                    key=lambda row: self.sort_function(row[sort_by], sort_by)
                )
            else:
                milestone_table = sorted(
                    milestone_table,
                    key=lambda row: self.sort_function(row[sort_by], sort_by),
                    reverse=True
                )
        return milestone_table

    def get_or_create_milestone_table(self):
        milestone_table = cache.get("milestone_table")
        if not milestone_table:
            milestone_table = create_milestone_table()
            cache.set(
                "milestone_table",
                json.dumps(milestone_table),
                timeout=None,
            )
        else:
            milestone_table = json.loads(milestone_table)
        return milestone_table

    def get_filter_lists(self, milestone_table):
        asset_type = []
        industry = []
        sector = []
        for row in milestone_table:
            asset_type.append(row[3])
            sector.append(row[4])
            industry.append(row[5])
        return {
            'asset_type': list(set(asset_type)),
            'sector': list(set(sector)),
            'industry': list(set(industry)),
        }

    def get(self, request):

        milestone_table = self.get_or_create_milestone_table()

        filter_value = request.query_params.getlist('filterValue[]', [])
        filter_type = request.query_params.getlist('filterType[]', [])
        search = request.query_params.get('search', '')
        sort_by = request.query_params.get('sort_by')
        sort_type = request.query_params.get('sort_type')
        page = int(request.query_params.get('page', 0))
        limit = int(request.query_params.get('limit', 20))

        milestone_table = self.apply_filters(
            milestone_table,
            filter_value,
            filter_type
        )
        milestone_table = self.apply_search(milestone_table, search)
        milestone_table = self.apply_sort(milestone_table, sort_by, sort_type)

        filter_lists = self.get_filter_lists(milestone_table)

        count = len(milestone_table)

        start = page*limit
        end = (page+1)*limit
        page = page + 1

        milestone_table = milestone_table[start:end]

        milestone_column_names = []
        for milestone in Milestone.objects.all().order_by('start'):
            milestone_column_names.append(f'Down {milestone.name}')
            milestone_column_names.append(f'Up {milestone.name}')

        return Response(
            {
                'page': page - 1,
                'count': count,
                'results': {
                    'data': milestone_table,
                    'filterDataList': filter_lists,
                    'milestoneColumnNames': milestone_column_names
                }
            },
            status=status.HTTP_201_CREATED
        )
