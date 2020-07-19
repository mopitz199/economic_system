from datetime import datetime

from apps.asset.models import Asset
from apps.crypto.models import Ranking
from apps.crypto.serializers.ranking import RankingFromSymbolSerializer


class RankingFactory:

    @classmethod
    def create_ranking_from_symbol(
        cls,
        data: dict
    ) -> Ranking:
        asset = Asset.objects.filter(
            symbol=data['symbol'],
            slug=data['slug'],
            asset_type='cryptos',
        ).first()

        if asset:
            date_obj = datetime.strptime(
                data['ranking_date'],
                '%Y-%m-%d'
            ).date()

            ranking = Ranking(
                asset=asset,
                marketcap=data['marketcap'],
                ranking=data['ranking'],
                ranking_date=date_obj,
                price=data['price']
            )
            ranking.save()
            return ranking
