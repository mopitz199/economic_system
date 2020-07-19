from django.conf.urls import url, include

from apps.asset.api import (
    GetCoinmatketcapIds,
    CreateCompleteCryptoAsset,
    AssetSearch,
    AssetProfile,
)


asset_urlpatterns = [
    url(
        r'^asset/coinmarketcap-ids/?$',
        GetCoinmatketcapIds.as_view()
    ),
    url(
        r'^asset/complete-crypto-asset/?$',
        CreateCompleteCryptoAsset.as_view()
    ),
    url(
        r'^asset/search/?$',
        AssetSearch.as_view()
    ),
    url(
        r'^asset/asset_profile/?$',
        AssetProfile.as_view()
    ),
]

url_app = []
url_app += asset_urlpatterns
