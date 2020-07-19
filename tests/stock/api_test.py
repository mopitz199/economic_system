from datetime import datetime
from decimal import Decimal
from unittest import mock

from freezegun import freeze_time
from model_bakery import baker
import pytest

from apps.stock.api import CreateMultipleDilutedEPS, GetPER
from apps.stock.models import DilutedEPS


@pytest.fixture
def asset1(db):
    asset = baker.make(
        'Asset',
        asset_type='stocks',
        symbol='AAPL'
    )
    return asset


@pytest.fixture
def asset2(db):
    asset = baker.make(
        'Asset',
        asset_type='stocks',
        symbol='CCL'
    )
    return asset


@pytest.fixture
def asset1_diluted_eps(asset1):
    data = [
        (datetime(2019, 1, 1).date(), 2),
        (datetime(2019, 4, 1).date(), 4),
        (datetime(2019, 7, 1).date(), 6),
    ]
    response = []
    for d in data:
        diluted_eps = baker.make(
            'DilutedEPS',
            asset=asset1,
            value=d[1],
            diluted_eps_date=d[0]
        )
        response.append(diluted_eps)
    return response


def test_create_multiple_diluted_eps_success_1(asset1):
    request = mock.Mock()
    request.data = {
        'diluted_eps_data': [
            {
                'symbol': asset1.symbol,
                'diluted_eps_date': '2020-1-1',
                'value': 10.3
            }
        ]
    }
    view = CreateMultipleDilutedEPS()
    view.post(request)

    assert DilutedEPS.objects.all().count() == 1

    diluted_eps = DilutedEPS.objects.all().first()
    assert diluted_eps.asset == asset1
    assert diluted_eps.diluted_eps_date == datetime(2020, 1, 1).date()
    assert float(diluted_eps.value) == float(Decimal(10.3))


@pytest.mark.django_db
def test_create_multiple_diluted_eps_empty():
    request = mock.Mock()
    request.data = {
        'diluted_eps_data': [
            {
                'symbol': 'NO_EXIST',
                'diluted_eps_date': '2020-1-1',
                'value': 10.3
            }
        ]
    }
    view = CreateMultipleDilutedEPS()
    view.post(request)
    assert DilutedEPS.objects.all().count() == 0


def test_create_multiple_diluted_eps_success_2(asset1, asset2):
    request = mock.Mock()
    request.data = {
        'diluted_eps_data': [
            {
                'symbol': asset1.symbol,
                'diluted_eps_date': '2020-1-1',
                'value': 10.3
            },
            {
                'symbol': asset2.symbol,
                'diluted_eps_date': '2020-1-1',
                'value': 10.3
            }
        ]
    }
    view = CreateMultipleDilutedEPS()
    view.post(request)
    assert DilutedEPS.objects.all().count() == 2


@freeze_time("2019-08-01")
@mock.patch('apps.stock.api.GenerateChartFactory.generate_chart')
def test_get_per(generate_chart, asset1, asset1_diluted_eps):
    generate_chart.return_value = [
        {
            'date': datetime(2019, 1, 1).date(),
            'price': 10,
        },
        {
            'date': datetime(2019, 2, 1).date(),
            'price': 12,
        },
        {
            'date': datetime(2019, 3, 1).date(),
            'price': 14,
        },
        {
            'date': datetime(2019, 4, 1).date(),
            'price': 16,
        },
        {
            'date': datetime(2019, 5, 1).date(),
            'price': 18,
        }
    ]
    request = mock.Mock()
    request.query_params = {
        'symbol': 'AAPL'
    }
    view = GetPER()
    repsonse = view.get(request)

    expected = {
        'results': [
            {'date': datetime(2019, 1, 1).date(), 'per': Decimal('5')},
            {'date': datetime(2019, 2, 1).date(), 'per': Decimal('6')},
            {'date': datetime(2019, 3, 1).date(), 'per': Decimal('7')},
            {'date': datetime(2019, 4, 1).date(), 'per': Decimal('4')},
            {'date': datetime(2019, 5, 1).date(), 'per': Decimal('4.5')}
        ]
    }
    assert repsonse.data == expected
