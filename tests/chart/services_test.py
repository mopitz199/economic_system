import pytest

from datetime import datetime, timedelta
from decimal import Decimal
from freezegun import freeze_time
from model_bakery import baker
from unittest import mock

from apps.chart.constants import (
    PER_HOUR,
    PER_DAY,
    PER_FOUR_HOURS,
    PER_WEEK,
    PER_MONTH,
    POINT_CHART_TYPE,
    CANDLE_CHART_TYPE,
)

from apps.chart.services import (
    transform_points,
    update_not_ending_asset_milestones_prices,
    transform_candles,
    get_best_time_frame_from_range,
    clean_intersection_data,
    fill_asset_milestone,
    get_deepest_down,
    get_biggest_up,
    get_first_date_with_data,
    get_last_date_with_data,
)

from apps.chart.models import AssetMilestone, Point


@pytest.fixture
def day_point_chart(db):
    chart = baker.make(
        'Chart',
        time_frame=PER_DAY,
        chart_type=POINT_CHART_TYPE,
    )

    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    for i in range(1):
        baker.make(
            'Point',
            point_date=aux_datetime,
            chart=chart,
            price=i
        )
        aux_datetime += timedelta(days=1)
    return chart


@pytest.fixture
def day_candle_chart(db):
    chart = baker.make(
        'Chart',
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )

    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    for i in range(1):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=chart,
            close_price=i,
        )
        aux_datetime += timedelta(days=1)
    return chart


