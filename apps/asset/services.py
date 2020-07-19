from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Max

from apps.asset.models import Asset, AssetDetail
from apps.portfolio.models import Portfolio, AssetPortfolio
from apps.chart.constants import PER_DAY
from apps.chart.models import Point, Chart, Candle, AssetMilestone, Milestone
from apps.chart.factory import GenerateChartFactory
from apps.chart.services import (
    create_chart,
    build_historical_data,
    get_best_time_frame_from_range,
    build_asset_milestones,
    clean_intersection_data,
    get_first_date_with_data,
    get_last_date_with_data,
    get_all_chart_data_by_day,
    chart_data_to_dict,
)
from constants import (
    CURRENCY_ASSET_TYPE,
    CRYPTO_ASSET_TYPE,
    STOCK_ASSET_TYPE,
    COMMODITY_ASSET_TYPE,
)
from utils import get_performance, price_to_show, to_usd


def get_asset_search_result(query: str) -> List[Dict]:
    """Search service to get all the asset according to
    the query"""

    from apps.asset.api_serializers import AssetSerializer
    if not query:
        return []
    else:
        assets_exactly = Asset.objects.filter(
            Q(name=query) | Q(symbol=query)
        )[:20]

        assets_contains = Asset.objects.filter(
            Q(name__icontains=query) | Q(symbol__icontains=query)
        )[:80]

        assets = list(set(list(assets_exactly) + list(assets_contains)))
        serializer = AssetSerializer(assets, many=True)
        return serializer.data


def get_current_asset_price(asset: Asset) -> Decimal:
    """Get the last price of an asset"""

    point = Point.objects.filter(chart__asset=asset).last()
    if point:
        return point.price
    else:
        return None


def get_yahoo_symbol(
    symbol: str,
    asset_type: str
) -> str:
    """Get the symbol that yahoo finance need to find an specific asset"""

    if asset_type == 'cryptos':
        return f"{symbol}-USD"
    elif asset_type == 'stocks':
        return symbol
    elif asset_type == 'commodities':
        raise Exception("We don't have commodities")
    elif asset_type == 'futures':
        return f"{symbol}=F"
    elif asset_type == 'etf':
        return symbol
    elif asset_type == 'currencies':
        return f"{symbol}=X"
    else:
        raise Exception(f"We coulnd't process {symbol} symbol")


def get_stock_info(yahoo_symbol: str) -> Dict:
    """It return the sector and industry of an specific stock"""

    url = (
        f"https://finance.yahoo.com/quote/{yahoo_symbol}"
        f"/profile?p={yahoo_symbol}"
    )
    response = requests.get(url)
    content = BeautifulSoup(response.text, 'html.parser')
    sector = content.find('span', text='Sector').findNext('span').text
    industry = content.find('span', text='Industry').findNext('span').text
    return {
        'sector': sector,
        'industry': industry
    }


def get_sector_and_industry(asset: Asset) -> Tuple:
    """Get the sector and industry of the given asset"""

    asset_details = asset.assetdetail_set.all()
    for asset_detail in asset_details:
        if asset_detail.name == 'generic':
            return (
                asset_detail.data.get('sector', None),
                asset_detail.data.get('industry', None)
            )
        else:
            return (None, None)
    return (None, None)


def asset_exists(symbol: str, asset_type: str) -> bool:
    """Check if an asset is already in the database"""

    return Asset.objects.filter(
        symbol=symbol,
        asset_type=asset_type
    ).exists()


def get_yahoo_historical_dataframe(yahoo_symbol: str) -> Any:
    """To get the pandas dataframe with the historical candles
    of an speific asset in yahoo finance"""

    ticker = yf.Ticker(yahoo_symbol)
    hist = ticker.history(period="max")
    return hist


def create_slug(name: str) -> str:
    """Create a name easy to use witout special characters
    , spaces or uppercase"""
    return name.lower().strip().replace(" ", "-")


