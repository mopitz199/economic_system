from decimal import Decimal
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Any

from django.db import transaction

from apps.chart.constants import (
    PER_HOUR,
    PER_FOUR_HOURS,
    PER_DAY,
    PER_WEEK,
    PER_MONTH,
    PER_YEAR,
)

from apps.asset.models import Asset
from apps.chart.models import Point, Candle, AssetMilestone, Chart, Milestone
from utils import (
    chunks,
    add_months,
    add_years,
    price_to_show,
    get_performance,
    str_to_datetime,
)


def group_points(points, target_time_frame) -> List[Any]:
    """Service to group a list of points instance in a list of
    dict single point data with the given target time frame"""

    def _group_points(points, target_time_frame):
        from itertools import groupby

        def keyfunc(point):
            if target_time_frame == PER_HOUR:
                return int(point.point_date.strftime("%Y%m%d%H"))
            elif target_time_frame == PER_DAY:
                if point.point_date.time() == time(0, 0, 0):
                    aux_date = point.point_date - timedelta(hours=1)
                    return int(aux_date.strftime("%Y%m%d"))
                else:
                    return int(point.point_date.strftime("%Y%m%d"))
            elif target_time_frame == PER_MONTH:
                return int(point.point_date.strftime("%Y%m"))
            elif target_time_frame == PER_YEAR:
                return int(point.point_date.strftime("%Y"))
            elif target_time_frame == PER_WEEK:
                return point.point_date.isocalendar()[1]
            else:
                raise Exception(f'Target frame not found: {target_time_frame}')

        chunks = []
        for key, group in groupby(points, keyfunc):
            chunks.append(list(group))
        return chunks

    def _group_four_hours_points(points):
        if not points:
            chunks = []
            return chunks

        sorted_points = sorted(points, key=lambda point: point.point_date)
        reference_point = sorted_points[0]
        chunks = []
        init_range = [
            reference_point.point_date,
            reference_point.point_date+timedelta(hours=4)
        ]
        chunk = []
        for point in points:
            if init_range[0] <= point.point_date < init_range[1]:
                point.init_hour = init_range[0].hour
                chunk.append(point)
            else:
                chunks.append(chunk)
                chunk = []
                init_range = [
                    init_range[1],
                    init_range[1]+timedelta(hours=4)
                ]
                while not init_range[0] <= point.point_date < init_range[1]:
                    init_range = [
                        init_range[1],
                        init_range[1]+timedelta(hours=4)
                    ]
                point.init_hour = init_range[0].hour
                chunk.append(point)

        if chunk not in chunks:
            chunks.append(chunk)
        return chunks

    def _get_minimun_data(target_time_frame):
        if target_time_frame == PER_HOUR:
            return 1
        elif target_time_frame == PER_FOUR_HOURS:
            return 4
        elif target_time_frame == PER_DAY:
            return 20
        if target_time_frame == PER_WEEK:
            return 20*7
        elif target_time_frame == PER_MONTH:
            return 20*25
        elif target_time_frame == PER_YEAR:
            return 20*25*300
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_chunk_reference_point(chunk):
        sorted_points = sorted(chunk, key=lambda point: point.point_date)
        len_point = len(sorted_points)
        reference_point = sorted_points[len_point-1]
        return reference_point

    def _past_to_next_day(reference_point, init_hour):
        current_hour = reference_point.point_date.hour
        return current_hour < init_hour

    def _get_last_four_hours_date(reference_point):
        init_hour = reference_point.init_hour

        if _past_to_next_day(reference_point, init_hour):
            aux_datetime = reference_point.point_date - timedelta(days=1)
        else:
            aux_datetime = reference_point.point_date

        aux_datetime = datetime.combine(aux_datetime, time(init_hour, 0, 0))
        return aux_datetime + timedelta(hours=3)

    def _get_last_week_day_date(reference_point):
        weekday = reference_point.point_date.weekday()
        days_left = 6-weekday
        return reference_point.point_date + timedelta(days=days_left)

    def _get_chunk_date(reference_point, target_time_frame):
        if target_time_frame == PER_HOUR:
            return reference_point.point_date.strftime("%Y-%m-%d %H:%M:%S")
        elif target_time_frame == PER_FOUR_HOURS:
            datetime_obj = _get_last_four_hours_date(
                reference_point
            )
            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        elif target_time_frame == PER_DAY:
            if reference_point.point_date.time() == time(0, 0, 0):
                aux_date = reference_point.point_date - timedelta(hours=1)
                return aux_date.strftime("%Y-%m-%d")
            else:
                return reference_point.point_date.strftime("%Y-%m-%d")
        elif target_time_frame == PER_WEEK:
            datetime_obj = _get_last_week_day_date(
                reference_point
            )
            return datetime_obj.strftime("%Y-%m-%d")
        elif target_time_frame == PER_MONTH:
            return reference_point.point_date.strftime("%Y-%m")
        elif target_time_frame == PER_YEAR:
            return reference_point.point_date.strftime("%Y")
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_chunk_point(chunk, target_time_frame):
        min_value = _get_minimun_data(target_time_frame)
        if len(chunk) >= min_value:
            reference_point = _get_chunk_reference_point(
                chunk
            )
            date_str = _get_chunk_date(
                reference_point,
                target_time_frame
            )
            if reference_point.price:
                return {
                    'date': date_str,
                    'price': price_to_show(reference_point.price)
                }
        else:
            return None

    final_points = []
    if target_time_frame != PER_FOUR_HOURS:
        chunks = _group_points(points, target_time_frame)
    else:
        chunks = _group_four_hours_points(points)

    for chunk in chunks:
        point = _get_chunk_point(
            chunk,
            target_time_frame
        )
        if point:
            final_points.append(point)
    return final_points


