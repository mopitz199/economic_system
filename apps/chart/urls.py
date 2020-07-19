from django.conf.urls import url, include

from apps.chart.api import (
    BulkPoints,
    GetChart,
    BulkPointsWithoutChart,
    GetMilestoneData,
)

from apps.chart.views import metrics

candle_urlpatterns = [
    url(r'^chart/point/bulk-points/?$', BulkPoints.as_view()),
    url(
        r'^chart/point/bulk-points-without-chart/?$',
        BulkPointsWithoutChart.as_view()
    ),
    url(r'^chart/chart/generate_chart/?$', GetChart.as_view()),
    url(
        r'^chart/chart/milestones/?$',
        GetMilestoneData.as_view(),
        name='get_milestones'
    ),
]

url_app = [
    url(r'^chart/metrics/?$', metrics),
]
url_app += candle_urlpatterns
