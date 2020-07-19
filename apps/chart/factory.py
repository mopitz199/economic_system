from datetime import datetime

from apps.chart.constants import (
    PER_DAY,
    PER_HOUR,
    CANDLE_CHART_TYPE,
    POINT_CHART_TYPE,
)
from apps.chart.models import Chart

from apps.chart.facade import ChartFacade
from apps.chart.services import (
    transform_candles,
    transform_points,
)


class GenerateChartFactory:

    @staticmethod
    def _transform(
        chart: Chart,
        time_frame: str,
        start: datetime,
        end: datetime,
    ):
        chart_facade = ChartFacade(chart)
        chart_data = chart_facade.get_data(
            start=start,
            end=end
        )
        if chart.chart_type == CANDLE_CHART_TYPE:
            return transform_candles(
                chart_data,
                time_frame,
                start,
                end,
            )
        elif chart.chart_type == POINT_CHART_TYPE:
            return transform_points(
                chart_data,
                time_frame
            )
        else:
            raise Exception(f'Chart type {chart.chart_type} not found')

    @staticmethod
    def generate_chart(
        symbol: str,
        asset_type: str,
        time_frame: str,
        start: datetime,
        end: datetime,
    ):
        day_chart = Chart.objects.filter(
            asset__asset_type=asset_type,
            asset__symbol=symbol,
            time_frame=PER_DAY
        ).first()

        all_data = []
        if day_chart:
            data = GenerateChartFactory._transform(
                day_chart,
                time_frame,
                start,
                end,
            )
            all_data += data

        hour_chart = Chart.objects.filter(
            asset__asset_type=asset_type,
            asset__symbol=symbol,
            time_frame=PER_HOUR
        ).first()

        if hour_chart:
            data = GenerateChartFactory._transform(
                hour_chart,
                time_frame,
                start,
                end,
            )
            all_data += data

        sorted_data = sorted(all_data, key=lambda d: d['date'])
        return sorted_data
