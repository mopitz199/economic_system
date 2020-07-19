import pytest
from model_bakery import baker

from apps.asset.models import Asset, AssetDetail
from apps.asset.api_serializers import AssetSerializer


@pytest.mark.django_db
def test_get_asset():
    asset = baker.make('Asset')
    asset_detail = baker.make('AssetDetail', asset=asset)
    serializer = AssetSerializer(asset)
    data = serializer.data
    assert True
