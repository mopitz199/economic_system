from django.conf.urls import url, include

from apps.crypto.api import CreateRankingFromSymbol


rankings_urlpatterns = [
    url(
        r'^rankings/create_ranking_from_symbol/?$',
        CreateRankingFromSymbol.as_view()
    ),
]

url_app = []
url_app += rankings_urlpatterns
