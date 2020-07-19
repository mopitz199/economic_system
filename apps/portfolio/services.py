from decimal import Decimal
from typing import Optional, List
import collections

from apps.asset.services import get_current_asset_price

from apps.portfolio.models import Portfolio, AssetPortfolio
from apps.portfolio_optimization.models import PortfolioOptimization
from apps.portfolio_optimization.services import optimize_model
from constants import CURRENCY_ASSET_TYPE
from utils import get_performance, to_usd


def get_total_portfolio_invested_amount(portfolio: Portfolio) -> Decimal:
    total = Decimal(0)
    for asset_portfolio in AssetPortfolio.objects.filter(portfolio=portfolio):
        total += get_asset_portfolio_invested_amount(asset_portfolio)
    return total


def get_asset_portfolio_invested_amount(
    asset_portfolio: AssetPortfolio
) -> Decimal:
    """Get the amount(USD) that we have invested in this asset"""

    currencies = [CURRENCY_ASSET_TYPE]
    asset = asset_portfolio.asset

    if asset.asset_type in currencies:
        return to_usd(asset_portfolio.quantity, asset.currency)
    else:
        amount = asset_portfolio.quantity*float(asset_portfolio.purchase_price)
        return to_usd(amount, asset.currency)


def portolfio_is_empty(portfolio: Portfolio) -> int:
    return portfolio.assetportfolio_set.all().count() == 0


def get_asset_portfolio_worst_performance(
    portfolio: Portfolio
) -> AssetPortfolio:
    """Get the asset portfolio with the worst performance at the moment"""
    portfolio_assets = AssetPortfolio.objects.filter(portfolio=portfolio)
    worst_asset_portfolio = None
    worst_performance = None
    for asset_portfolio in portfolio_assets:
        if worst_asset_portfolio is None:
            worst_asset_portfolio = asset_portfolio
            worst_performance = get_asset_portfolio_performance(
                asset_portfolio
            )
        else:
            performance = get_asset_portfolio_performance(asset_portfolio)
            if worst_performance is None:
                worst_asset_portfolio = asset_portfolio
                worst_performance = performance

            if performance and performance < worst_performance:
                worst_asset_portfolio = asset_portfolio
                worst_performance = performance

    return worst_asset_portfolio


def get_asset_portfolio_best_performance(
    portfolio: Portfolio
) -> AssetPortfolio:
    """Get the asset portfolio with the best performance at the moment"""
    portfolio_assets = AssetPortfolio.objects.filter(portfolio=portfolio)
    best_asset_portfolio = None
    best_performance = None
    for asset_portfolio in portfolio_assets:
        if best_asset_portfolio is None:
            best_asset_portfolio = asset_portfolio
            best_performance = get_asset_portfolio_performance(asset_portfolio)
        else:
            performance = get_asset_portfolio_performance(asset_portfolio)
            if best_performance is None:
                best_asset_portfolio = asset_portfolio
                best_performance = performance

            if performance and performance > best_performance:
                best_asset_portfolio = asset_portfolio
                best_performance = performance

    return best_asset_portfolio


def get_portfolio_earnings(portfolio: Portfolio) -> float:
    """Get the total earning or loses of some portafolio user"""
    portfolio_assets = AssetPortfolio.objects.filter(portfolio=portfolio)
    earnings = 0
    for asset_portfolio in portfolio_assets:
        earning = get_asset_portfolio_earning(asset_portfolio)
        if earning:
            earnings += earning
    return earnings


def get_asset_portfolio_earning(
    asset_porfolio: AssetPortfolio
) -> Optional[float]:
    currently_price = get_current_asset_price(asset_porfolio.asset)
    purchase_price = asset_porfolio.purchase_price
    currencies = [CURRENCY_ASSET_TYPE]
    if asset_porfolio.asset.asset_type in currencies:
        if currently_price is not None and purchase_price is not None:
            performance = get_performance(purchase_price, currently_price)
            if performance >= -100:
                rate = performance/float(100)
                earning = rate*asset_porfolio.quantity
                return to_usd(earning, asset_porfolio.asset.currency)
            else:
                return Decimal(0)
        else:
            return None
    else:
        if currently_price is not None and purchase_price is not None:
            max_lose = purchase_price*Decimal(asset_porfolio.quantity)*-1
            unit_earning = currently_price - purchase_price
            earning = unit_earning * Decimal(asset_porfolio.quantity)
            earning = max(earning, max_lose)
            return to_usd(earning, asset_porfolio.asset.currency)
        else:
            return None


def get_asset_portfolio_performance(asset_portfolio: AssetPortfolio) -> float:
    """Get the performance of one of your asset portfolio with the current
    asset value."""

    current_price = get_current_asset_price(asset_portfolio.asset)
    if not current_price:
        return None
    else:
        return get_performance(
            asset_portfolio.purchase_price,
            current_price
        )


def get_optmization_portfolios(
    portoflio: Portfolio
) -> List[PortfolioOptimization]:
    """Get which portfolio optimizations fits with the given portfolio"""

    user = portoflio.user
    asset_ids = portoflio.assetportfolio_set.all().values_list('asset_id')
    portfolio_optimizations = PortfolioOptimization.objects.filter(user=user)

    suitable_optimizations = []
    for portfolio_optimization in portfolio_optimizations:
        asset_optimizations = portfolio_optimization.assetoptimization_set.all()
        optimization_asset_ids = asset_optimizations.values_list('asset_id')

        asset_ids_collection = collections.Counter(asset_ids)
        optimization_asset_ids_collection = collections.Counter(
            optimization_asset_ids
        )
        if asset_ids_collection == optimization_asset_ids_collection:
            suitable_optimizations.append(portfolio_optimization)
    return suitable_optimizations


def build_data_to_apply_optimization(
    portfolio: Portfolio,
    portfolio_optimization: PortfolioOptimization,
) -> "RequestOptimizationSerializer":
    """Generate the serializer to apply optimization"""

    from apps.portfolio_optimization.api_serializers import (
        RequestOptimizationSerializer
    )

    total_invested = get_total_portfolio_invested_amount(portfolio)
    data = {
        "total_amount_to_invest": total_invested,
        "optimism": portfolio_optimization.optimism,
        "min_disposed_to_lose": portfolio_optimization.min_disposed_to_lose,
        "asset_optimizations": []
    }

    asset_optimizations = portfolio_optimization.assetoptimization_set.all()
    for asset_optimization in asset_optimizations:
        asset_optimization_data = {
            "asset_id": asset_optimization.asset_id,
            "min_to_invest": asset_optimization.min_to_invest,
            "max_to_invest": asset_optimization.max_to_invest,
        }
        if asset_optimization.amount_to_invest:
            amount_to_invest = asset_optimization.amount_to_invest
            asset_optimization_data["amount_to_invest"] = amount_to_invest

        data["asset_optimizations"].append(asset_optimization_data)

    serializer = RequestOptimizationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer


def apply_optimization(
    portfolio: Portfolio,
    portfolio_optimization: PortfolioOptimization,
):
    """It will apply the optimization portfolio in your given
    portfolio. The portoflio optimization MUST be suitable"""

    valid_serializer = build_data_to_apply_optimization(
        portfolio,
        portfolio_optimization
    )
    return optimize_model(valid_serializer)