def create_asset(
    symbol: str,
    name: str,
    asset_type: str,
    slug: str = None
) -> Asset:
    """Service to create a simple asset instance without any other
    relation"""
    if not slug:
        slug = create_slug(name)
    asset = Asset(
        name=name,
        symbol=symbol,
        asset_type=asset_type,
        slug=slug,
    )
    asset.save()
    return asset


def create_asset_detail(
    asset: Asset,
    name: str,
    data: Dict,
) -> AssetDetail:
    """Service to create a simple asset detail instance without any other
    relation"""

    asset_detail = AssetDetail(
        asset=asset,
        name=name,
        data=data
    )
    asset_detail.save()
    return asset_detail


@transaction.atomic
def build_asset(symbol, name, asset_type):
    """The main service to create an asset with all the
    requirements (charts, historical data, info, etc...)"""

    if asset_exists(symbol, asset_exists):
        raise Exception('Asset already exists')

    yahoo_symbol = get_yahoo_symbol(symbol, asset_type)
    hist = get_yahoo_historical_dataframe(yahoo_symbol)
    if not hist.empty:
        asset = create_asset(symbol, name, asset_type)
        candle_chart = create_chart(asset, '1d', 'candle')
        point_chart = create_chart(asset, '1h', 'point')
        if asset_type == 'stocks':
            stock_info = get_stock_info(yahoo_symbol)
            asset_detail = create_asset_detail(asset, 'generic', stock_info)
        build_historical_data(hist, candle_chart)
        build_asset_milestones(asset)
        health = get_asset_health_indicator(asset)
        asset.health = health or 0
        asset.save()
    else:
        raise Exception(f"{symbol} hasn't has historical data")


