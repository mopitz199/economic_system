from django.conf.urls import url, include

from apps.stock.api import CreateMultipleDilutedEPS, GetPER


stock_urlpatterns = [
    url(
        r'^stock/add-multiple-diluted-eps/?$',
        CreateMultipleDilutedEPS.as_view()
    ),
    url(
        r'^stock/get-per/?$',
        GetPER.as_view()
    ),
]

url_app = []
url_app += stock_urlpatterns