def group_candles(candles: List[Candle], target_time_frame: str) -> List[Any]:
    """Service to group a list of candles instance in a list of
    dict single point data with the given target time frame"""

    def _group_candles(candles, target_time_frame):
        from itertools import groupby

        def keyfunc(candle):
            if target_time_frame == PER_DAY:
                return int(candle.candle_date.strftime("%Y%m%d"))
            elif target_time_frame == PER_MONTH:
                return int(candle.candle_date.strftime("%Y%m"))
            elif target_time_frame == PER_YEAR:
                return int(candle.candle_date.strftime("%Y"))
            elif target_time_frame == PER_WEEK:
                return candle.candle_date.isocalendar()[1]
            else:
                raise Exception(f'Target frame not found: {target_time_frame}')

        chunks = []
        for key, group in groupby(candles, keyfunc):
            chunks.append(list(group))
        return chunks

    def _get_minimun_data(target_time_frame):
        if target_time_frame == PER_DAY:
            return 1
        if target_time_frame == PER_WEEK:
            return 5
        elif target_time_frame == PER_MONTH:
            return 15
        elif target_time_frame == PER_YEAR:
            return 250
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_chunk_reference_candle(chunk):
        sorted_candles = sorted(chunk, key=lambda candle: candle.candle_date)
        len_point = len(sorted_candles)
        reference_candle = sorted_candles[len_point-1]
        return reference_candle

    def _get_last_week_day_date(reference_candle):
        weekday = reference_candle.candle_date.weekday()
        days_left = 6-weekday
        return reference_candle.candle_date + timedelta(days=days_left)

    def _get_chunk_date(reference_candle, target_time_frame):
        if target_time_frame in [PER_DAY]:
            return reference_candle.candle_date.strftime("%Y-%m-%d")
        elif target_time_frame in [PER_WEEK]:
            chunk_date = _get_last_week_day_date(
                reference_candle
            )
            return chunk_date.strftime("%Y-%m-%d")
        elif target_time_frame == PER_MONTH:
            return reference_candle.candle_date.strftime("%Y-%m")
        elif target_time_frame == PER_YEAR:
            return reference_candle.candle_date.strftime("%Y")
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_chunk_point(chunk, target_time_frame):
        min_value = _get_minimun_data(target_time_frame)
        if len(chunk) >= min_value:
            reference_candle = _get_chunk_reference_candle(
                chunk
            )
            date_str = _get_chunk_date(
                reference_candle,
                target_time_frame
            )
            if reference_candle.close_price:
                return {
                    'date': date_str,
                    'price': price_to_show(reference_candle.close_price)
                }
        else:
            return None

    final_points = []
    chunks = _group_candles(candles, target_time_frame)

    for chunk in chunks:
        point = _get_chunk_point(
            chunk,
            target_time_frame
        )
        if point:
            final_points.append(point)
    return final_points


