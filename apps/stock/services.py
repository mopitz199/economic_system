from datetime import datetime, date

from apps.stock.models import DilutedEPS


class DilutedEPSServices:

    @staticmethod
    def get_eps(symbol: str, date_obj: date):
        diluted_eps = DilutedEPS.objects.filter(
            asset__symbol=symbol,
            asset__asset_type='stocks',
            diluted_eps_date__lte=date_obj
        ).order_by('diluted_eps_date').last()

        return diluted_eps
