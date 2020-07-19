from django.conf.urls import url, include
from django.urls import path

from apps.portfolio_optimization.api import (
    PortfolioOptimizationAPI,
    GenerateOptimizationAPI
)


portfolio_optimization_urlpatterns = [
    path(
        'portfolio-optimization/<int:id>/',
        PortfolioOptimizationAPI.as_view()
    ),
    path(
        'portfolio-optimization/',
        PortfolioOptimizationAPI.as_view()
    ),
    path(
        'generate-optimization/',
        GenerateOptimizationAPI.as_view()
    ),
]

url_app = []
url_app += portfolio_optimization_urlpatterns