@pytest.mark.django_db
def test_point_services_transform_day_1():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(24):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [{'date': '2020-01-01', 'price': 23}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_2():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(30):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [{'date': '2020-01-01', 'price': 23}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_3():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(20):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [{'date': '2020-01-01', 'price': 19}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_4():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(10):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = []
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_5():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(48):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [
        {'date': '2020-01-01', 'price': 23},
        {'date': '2020-01-02', 'price': 47},
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_6():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(46):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [
        {'date': '2020-01-01', 'price': 23},
        {'date': '2020-01-02', 'price': 45},
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_7():
    aux_datetime = datetime(2020, 1, 1, 10, 0, 0)
    points = []
    for i in range(27):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = []
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_day_8():
    aux_datetime = datetime(2020, 1, 1, 2, 0, 0)
    points = []
    for i in range(27):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_DAY)
    expected = [{'date': '2020-01-01', 'price': 22}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_1():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(6):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [{'date': '2020-01-01 04:00:00', 'price': 3}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_2():
    aux_datetime = datetime(2020, 1, 1, 3, 0, 0)
    points = []
    for i in range(6):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [{'date': '2020-01-01 06:00:00', 'price': 3}]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_3():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(3):
        point = baker.make('Point', point_date=aux_datetime, price=i)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = []
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_4():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    points = []
    for i in range(24):
        point = baker.make('Point', point_date=aux_datetime, price=i+1)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [
        {'date': '2020-01-01 03:00:00', 'price': 4},
        {'date': '2020-01-01 07:00:00', 'price': 8},
        {'date': '2020-01-01 11:00:00', 'price': 12},
        {'date': '2020-01-01 15:00:00', 'price': 16},
        {'date': '2020-01-01 19:00:00', 'price': 20},
        {'date': '2020-01-01 23:00:00', 'price': 24}
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_5():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    points = []
    for i in range(25):
        point = baker.make('Point', point_date=aux_datetime, price=i+1)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [
        {'date': '2020-01-01 03:00:00', 'price': 4},
        {'date': '2020-01-01 07:00:00', 'price': 8},
        {'date': '2020-01-01 11:00:00', 'price': 12},
        {'date': '2020-01-01 15:00:00', 'price': 16},
        {'date': '2020-01-01 19:00:00', 'price': 20},
        {'date': '2020-01-01 23:00:00', 'price': 24}
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_6():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(25):
        point = baker.make('Point', point_date=aux_datetime, price=i+1)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [
        {'date': '2020-01-01 04:00:00', 'price': 4},
        {'date': '2020-01-01 08:00:00', 'price': 8},
        {'date': '2020-01-01 12:00:00', 'price': 12},
        {'date': '2020-01-01 16:00:00', 'price': 16},
        {'date': '2020-01-01 20:00:00', 'price': 20},
        {'date': '2020-01-02 00:00:00', 'price': 24}
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_four_hours_7():
    aux_datetime = datetime(2020, 1, 1, 18, 0, 0)
    points = []
    for i in range(26):
        point = baker.make('Point', point_date=aux_datetime, price=i+1)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_FOUR_HOURS)
    expected = [
        {'date': '2020-01-01 21:00:00', 'price': 4},
        {'date': '2020-01-02 01:00:00', 'price': 8},
        {'date': '2020-01-02 05:00:00', 'price': 12},
        {'date': '2020-01-02 09:00:00', 'price': 16},
        {'date': '2020-01-02 13:00:00', 'price': 20},
        {'date': '2020-01-02 17:00:00', 'price': 24}
    ]
    assert data == expected


@pytest.mark.django_db
def test_point_services_transform_hours_1():
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    points = []
    for i in range(1):
        point = baker.make('Point', point_date=aux_datetime, price=i+1)
        points.append(point)
        aux_datetime = aux_datetime + timedelta(hours=1)

    data = transform_points(points, PER_HOUR)
    expected = [{'date': '2020-01-01 01:00:00', 'price': 1}]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_week_1():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(7):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_WEEK)
    expected = [{'date': '2020-01-05', 'price': 5}]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_week_2():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(10):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_WEEK)
    expected = [
        {'date': '2020-01-05', 'price': 5},
        {'date': '2020-01-12', 'price': 10}
    ]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_week_3():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(12):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_WEEK)
    expected = [
        {'date': '2020-01-05', 'price': 5},
        {'date': '2020-01-12', 'price': 12}
    ]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_week_4():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(9):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_WEEK)
    expected = [
        {'date': '2020-01-05', 'price': 5}
    ]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_hour_1():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(1):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_HOUR)

    expected = [
        {'date': '2020-01-01 01:00:00', 'price': 1},
        {'date': '2020-01-01 02:00:00', 'price': 1},
        {'date': '2020-01-01 03:00:00', 'price': 1},
        {'date': '2020-01-01 04:00:00', 'price': 1},
        {'date': '2020-01-01 05:00:00', 'price': 1},
        {'date': '2020-01-01 06:00:00', 'price': 1},
        {'date': '2020-01-01 07:00:00', 'price': 1},
        {'date': '2020-01-01 08:00:00', 'price': 1},
        {'date': '2020-01-01 09:00:00', 'price': 1},
        {'date': '2020-01-01 10:00:00', 'price': 1},
        {'date': '2020-01-01 11:00:00', 'price': 1},
        {'date': '2020-01-01 12:00:00', 'price': 1},
        {'date': '2020-01-01 13:00:00', 'price': 1},
        {'date': '2020-01-01 14:00:00', 'price': 1},
        {'date': '2020-01-01 15:00:00', 'price': 1},
        {'date': '2020-01-01 16:00:00', 'price': 1},
        {'date': '2020-01-01 17:00:00', 'price': 1},
        {'date': '2020-01-01 18:00:00', 'price': 1},
        {'date': '2020-01-01 19:00:00', 'price': 1},
        {'date': '2020-01-01 20:00:00', 'price': 1},
        {'date': '2020-01-01 21:00:00', 'price': 1},
        {'date': '2020-01-01 22:00:00', 'price': 1},
        {'date': '2020-01-01 23:00:00', 'price': 1},
        {'date': '2020-01-02 00:00:00', 'price': 1}
    ]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_four_hour_1():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(1):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_FOUR_HOURS)

    expected = [
        {'date': '2020-01-01 04:00:00', 'price': 1},
        {'date': '2020-01-01 08:00:00', 'price': 1},
        {'date': '2020-01-01 12:00:00', 'price': 1},
        {'date': '2020-01-01 16:00:00', 'price': 1},
        {'date': '2020-01-01 20:00:00', 'price': 1},
        {'date': '2020-01-02 00:00:00', 'price': 1},
    ]
    assert data == expected


@pytest.mark.django_db
def test_candle_services_transform_day_1():
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    candles = []
    for i in range(1):
        candle = baker.make(
            'Candle',
            candle_date=aux_datetime,
            close_price=i+1
        )
        candles.append(candle)
        aux_datetime = aux_datetime + timedelta(days=1)

    data = transform_candles(candles, PER_DAY)

    expected = [
        {'date': '2020-01-01', 'price': 1},
    ]
    assert data == expected


def test_get_best_time_frame_from_range_per_hour():
    init_date = datetime(2020, 1, 1)
    ending_date = datetime(2020, 1, 1)
    time_frame = get_best_time_frame_from_range(init_date, ending_date)
    assert time_frame == PER_HOUR


def test_get_best_time_frame_from_range_per_four_hour():
    init_date = datetime(2020, 1, 1)
    ending_date = datetime(2020, 2, 20)
    time_frame = get_best_time_frame_from_range(init_date, ending_date)
    assert time_frame == PER_FOUR_HOURS


def test_get_best_time_frame_from_range_per_day():
    init_date = datetime(2020, 1, 1)
    ending_date = datetime(2020, 12, 20)
    time_frame = get_best_time_frame_from_range(init_date, ending_date)
    assert time_frame == PER_DAY


def test_get_best_time_frame_from_range_per_week():
    init_date = datetime(2020, 1, 1)
    ending_date = datetime(2024, 2, 20)
    time_frame = get_best_time_frame_from_range(init_date, ending_date)
    assert time_frame == PER_WEEK


def test_get_best_time_frame_from_range_per_month():
    init_date = datetime(2020, 1, 1)
    ending_date = datetime(2030, 2, 20)
    time_frame = get_best_time_frame_from_range(init_date, ending_date)
    assert time_frame == PER_MONTH


@pytest.mark.django_db
def test_clean_intersection_data():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 1, 1, 0, 0, 0)
    baker.make(
        'Candle',
        candle_date=aux_datetime,
        chart=day_chart,
        close_price=10,
    )

    hour_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_HOUR,
        chart_type=POINT_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 1, 1, 10, 0, 0)
    for i in range(20):
        baker.make(
            'Point',
            point_date=aux_datetime,
            chart=hour_chart,
            price=i
        )
        aux_datetime += timedelta(hours=1)

    clean_intersection_data(asset)

    assert Point.objects.filter(chart__asset=asset).count() == 6