def get_asset_performance(
    asset: Asset,
    start: datetime,
    end: datetime,
) -> Optional[Decimal]:
    """It will give you the performance in percentage
    in the given range"""

    from apps.chart.api_serializers import GetChartRequestSerializer

    best_time_frame = get_best_time_frame_from_range(start, end)

    data = {
        'symbol': asset.symbol,
        'asset_type': asset.asset_type,
        'time_frame': best_time_frame,
        'start': start,
        'end': end,
    }
    request_serializer = GetChartRequestSerializer(data=data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data
    simulated_chart_data = GenerateChartFactory.generate_chart(**data)
    if simulated_chart_data:
        first_price = simulated_chart_data[0]['price']
        last_price = simulated_chart_data[-1]['price']
        return get_performance(first_price, last_price)
    else:
        return None


def get_24_hour_asset_performance(asset: Asset) -> Optional[Decimal]:
    ending_date = datetime.now()
    init_date = ending_date - timedelta(days=1)
    return get_asset_performance(asset, init_date, ending_date)


def get_weekly_asset_performance(asset: Asset) -> Optional[Decimal]:
    ending_date = datetime.now()
    init_date = ending_date - timedelta(days=7)
    return get_asset_performance(asset, init_date, ending_date)


def get_monthly_asset_performance(asset: Asset) -> Optional[Decimal]:
    ending_date = datetime.now()
    init_date = ending_date - timedelta(days=30)
    return get_asset_performance(asset, init_date, ending_date)


def get_max_price(asset: Asset) -> Decimal:
    """Get the historical max price of the asset"""

    max_price_1 = Candle.objects\
        .filter(
            chart__asset=asset
        )\
        .aggregate(Max('close_price'))['close_price__max']

    max_price_2 = Point.objects\
        .filter(
            chart__asset=asset
        )\
        .aggregate(Max('price'))['price__max']
    if max_price_1 is not None and max_price_2 is not None:
        return max(max_price_1, max_price_2)
    else:
        return max_price_1 or max_price_2


def reset_asset(asset):
    """Re load all candle day data and all their milestones
    and clean the intersection with points"""

    yahoo_symbol = get_yahoo_symbol(asset.symbol, asset.asset_type)
    df = get_yahoo_historical_dataframe(yahoo_symbol)
    chart = Chart.objects.get(chart_type='candle', asset=asset)
    Candle.objects.filter(chart=chart).delete()
    build_historical_data(df, chart)
    clean_intersection_data(asset)
    build_asset_milestones(asset)


def get_asset_health_indicator(asset):
    """Indicator to get how healthy and trustly is an asset data price"""
    from apps.chart.api_serializers import GetChartRequestSerializer

    first_date = get_first_date_with_data(asset)
    last_date = get_last_date_with_data(asset)
    if first_date and last_date:
        data = {
            'symbol': asset.symbol,
            'asset_type': asset.asset_type,
            'time_frame': PER_DAY,
            'start': first_date,
            'end': last_date,
        }

        total_days = (last_date - first_date).days
        request_serializer = GetChartRequestSerializer(data=data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        simulated_chart_data = GenerateChartFactory.generate_chart(**data)

        if simulated_chart_data:
            filtered_data = []
            for price_data in simulated_chart_data:
                datetime_object = datetime.strptime(price_data['date'], '%Y-%m-%d')
                if datetime_object.weekday() not in [5, 6]:
                    filtered_data.append(price_data)

            filtered_total_days = len(filtered_data)

            df = pd.DataFrame(filtered_data)
            volatility_list = df['price'].rolling(
                window=2
            ).std().values.tolist()

            filter_volatility_list = filter(
                lambda v: v > 0,
                volatility_list
            )
            volatile_days = len(list(filter_volatility_list))

            rate_min_days = volatile_days/90
            if rate_min_days > 1:
                rate_min_days = 1

            return (volatile_days/filtered_total_days)*rate_min_days
    return 0


def update_all_asset_health():
    """Update the health indicator of all assets"""

    assets = []
    for asset in Asset.objects.all().order_by('id'):
        health = get_asset_health_indicator(asset)
        asset.health = health
        assets.append(asset)

    Asset.objects.bulk_update(assets, ['health'])


def generate_all_asset_milestone_charts(milestone: Milestone) -> Dict:
    """Generate all chart data for all asset milestone linked
    to the given milestone"""

    asset_milestones = milestone.assetmilestone_set.exclude(
        total_performance=None
    )

    results = {}
    for asset_milestone in asset_milestones:
        data = {
            'symbol': asset_milestone.asset.symbol,
            'asset_type': asset_milestone.asset.asset_type,
            'time_frame': PER_DAY,
            'start': milestone.start,
            'end': milestone.end,
        }
        asset_data = GenerateChartFactory.generate_chart(**data)
        asset_data_dict = chart_data_to_dict(asset_data)
        if asset_data_dict:
            results[asset_milestone.id] = asset_data_dict

    return results


def get_correlation_between_to_data_charts(data_chart1, data_chart2):

    dataframe_data = {
        'date': [],
        'asset1': [],
        'asset2': []
    }

    for key in data_chart1:
        asset1_price = data_chart1.get(key)
        asset2_price = data_chart2.get(key)
        if asset2_price and asset1_price:
            dataframe_data['asset1'].append(float(asset1_price))
            dataframe_data['asset2'].append(float(asset2_price))
            dataframe_data['date'].append(key)

    df = pd.DataFrame(data=dataframe_data)
    if df.empty:
        return None
    else:
        return df['asset1'].corr(df['asset2'])


def generate_asset_milestone_correlation(milestone: Milestone):
    """Create all the AssetMilestoneComparision of all the assets
    involved with the given milestone"""

    from apps.chart.models import AssetMilestoneComparision

    data = generate_all_asset_milestone_charts(milestone)

    asset_ids = []
    for asset_id in data:
        asset_ids.append(asset_id)

    results = []

    for asset_id in asset_ids:
        main_data = data.pop(asset_id)
        for aux_asset_id in data:
            aux_data = data[aux_asset_id]
            correlation = get_correlation_between_to_data_charts(
                main_data,
                aux_data
            )
            comparision = AssetMilestoneComparision(
                asset_milestone_1_id=asset_id,
                asset_milestone_2_id=aux_asset_id,
                correlation=correlation
            )
            results.append(comparision)
            if len(results) >= 50000:
                AssetMilestoneComparision.objects.bulk_create(results)
                results = []

    AssetMilestoneComparision.objects.bulk_create(results)
