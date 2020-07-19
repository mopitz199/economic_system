from datetime import datetime, timedelta
from itertools import groupby

from django.shortcuts import render

from apps.chart.models import Point


def metrics(request):

    def group_func(p):
        return int(p.point_date.strftime("%Y%m%d%H0000"))

    start = datetime.today() - timedelta(days=1)

    dates = list(Point.objects.filter(point_date__gte=start).distinct('point_date').values_list('point_date', flat=True))
    init_data = {}
    for date_obj in dates:
        date_str = int(date_obj.strftime("%Y%m%d%H0000"))
        init_data[date_str] = 0

    stocks_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='stocks').order_by("point_date")
    stocks_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(stocks_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        stocks_chart.append(aux_dict[i])

    futures_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='futures').order_by("point_date")
    futures_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(futures_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        futures_chart.append(aux_dict[i])

    commodities_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='commodities').order_by("point_date")
    commodities_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(commodities_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        commodities_chart.append(aux_dict[i])

    etf_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='etf').order_by("point_date")
    etf_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(etf_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        etf_chart.append(aux_dict[i])

    index_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='index').order_by("point_date")
    index_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(index_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        index_chart.append(aux_dict[i])

    currencies_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='currencies').order_by("point_date")
    currencies_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(currencies_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        currencies_chart.append(aux_dict[i])

    cryptos_points = Point.objects.filter(point_date__gte=start, chart__asset__asset_type='cryptos').order_by("point_date")
    cryptos_chart = []
    aux_dict = init_data.copy()
    for key, group in groupby(cryptos_points, group_func):
        aux_dict[key] = len(list(group))
    for i in sorted(aux_dict.keys()):
        cryptos_chart.append(aux_dict[i])

    labels = sorted(dates)
    labels = [d.strftime("%Y%m%d%H") for d in labels]

    context = {
        'labels': labels,
        'stocks_chart': stocks_chart,
        'futures_chart': futures_chart,
        'currencies_chart': currencies_chart,
        'commodities_chart': commodities_chart,
        'etf_chart': etf_chart,
        'cryptos_chart': cryptos_chart,
        'index_chart': index_chart,
    }
    return render(request, 'metrics.html', context)