def split_candles(
    candles: List[Candle],
    target_time_frame: str,
    start: datetime,
    end: datetime,
):
    """Separate a list of candles in a list of single point dicts where
    each point dict represent the target time frame in a given range"""

    def _get_split_time(target_time_frame):
        if target_time_frame == PER_FOUR_HOURS:
            return 6
        elif target_time_frame == PER_HOUR:
            return 24
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_step(target_time_frame):
        if target_time_frame == PER_FOUR_HOURS:
            return timedelta(hours=4)
        elif target_time_frame == PER_HOUR:
            return timedelta(hours=1)
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_init_date(candle, target_time_frame, start_hour):
        if target_time_frame == PER_FOUR_HOURS:
            if not start_hour:
                start_hour = 4
            return datetime.combine(candle.candle_date, time(start_hour, 0, 0))
        elif target_time_frame == PER_HOUR:
            if not start_hour:
                start_hour = 1
            return datetime.combine(candle.candle_date, time(start_hour, 0, 0))
        else:
            raise Exception(f'Target frame not found: {target_time_frame}')

    def _get_start_hour(start: datetime):
        try:
            return start.hour
        except Exception:
            return None

    def _split_candle(
        candle,
        target_time_frame,
        start,
        end,
    ):
        points = []
        split_times = _get_split_time(target_time_frame)
        step = _get_step(target_time_frame)
        start_hour = _get_start_hour(start)
        init_date = _get_init_date(
            candle,
            target_time_frame,
            start_hour,
        )
        price = candle.close_price

        if price:
            for idx in range(split_times):
                if end and init_date > end:
                    break
                points.append({
                    'date': init_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'price': price_to_show(price)
                })
                init_date = init_date + step
        return points

    all_points = []
    for candle in candles:
        points = _split_candle(
            candle,
            target_time_frame,
            start,
            end,
        )
        if points:
            all_points += points
    return all_points


def transform_candles(
    candles: List[Candle],
    target_time_frame: str,
    start=None,
    end=None,
) -> List[Any]:
    """Main service to transform a list of candles in a list of single dict
    data according to the target time frame in a given range"""

    if target_time_frame in [PER_HOUR, PER_HOUR, PER_FOUR_HOURS]:
        points = split_candles(
            candles,
            target_time_frame,
            start,
            end,
        )
        return points
    elif target_time_frame in [PER_DAY, PER_WEEK, PER_MONTH, PER_YEAR]:
        points = group_candles(
            candles,
            target_time_frame
        )
        return points
    else:
        raise Exception(f'Target frame not found: {target_time_frame}')


def transform_points(points: List[Point], target_time_frame: str) -> List[Any]:
    """Main service to transform a list of points in a list of single dict
    data according to the target time frame"""
    return group_points(points, target_time_frame)


def update_not_ending_asset_milestones_prices() -> None:
    """Service to update all the milestone that aren't finished
    and update their max and min values"""

    datetime_obj = datetime.now()
    datetime_obj = datetime_obj - timedelta(hours=1)
    datetime_reference = datetime_obj.strftime('%Y-%m-%d %H:00:00')
    points = Point.objects.select_related('chart').filter(
        point_date=datetime_reference
    )

    points_dict = {}
    asset_ids = []
    for point in points:
        asset_id = point.chart.asset_id
        points_dict[asset_id] = point.price
        asset_ids.append(asset_id)

    asset_milestones = AssetMilestone\
        .objects\
        .select_related('asset')\
        .filter(
            asset_id__in=asset_ids,
            milestone__end=None
        )

    for asset_milestone in asset_milestones:
        fill_asset_milestone(asset_milestone)


def get_percentage(asset_milestone: AssetMilestone) -> Optional[float]:
    """Get the percentage of return during the whole period of the
    milestone"""

    max_price = asset_milestone.max_price
    min_price = asset_milestone.min_price
    if max_price and min_price:
        if asset_milestone.max_price_date > asset_milestone.min_price_date:
            return get_performance(min_price, max_price)
        else:
            return get_performance(max_price, min_price)
    else:
        return None


