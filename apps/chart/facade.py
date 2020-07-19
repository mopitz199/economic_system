from datetime import timedelta
from typing import List

from apps.chart.constants import (
    CANDLE_CHART_TYPE,
    POINT_CHART_TYPE,
    PER_HOUR,
    PER_FOUR_HOURS,
    PER_DAY,
    PER_WEEK,
    PER_MONTH,
    PER_YEAR,
)

from apps.chart.models import Point, Candle
from utils import chunks


class ChartFacade:

    def __init__(self, chart):
        self.chart = chart

    def get_type_data(self):
        chart_type = self.chart.chart_type
        if chart_type == CANDLE_CHART_TYPE:
            return Candle
        elif chart_type == POINT_CHART_TYPE:
            return Point
        else:
            raise Exception(f'{chart_type} not found')

    def get_data_name(self):
        chart_type = self.chart.chart_type
        if chart_type == CANDLE_CHART_TYPE:
            return CANDLE_CHART_TYPE
        elif chart_type == POINT_CHART_TYPE:
            return POINT_CHART_TYPE
        else:
            raise Exception(f'{chart_type} not found')

    def get_data(self, start, end):
        chart_type_cls = self.get_type_data()
        data_name = self.get_data_name()

        filters = {
            f'{data_name}_date__gte': start,
            f'{data_name}_date__lte': end,
        }

        order_data = [f'{data_name}_date']

        return chart_type_cls.objects\
            .filter(chart=self.chart)\
            .filter(**filters)\
            .order_by(*order_data)


class PointFacade:

    def __init__(self, point):
        self.point = point


class CandleFacade:
    pass