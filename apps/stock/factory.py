from typing import Dict, List

from apps.asset.models import Asset
from apps.stock.models import DilutedEPS


class DilutedEPSFactory:

    @staticmethod
    def create_diluted_eps(
        data: Dict,
        commit: bool = False,
    ) -> DilutedEPS:
        symbol = data['symbol']
        asset = Asset.objects.filter(
            asset_type='stocks',
            symbol=symbol
        ).first()
        if asset:
            data.pop('symbol')
            diluted_esp = DilutedEPS(**data, asset=asset)
            if commit:
                diluted_esp.save()
            return diluted_esp
        else:
            return None

    @staticmethod
    def create_multiple_diluted_eps(
        data: List,
        commit: bool = True,
    ) -> List[DilutedEPS]:
        all_diluted_eps = []
        for diluted_eps_dict in data:
            diluted_eps = DilutedEPSFactory.create_diluted_eps(
                diluted_eps_dict,
                commit=False,
            )
            if diluted_eps:
                all_diluted_eps.append(diluted_eps)
        if commit:
            if all_diluted_eps:
                DilutedEPS.objects.bulk_create(all_diluted_eps)
        return all_diluted_eps