def create_chart(
    asset: Asset,
    time_frame: str,
    chart_type: str,
) -> Chart:
    """Service to create a simple chart instance without any other
    relation"""

    chart = Chart(
        time_frame=time_frame,
        chart_type=chart_type,
        asset=asset,
    )
    chart = chart.save()
    return chart


def create_candle(
    chart: Chart,
    candle_date: datetime,
    open_price: Decimal,
    high_price: Decimal,
    low_price: Decimal,
    close_price: Decimal,
    volume: int,
    source: str,
    commit=True,
) -> Candle:
    """Service to create a simple candle instance without any other
    relation"""
    candle = Candle(
        chart=chart,
        candle_date=candle_date,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=volume,
        source=source,
    )
    if commit:
        candle = candle.save()
    return candle


def build_historical_data(hist: Any, chart: Chart) -> List[Candle]:
    """Create all the candles to an speific chart from
    a dataframe with all the historical data
    (THIS WORK WITH YAHOO HISTORICAL DATAFRAME)"""

    all_candles = []
    for timestamp, row in hist.iterrows():
        datetime_obj = timestamp.to_pydatetime()
        open_price = row[0]
        high_price = row[1]
        low_price = row[2]
        close_price = row[3]
        volume = row[4]
        try:
            volume = int(volume)
        except Exception:
            volume = 0

        candle = create_candle(
            chart=chart,
            candle_date=datetime_obj,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume,
            source="yahoo-finance",
            commit=False
        )
        all_candles.append(candle)
    Candle.objects.bulk_create(all_candles)
    return all_candles


@transaction.atomic
def clean_intersection_data(asset):
    """Get all the points that are in the candle territory and delete it"""

    last_candle = Candle.objects\
        .filter(chart__asset=asset)\
        .order_by('candle_date')\
        .last()
    last_candle_date = last_candle.candle_date
    Point.objects.filter(
        chart__asset=asset,
        point_date__date__lte=last_candle_date
    ).delete()


def get_best_time_frame_from_range(start, end):
    """Get the best suitable time frame from a given
    range of date"""
    delta = end - start
    days = delta.days
    if days <= 14:
        return PER_HOUR
    elif days <= 90:
        return PER_FOUR_HOURS
    elif days <= 365:
        return PER_DAY
    elif days <= 365*5:
        return PER_WEEK
    else:
        return PER_MONTH


def create_asset_milestone(
    asset: Asset,
    milestone: Milestone,
    deepest_down: float = None,
    biggest_up: float = None,
    total_performance: float = None,
) -> AssetMilestone:
    """Service to create a simple asset milestone instance without any other
    relation"""

    asset_milestone = AssetMilestone(
        asset=asset,
        milestone=milestone,
        deepest_down=deepest_down,
        biggest_up=biggest_up,
        total_performance=total_performance,
    )
    asset_milestone.save()
    return asset_milestone


def split_data_chart(data, point_data_to_split):
    """Divide the data chart in two parts, separated by
    a point data(the point data will be in the second part)"""

    first_part = []
    second_part = []
    for idx, point_data in enumerate(data):
        if point_data['date'] == point_data_to_split['date']:
            first_part = data[:idx]
            second_part = data[idx:]
            return {
                'first_part': first_part,
                'second_part': second_part,
            }
    return {
        'first_part': data,
        'second_part': [],
    }


def get_min_point_data(data_chart):
    min_point_data = None
    for point_data in data_chart:
        if not min_point_data:
            min_point_data = point_data

        if min_point_data['price'] > point_data['price']:
            min_point_data = point_data

    return min_point_data


def get_max_point_data(data_chart):
    max_point_data = None
    for point_data in data_chart:
        if not max_point_data:
            max_point_data = point_data

        if max_point_data['price'] < point_data['price']:
            max_point_data = point_data

    return max_point_data


