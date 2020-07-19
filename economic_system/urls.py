"""economic_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.asset.api import AssetViewSet
from apps.portfolio.api import AssetPortfolioViewSet
from apps.crypto.api import RankingViewSet
from apps.chart.api import ChartViewSet

from apps.crypto.api import CreateRankingFromSymbol


router = routers.DefaultRouter()
router.register(r'crypto/rankings', RankingViewSet)
router.register(r'asset/assets', AssetViewSet)
router.register(
    r'portfolio/asset_portfolio',
    AssetPortfolioViewSet,
    basename='AssetPortfolioViewSet'
)
router.register(r'chart/charts', ChartViewSet)


schema_view = get_schema_view(
   openapi.Info(
      title="Economic System API",
      default_version='v1',
      description="Documentation to test our api in a sandbox environment",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="mopitz199@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


from apps.crypto.urls import url_app as url_crypto_app
from apps.chart.urls import url_app as url_chart_app
from apps.asset.urls import url_app as url_asset_app
from apps.stock.urls import url_app as url_stock_app
from apps.portfolio.urls import url_app as url_portfolio_app
from apps.portfolio_optimization.urls import (
    url_app as url_portfolio_optimization_app
)
from apps.user.urls import url_app as url_user_app


urlpatterns = [
    url(r'^api/', include(url_crypto_app)),
    url(r'^api/', include(url_chart_app)),
    url(r'^api/', include(url_asset_app)),
    url(r'^api/', include(url_stock_app)),
    url(r'^api/', include(url_portfolio_app)),
    url(r'^api/', include(url_portfolio_optimization_app)),
    url(r'^api/', include(url_user_app)),
    url(r'^api/', include(router.urls)),
    url(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework'
    )),
]