@pytest.mark.django_db
def test_fill_asset_milestone():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    for i in range(20):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=day_chart,
            close_price=i+1,
        )
        aux_datetime += timedelta(days=1)
    milestone = baker.make(
        'Milestone',
        start=datetime(2020, 1, 5),
        end=datetime(2020, 1, 10),
    )
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
    )
    updated_asset_milestone = fill_asset_milestone(asset_milestone)
    assert (
        updated_asset_milestone.id == asset_milestone.id and
        updated_asset_milestone.deepest_down == 0 and
        updated_asset_milestone.biggest_up == 80 and
        updated_asset_milestone.total_performance == 80
    )


@pytest.mark.django_db
def test_fill_asset_milestone_empty():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 2, 1, 1, 0, 0)
    for i in range(40):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=day_chart,
            close_price=i+1,
        )
        aux_datetime += timedelta(days=1)
    milestone = baker.make(
        'Milestone',
        start=datetime(2020, 1, 1),
        end=datetime(2020, 2, 10),
    )
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
    )
    updated_asset_milestone = fill_asset_milestone(asset_milestone)
    assert (
        updated_asset_milestone.id == asset_milestone.id and
        updated_asset_milestone.deepest_down is None and
        updated_asset_milestone.biggest_up is None and
        updated_asset_milestone.total_performance is None
    )


@pytest.mark.django_db
def test_fill_asset_milestone_empty_2():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 2, 1, 1, 0, 0)
    for i in range(10):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=day_chart,
            close_price=i+1,
        )
        aux_datetime += timedelta(days=1)
    milestone = baker.make(
        'Milestone',
        start=datetime(2020, 2, 2),
        end=datetime(2020, 4, 1),
    )
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
    )
    updated_asset_milestone = fill_asset_milestone(asset_milestone)
    assert (
        updated_asset_milestone.id == asset_milestone.id and
        updated_asset_milestone.deepest_down is None and
        updated_asset_milestone.biggest_up is None and
        updated_asset_milestone.total_performance is None
    )