def get_max_min_from_data_chart(data_chart):
    """Get the min and max points and dates
    of the given data chart"""

    min_point_data = None
    max_point_data = None
    for point_data in data_chart:
        if not min_point_data:
            min_point_data = point_data
        if not max_point_data:
            max_point_data = point_data

        if min_point_data['price'] > point_data['price']:
            min_point_data = point_data

        if max_point_data['price'] < point_data['price']:
            max_point_data = point_data

    return {
        'max_point_data': max_point_data,
        'min_point_data': min_point_data
    }


def fill_asset_milestone(asset_milestone: AssetMilestone) -> AssetMilestone:
    """fill or re fill an asset milestones with the proper values"""
    from apps.chart.factory import GenerateChartFactory

    start = asset_milestone.milestone.start
    end = asset_milestone.milestone.end
    if not end:
        end = datetime.today()

    asset_milestone_days = (end - start).days

    first_date = get_first_date_with_data(asset_milestone.asset)
    last_date = get_last_date_with_data(asset_milestone.asset)

    if last_date is None or first_date is None:
        return asset_milestone

    end_diff = (last_date - end).days
    start_diff = (start - first_date).days

    allowed_days = (asset_milestone_days*0.1)*-1

    if end_diff < allowed_days or start_diff < allowed_days:
        return asset_milestone

    time_frame = get_best_time_frame_from_range(start, end)
    params = {
        'symbol': asset_milestone.asset.symbol,
        'asset_type': asset_milestone.asset.asset_type,
        'start': start,
        'end': end,
        'time_frame': time_frame
    }
    data = GenerateChartFactory.generate_chart(**params)
    if data:
        deepest_down = get_deepest_down(data)
        biggest_up = get_biggest_up(data)
        total_performance = get_total_performance(data)
        asset_milestone.deepest_down = deepest_down
        asset_milestone.biggest_up = biggest_up
        asset_milestone.total_performance = total_performance
        asset_milestone.save()
    return asset_milestone


def build_asset_milestones(asset):
    """Try to create all milestones of the given asset
    and fill them"""

    milestones = Milestone.objects.all()
    for milestone in milestones:
        asset_milestone = AssetMilestone.objects\
            .filter(asset=asset, milestone=milestone)\
            .first()
        if not asset_milestone:
            asset_milestone = create_asset_milestone(
                asset=asset,
                milestone=milestone
            )
        fill_asset_milestone(asset_milestone)


def get_suitable_asset_milestone_chart_data(asset_milestone) -> List:
    """Return the chart data of the asset milestone in the
    most suitable time frame"""
    from apps.chart.factory import GenerateChartFactory

    end = datetime.today()
    if asset_milestone.milestone.end:
        end = asset_milestone.milestone.end

    start = asset_milestone.milestone.start

    best_time_frame = get_best_time_frame_from_range(start=start, end=end)
    asset = asset_milestone.asset

    params = {
        'symbol': asset.symbol,
        'asset_type': asset.asset_type,
        'time_frame': best_time_frame,
        'start': start,
        'end': end,
    }
    return GenerateChartFactory.generate_chart(**params)


def get_deepest_down(data):
    """Get the percentage with the biggest down of the given data chart"""

    data_detail = get_max_min_from_data_chart(data)

    max_point_data = data_detail['max_point_data']
    parts = split_data_chart(data, max_point_data)
    min_after_max_point = get_min_point_data(parts['second_part'])

    deep_canididate_1 = None
    if min_after_max_point:
        deep_canididate_1 = get_performance(
            max_point_data['price'],
            min_after_max_point['price']
        )

    min_point_data = data_detail['min_point_data']
    parts = split_data_chart(data, min_point_data)
    max_before_min_point = get_max_point_data(parts['first_part'])

    deep_canididate_2 = None
    if max_before_min_point:
        deep_canididate_2 = get_performance(
            max_before_min_point['price'],
            min_point_data['price']
        )

    if deep_canididate_1 is not None and deep_canididate_2 is not None:
        return min(deep_canididate_1, deep_canididate_2, 0)
    else:
        if deep_canididate_1 is None and deep_canididate_2 is not None:
            return min(deep_canididate_2, 0)

        if deep_canididate_2 is None and deep_canididate_1 is not None:
            return min(deep_canididate_1, 0)

    return None


