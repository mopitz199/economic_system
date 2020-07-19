import pytest
from decimal import Decimal
from model_bakery import baker
from unittest import mock

from apps.asset.services import (
    get_yahoo_symbol,
    get_current_asset_price,
    create_slug,
    create_asset,
    create_asset_detail,
    generate_asset_milestone_correlation,
)
from apps.asset.models import Asset
from apps.chart.models import Point, AssetMilestoneComparision
from constants import CRYPTO_ASSET_TYPE, CURRENCY_ASSET_TYPE


def test_get_yahoo_symbol_stock():
    yahoo_symbol = get_yahoo_symbol('ABC', 'stocks')
    assert yahoo_symbol == 'ABC'


def test_get_yahoo_symbol_crypto():
    yahoo_symbol = get_yahoo_symbol('ABC', 'cryptos')
    assert yahoo_symbol == 'ABC-USD'


def test_get_yahoo_symbol_currency():
    yahoo_symbol = get_yahoo_symbol('ABC', 'currencies')
    assert yahoo_symbol == 'ABC=X'


def test_get_yahoo_symbol_etf():
    yahoo_symbol = get_yahoo_symbol('ABC', 'etf')
    assert yahoo_symbol == 'ABC'


def test_get_yahoo_symbol_future():
    yahoo_symbol = get_yahoo_symbol('ABC', 'futures')
    assert yahoo_symbol == 'ABC=F'


@pytest.mark.django_db
def test_get_current_asset_price_1():
    asset = baker.make('Asset')
    chart = baker.make('Chart', asset=asset)
    point = baker.make(
        'Point',
        chart=chart,
        price=Decimal(10)
    )
    current_price = get_current_asset_price(asset)
    assert current_price == Decimal(10)


@pytest.mark.django_db
def test_get_current_asset_price_2():
    asset = baker.make('Asset')
    chart = baker.make('Chart', asset=asset)
    point = baker.make(
        'Point',
        chart=chart,
        price=Decimal(10)
    )
    point = baker.make(
        'Point',
        chart=chart,
        price=Decimal(12)
    )
    current_price = get_current_asset_price(asset)
    assert current_price == Decimal(12)


@pytest.mark.django_db
def test_get_current_asset_price_3():
    asset = baker.make('Asset')
    chart = baker.make('Chart', asset=asset)
    current_price = get_current_asset_price(asset)
    assert current_price is None


@pytest.mark.django_db
def test_create_slug():
    slug = create_slug('FRF DAS  ')
    assert slug == 'frf-das'


@pytest.mark.django_db
def test_create_asset():
    asset = create_asset('BTC', 'bitcoin', 'cryptos')
    assert asset.symbol == 'BTC'
    assert asset.name == 'bitcoin'
    assert asset.asset_type == 'cryptos'
    assert asset.slug == 'bitcoin'


@pytest.mark.django_db
def test_create_asset_detail():
    asset = baker.make('Asset')
    asset_detail = create_asset_detail(
        asset=asset,
        name='anything',
        data={'name': 'bob'}
    )
    assert asset_detail.asset == asset
    assert asset_detail.name == 'anything'
    assert asset_detail.data == {'name': 'bob'}


@pytest.mark.django_db
@mock.patch('apps.asset.services.get_correlation_between_to_data_charts')
@mock.patch('apps.asset.services.generate_all_asset_milestone_charts')
def test_generate_asset_milestone_correlation(
    generate_all_asset_milestone_charts_mock,
    get_correlation_between_to_data_charts_mock,
):

    milestone = baker.make('Milestone')

    asset_milestones = []
    for i in range(4):
        asset_milestone = baker.make('AssetMilestone', milestone=milestone)
        asset_milestones.append(asset_milestone)

    return_value = {}
    for asset_milestone in asset_milestones:
        return_value[asset_milestone.id] = []
    generate_all_asset_milestone_charts_mock.return_value = return_value

    initial_correlations = [1, 2, 3, 4, 5, 6]
    get_correlation_between_to_data_charts_mock\
        .side_effect = initial_correlations

    generate_asset_milestone_correlation(milestone)

    comparisions = AssetMilestoneComparision.objects.all()

    correlations = comparisions.order_by(
        'correlation'
    ).values_list(
        'correlation',
        flat=True
    )
    correlations = list(correlations)

    assert correlations == initial_correlations
    assert comparisions.count() == 6