@pytest.mark.django_db
@freeze_time("2020-3-7")
def test_fill_asset_milestone_empty_3():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    for i in range(20):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=day_chart,
            close_price=i+1,
        )
        aux_datetime += timedelta(days=1)
    milestone = baker.make(
        'Milestone',
        start=datetime(2020, 1, 5),
        end=None,
    )
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
    )
    updated_asset_milestone = fill_asset_milestone(asset_milestone)
    assert (
        updated_asset_milestone.id == asset_milestone.id and
        updated_asset_milestone.deepest_down is None and
        updated_asset_milestone.biggest_up is None and
        updated_asset_milestone.total_performance is None
    )


@pytest.mark.django_db
@freeze_time("2020-1-7")
def test_fill_asset_milestone_none_end():
    asset = baker.make('Asset')
    day_chart = baker.make(
        'Chart',
        asset=asset,
        time_frame=PER_DAY,
        chart_type=CANDLE_CHART_TYPE,
    )
    aux_datetime = datetime(2020, 1, 1, 1, 0, 0)
    for i in range(20):
        baker.make(
            'Candle',
            candle_date=aux_datetime,
            chart=day_chart,
            close_price=i+1,
        )
        aux_datetime += timedelta(days=1)
    milestone = baker.make(
        'Milestone',
        start=datetime(2020, 1, 5),
        end=None,
    )
    asset_milestone = baker.make(
        'AssetMilestone',
        asset=asset,
        milestone=milestone,
    )
    updated_asset_milestone = fill_asset_milestone(asset_milestone)
    assert (
        updated_asset_milestone.id == asset_milestone.id and
        updated_asset_milestone.deepest_down == 0 and
        updated_asset_milestone.biggest_up == 20 and
        updated_asset_milestone.total_performance == 20
    )


def test_get_deepest_down_1():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(8)},
        {'date': '2020-1-3', 'price': Decimal(6)},
        {'date': '2020-1-4', 'price': Decimal(4)},
        {'date': '2020-1-5', 'price': Decimal(2)},
        {'date': '2020-1-6', 'price': Decimal(30)},
        {'date': '2020-1-7', 'price': Decimal(27)},
        {'date': '2020-1-9', 'price': Decimal(28)},
        {'date': '2020-1-10', 'price': Decimal(26)},
        {'date': '2020-1-11', 'price': Decimal(24)},
    ]
    deepest_down = get_deepest_down(data)
    assert deepest_down == -80


def test_get_deepest_down_2():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(8)},
        {'date': '2020-1-3', 'price': Decimal(8)},
        {'date': '2020-1-4', 'price': Decimal(8)},
        {'date': '2020-1-5', 'price': Decimal(8)},
        {'date': '2020-1-6', 'price': Decimal(30)},
        {'date': '2020-1-7', 'price': Decimal(27)},
        {'date': '2020-1-9', 'price': Decimal(28)},
        {'date': '2020-1-10', 'price': Decimal(26)},
        {'date': '2020-1-11', 'price': Decimal(24)},
    ]
    deepest_down = get_deepest_down(data)
    assert deepest_down == -20


def test_get_deepest_down_3():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(12)},
        {'date': '2020-1-3', 'price': Decimal(14)},
        {'date': '2020-1-4', 'price': Decimal(16)},
        {'date': '2020-1-5', 'price': Decimal(18)},
        {'date': '2020-1-6', 'price': Decimal(20)},
    ]
    deepest_down = get_deepest_down(data)
    assert deepest_down == 0


def test_get_deepest_down_4():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(9)},
        {'date': '2020-1-3', 'price': Decimal(14)},
        {'date': '2020-1-4', 'price': Decimal(16)},
        {'date': '2020-1-5', 'price': Decimal(18)},
        {'date': '2020-1-6', 'price': Decimal(20)},
    ]
    deepest_down = get_deepest_down(data)
    assert deepest_down == -10


