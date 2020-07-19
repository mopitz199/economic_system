import pytest
from decimal import Decimal
from model_bakery import baker
from unittest import mock

from apps.portfolio.services import (
    get_asset_portfolio_earning,
    get_asset_portfolio_best_performance,
    get_asset_portfolio_worst_performance,
    get_asset_portfolio_invested_amount,
    get_asset_portfolio_performance,
    get_optmization_portfolios,
    build_data_to_apply_optimization,
)
from apps.asset.models import Asset
from apps.chart.models import Point
from constants import CRYPTO_ASSET_TYPE, CURRENCY_ASSET_TYPE


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_performance_1(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(100)

    asset = baker.make('Asset')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(10),
    )

    performance = get_asset_portfolio_performance(asset_portfolio)
    assert performance == 900


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_performance_2(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(20)

    asset = baker.make('Asset')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(10),
    )

    performance = get_asset_portfolio_performance(asset_portfolio)
    assert performance == 100


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_performance_3(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(1)

    asset = baker.make('Asset')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(100),
    )

    performance = get_asset_portfolio_performance(asset_portfolio)
    assert performance == -99


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_performance_4(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(0.1)

    asset = baker.make('Asset')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(100),
    )

    performance = get_asset_portfolio_performance(asset_portfolio)
    assert performance == -99.9


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_profit(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(10)
    asset = baker.make('Asset', currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(7),
        quantity=1,
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning == Decimal(3)


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_lose(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(10)
    asset = baker.make('Asset', currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(12),
        quantity=1
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning == Decimal(-2)


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_currency(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(820)
    asset = baker.make('Asset', asset_type=CURRENCY_ASSET_TYPE, currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(800),
        quantity=10
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning == Decimal('0.25')


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_currency_2(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = Decimal(780)
    asset = baker.make('Asset', asset_type=CURRENCY_ASSET_TYPE, currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(800),
        quantity=10
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning == Decimal('-0.25')


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_currency_none(
    get_current_asset_price_mock
):
    get_current_asset_price_mock.return_value = None
    asset = baker.make('Asset', asset_type=CURRENCY_ASSET_TYPE, currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(800),
        quantity=10
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning is None


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_none(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = None
    asset = baker.make('Asset', currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(12),
        quantity=1
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning is None


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_current_asset_price')
def test_get_asset_portfolio_earning_negative(get_current_asset_price_mock):
    get_current_asset_price_mock.return_value = -20
    asset = baker.make('Asset', currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        purchase_price=Decimal(12),
        quantity=1
    )
    earning = get_asset_portfolio_earning(asset_portfolio)
    assert earning == Decimal(-12)


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_best_performance_1(
    get_asset_portfolio_performance_mock
):
    get_asset_portfolio_performance_mock.side_effect = [1, 3, 5]

    portfolio = baker.make('Portfolio')
    asset_portfolio1 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio2 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio3 = baker.make('AssetPortfolio', portfolio=portfolio)

    best_asset_portfolio = get_asset_portfolio_best_performance(portfolio)
    assert best_asset_portfolio == asset_portfolio3


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_best_performance_2(
    get_asset_portfolio_performance_mock
):
    get_asset_portfolio_performance_mock.side_effect = [1, 3, None]

    portfolio = baker.make('Portfolio')
    asset_portfolio1 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio2 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio3 = baker.make('AssetPortfolio', portfolio=portfolio)

    best_asset_portfolio = get_asset_portfolio_best_performance(portfolio)
    assert best_asset_portfolio == asset_portfolio2


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_best_performance_none(
    get_asset_portfolio_performance_mock
):
    portfolio = baker.make('Portfolio')

    best_asset_portfolio = get_asset_portfolio_best_performance(portfolio)
    assert best_asset_portfolio is None


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_best_performance_3(
    get_asset_portfolio_performance_mock
):
    get_asset_portfolio_performance_mock.side_effect = [1, 3, -10]

    portfolio = baker.make('portfolio')
    asset_portfolio1 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio2 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio3 = baker.make('AssetPortfolio', portfolio=portfolio)

    best_asset_portfolio = get_asset_portfolio_best_performance(portfolio)
    assert best_asset_portfolio == asset_portfolio2


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_worst_performance_1(
    get_asset_portfolio_performance_mock
):
    get_asset_portfolio_performance_mock.side_effect = [1, 3, -10]

    portfolio = baker.make('Portfolio')
    asset_portfolio1 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio2 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio3 = baker.make('AssetPortfolio', portfolio=portfolio)

    worst_asset_portfolio = get_asset_portfolio_worst_performance(portfolio)
    assert worst_asset_portfolio == asset_portfolio3


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_worst_performance_2(
    get_asset_portfolio_performance_mock
):
    get_asset_portfolio_performance_mock.side_effect = [1, -3, 10]

    portfolio = baker.make('Portfolio')
    asset_portfolio1 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio2 = baker.make('AssetPortfolio', portfolio=portfolio)
    asset_portfolio3 = baker.make('AssetPortfolio', portfolio=portfolio)

    worst_asset_portfolio = get_asset_portfolio_worst_performance(portfolio)
    assert worst_asset_portfolio == asset_portfolio2


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_asset_portfolio_performance')
def test_get_asset_portfolio_worst_performance_none(
    get_asset_portfolio_performance_mock
):
    portfolio = baker.make('Portfolio')

    worst_asset_portfolio = get_asset_portfolio_worst_performance(portfolio)
    assert worst_asset_portfolio is None


@pytest.mark.django_db
@mock.patch('utils.CurrencyConverter.convert')
def test_get_asset_portfolio_invested_amount_currencies(convert_mock):

    convert_mock.return_value = 9

    asset = baker.make(
        'Asset',
        asset_type='currencies',
        currency='EUR',
    )
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        quantity=10,
    )
    invested_amount = get_asset_portfolio_invested_amount(asset_portfolio)
    assert invested_amount == 9


@pytest.mark.django_db
def test_get_asset_portfolio_invested_amount():

    asset = baker.make('Asset', asset_type='anything', currency='USD')
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        quantity=10,
        purchase_price=9,
    )
    invested_amount = get_asset_portfolio_invested_amount(asset_portfolio)
    assert invested_amount == 90


@pytest.mark.django_db
def test_get_optmization_portfolios_ok():

    user = baker.make('User')
    asset = baker.make('Asset')
    portfolio = baker.make('Portfolio', user=user)
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        portfolio=portfolio,
    )

    portfolio_optimization = baker.make(
        'PortfolioOptimization',
        user=user,
    )
    asset_optimization = baker.make(
        'AssetOptimization',
        asset=asset,
        portfolio_optimization=portfolio_optimization,
    )

    response = get_optmization_portfolios(portfolio)
    assert response == [portfolio_optimization]


@pytest.mark.django_db
def test_get_optmization_portfolios_wrong():

    user = baker.make('User')
    asset1 = baker.make('Asset')
    asset2 = baker.make('Asset')
    portfolio = baker.make('Portfolio', user=user)
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset1,
        portfolio=portfolio,
    )

    portfolio_optimization = baker.make(
        'PortfolioOptimization',
        user=user,
    )
    asset_optimization = baker.make(
        'AssetOptimization',
        asset=asset2,
        portfolio_optimization=portfolio_optimization,
    )

    response = get_optmization_portfolios(portfolio)
    assert response == []


@pytest.mark.django_db
def test_get_optmization_portfolios_no_optimization():

    user = baker.make('User')
    asset = baker.make('Asset')
    portfolio = baker.make('Portfolio', user=user)
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        portfolio=portfolio,
    )
    response = get_optmization_portfolios(portfolio)
    assert response == []


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_total_portfolio_invested_amount')
def test_build_data_to_apply_optimization(
    get_total_portfolio_invested_amount_mock
):

    get_total_portfolio_invested_amount_mock.return_value = Decimal(100)

    user = baker.make('User')
    asset = baker.make('Asset', currency='USD')
    portfolio = baker.make('Portfolio', user=user)
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        portfolio=portfolio,
    )

    portfolio_optimization = baker.make(
        'PortfolioOptimization',
        optimism=10,
        min_disposed_to_lose=60,
        user=user,
    )
    asset_optimization = baker.make(
        'AssetOptimization',
        asset=asset,
        min_to_invest=0,
        max_to_invest=80,
        portfolio_optimization=portfolio_optimization,
    )

    response = build_data_to_apply_optimization(
        portfolio,
        portfolio_optimization
    )

    expected = {
        'total_amount_to_invest': 100,
        'optimism': 10,
        'min_disposed_to_lose': 60,
        'asset_optimizations': [
            {
                'asset_id': asset.id,
                'min_to_invest': 0,
                'max_to_invest': 80,
            }
        ]
    }
    assert response.validated_data == expected


@pytest.mark.django_db
@mock.patch('apps.portfolio.services.get_total_portfolio_invested_amount')
def test_build_data_to_apply_optimization_empty_asset(
    get_total_portfolio_invested_amount_mock
):

    get_total_portfolio_invested_amount_mock.return_value = Decimal(100)

    user = baker.make('User')
    asset = baker.make('Asset', currency='USD')
    portfolio = baker.make('Portfolio', user=user)
    asset_portfolio = baker.make(
        'AssetPortfolio',
        asset=asset,
        portfolio=portfolio,
    )

    portfolio_optimization = baker.make(
        'PortfolioOptimization',
        optimism=10,
        min_disposed_to_lose=60,
        user=user,
    )

    response = build_data_to_apply_optimization(
        portfolio,
        portfolio_optimization
    )

    expected = {
        'total_amount_to_invest': 100,
        'optimism': 10,
        'min_disposed_to_lose': 60,
        'asset_optimizations': []
    }
    assert response.validated_data == expected