def get_biggest_up(data):
    """Get the percentage with the biggest down of the given data chart"""

    data_detail = get_max_min_from_data_chart(data)

    max_point_data = data_detail['max_point_data']
    parts = split_data_chart(data, max_point_data)
    min_before_max_point = get_min_point_data(parts['first_part'])

    big_canididate_1 = None
    if min_before_max_point:
        big_canididate_1 = get_performance(
            min_before_max_point['price'],
            max_point_data['price'],
        )

    min_point_data = data_detail['min_point_data']
    parts = split_data_chart(data, min_point_data)
    max_after_min_point = get_max_point_data(parts['second_part'])

    big_canididate_2 = None
    if max_after_min_point:
        big_canididate_2 = get_performance(
            min_point_data['price'],
            max_after_min_point['price'],
        )

    if big_canididate_1 is not None and big_canididate_2 is not None:
        return max(big_canididate_1, big_canididate_2, 0)
    else:
        if big_canididate_1 is None and big_canididate_2 is not None:
            return max(big_canididate_2, 0)

        if big_canididate_2 is None and big_canididate_1 is not None:
            return max(big_canididate_1, 0)

    return None


def get_total_performance(data):
    """Get the percentage performance of the total chart data"""

    first_point = data[0]
    last_point = data[-1]
    performance = get_performance(
        first_point['price'],
        last_point['price'],
    )
    return performance


def create_milestone_table():
    from apps.asset.services import get_sector_and_industry

    assets = Asset.objects.all()\
        .prefetch_related(
            'assetmilestone_set',
            'assetdetail_set'
        )

    results = []
    for asset in assets:
        asset_milestones = asset.assetmilestone_set\
            .select_related('milestone')\
            .all()\
            .order_by('milestone__start')
        sector, industry = get_sector_and_industry(asset)
        data = {
            'id': asset.id,
            'name': asset.name,
            'symbol': asset.symbol,
            'asset_type': asset.asset_type,
            'sector': sector,
            'industry': industry,
            'healthy': asset.health,
        }
        for asset_milestone in asset_milestones:
            deepest_down = asset_milestone.deepest_down
            biggest_up = asset_milestone.biggest_up

            key = f'down_{asset_milestone.milestone.slug}'
            data[key] = deepest_down

            key = f'up_{asset_milestone.milestone.slug}'
            data[key] = biggest_up

        results.append(data)

    rows = []
    for data in results:
        row = []
        for key in data:
            row.append(data[key])
        rows.append(row)
    return rows


def get_first_date_with_data(asset):
    """Get the first date with data of an asset"""
    first_candle = Candle.objects.filter(
        chart__asset=asset
    ).order_by('candle_date').first()

    first_point = Point.objects.filter(
        chart__asset=asset
    ).order_by('point_date').first()

    date1 = None
    if first_candle:
        date1 = first_candle.candle_date

    date2 = None
    if first_point:
        date2 = first_point.point_date

    if date1 is None:
        return date2

    if date2 is None:
        return date1

    return min(date1, date2)


def get_last_date_with_data(asset):
    """Get the last date with data of an asset"""
    last_candle = Candle.objects.filter(
        chart__asset=asset
    ).order_by('candle_date').last()

    last_point = Point.objects.filter(
        chart__asset=asset
    ).order_by('point_date').last()

    date1 = None
    if last_candle:
        date1 = last_candle.candle_date

    date2 = None
    if last_point:
        date2 = last_point.point_date

    if date1 is None:
        return date2

    if date2 is None:
        return date1

    return max(date1, date2)


def get_all_chart_data_by_day(asset):
    """Get all the chart data of the given asset by day"""
    from apps.chart.factory import GenerateChartFactory

    start = get_first_date_with_data(asset)
    end = get_last_date_with_data(asset)

    params = {
        'symbol': asset.symbol,
        'asset_type': asset.asset_type,
        'time_frame': '1d',
        'start': start,
        'end': end,
    }
    return GenerateChartFactory.generate_chart(**params)


def chart_data_to_dict(data: List):
    """Transform data chart in a dict"""
    data_dict = {}
    for data_point in data:
        data_dict[data_point['date']] = data_point['price']
    return data_dict