def test_get_biggest_up_1():
    data = [
        {'date': '2020-1-1', 'price': Decimal(2)},
        {'date': '2020-1-2', 'price': Decimal(9)},
        {'date': '2020-1-3', 'price': Decimal(15)},
        {'date': '2020-1-4', 'price': Decimal(13)},
        {'date': '2020-1-5', 'price': Decimal(8)},
        {'date': '2020-1-6', 'price': Decimal(10)},
        {'date': '2020-1-7', 'price': Decimal(12)},
        {'date': '2020-1-8', 'price': Decimal(15)},
    ]
    biggest_up = get_biggest_up(data)
    assert biggest_up == 650


def test_get_biggest_up_2():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(8)},
        {'date': '2020-1-3', 'price': Decimal(6)},
        {'date': '2020-1-4', 'price': Decimal(4)},
    ]
    biggest_up = get_biggest_up(data)
    assert biggest_up == 0


def test_get_biggest_up_3():
    data = [
        {'date': '2020-1-1', 'price': Decimal(10)},
        {'date': '2020-1-2', 'price': Decimal(9)},
        {'date': '2020-1-3', 'price': Decimal(15)},
        {'date': '2020-1-4', 'price': Decimal(13)},
        {'date': '2020-1-5', 'price': Decimal(8)},
        {'date': '2020-1-6', 'price': Decimal(10)},
        {'date': '2020-1-7', 'price': Decimal(12)},
        {'date': '2020-1-8', 'price': Decimal(15)},
        {'date': '2020-1-9', 'price': Decimal(8)},
        {'date': '2020-1-10', 'price': Decimal(20)},
        {'date': '2020-1-11', 'price': Decimal(25)}
    ]
    biggest_up = get_biggest_up(data)
    assert biggest_up == 212.5


@pytest.mark.django_db
def test_get_first_date_with_data_1():
    asset = baker.make('Asset')
    candle_chart = baker.make('Chart', asset=asset)
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 1))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    response = get_first_date_with_data(asset)
    assert response == datetime(2020, 1, 1)


@pytest.mark.django_db
def test_get_first_date_with_data_2():
    asset = baker.make('Asset')
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    response = get_first_date_with_data(asset)
    assert response == datetime(2020, 1, 2)


@pytest.mark.django_db
def test_get_first_date_with_data_3():
    asset = baker.make('Asset')
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 4))
    response = get_first_date_with_data(asset)
    assert response == datetime(2020, 1, 2)


@pytest.mark.django_db
def test_get_first_date_with_data_4():
    asset = baker.make('Asset')
    candle_chart = baker.make('Chart', asset=asset)
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 1))
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 3))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 4))
    response = get_first_date_with_data(asset)
    assert response == datetime(2020, 1, 1)


@pytest.mark.django_db
def test_get_first_date_with_data_5():
    asset = baker.make('Asset')
    response = get_first_date_with_data(asset)
    assert response is None


@pytest.mark.django_db
def test_get_last_date_with_data_1():
    asset = baker.make('Asset')
    candle_chart = baker.make('Chart', asset=asset)
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 1))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    response = get_last_date_with_data(asset)
    assert response == datetime(2020, 1, 2)


@pytest.mark.django_db
def test_get_last_date_with_data_2():
    asset = baker.make('Asset')
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    response = get_last_date_with_data(asset)
    assert response == datetime(2020, 1, 2)


@pytest.mark.django_db
def test_get_last_date_with_data_3():
    asset = baker.make('Asset')
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 4))
    response = get_last_date_with_data(asset)
    assert response == datetime(2020, 1, 4)


@pytest.mark.django_db
def test_get_last_date_with_data_4():
    asset = baker.make('Asset')
    candle_chart = baker.make('Chart', asset=asset)
    point_chart = baker.make('Chart', asset=asset)
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 1))
    baker.make('Candle', chart=candle_chart, candle_date=datetime(2020, 1, 3))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 2))
    baker.make('Point', chart=point_chart, point_date=datetime(2020, 1, 4))
    response = get_last_date_with_data(asset)
    assert response == datetime(2020, 1, 4)


@pytest.mark.django_db
def test_get_last_date_with_data_5():
    asset = baker.make('Asset')
    response = get_last_date_with_data(asset)
    assert response is None
