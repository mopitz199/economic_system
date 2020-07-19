from django.conf.urls import url, include

from apps.portfolio.api import GetPortfolioData, ApplyOptimization


portfolio_urlpatterns = [
    url(
        r'^portfolio/asset_portoflio_data/?$',
        GetPortfolioData.as_view()
    ),
    url(
        r'^portfolio/apply-optimization/?$',
        ApplyOptimization.as_view()
    ),
]

url_app = []
url_app += portfolio_urlpatterns
