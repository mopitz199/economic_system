from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from apps.portfolio.serializers import (
    AssetPortfolioSerializer,
    AssetPortfolioViewSerializer,
)
from apps.portfolio.services import (
    get_asset_portfolio_worst_performance,
    get_asset_portfolio_best_performance,
    get_portfolio_earnings,
    get_total_portfolio_invested_amount,
    apply_optimization,
    get_optmization_portfolios,
    get_asset_portfolio_invested_amount,
    portolfio_is_empty,
)
from apps.portfolio.models import AssetPortfolio, Portfolio

from utils import price_to_show


class AssetPortfolioViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        portfolio, _ = Portfolio.objects.get_or_create(user=user)
        return AssetPortfolio.objects.filter(portfolio=portfolio)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return AssetPortfolioSerializer
        elif self.action in ["retrieve", "list"]:
            return AssetPortfolioViewSerializer
        else:
            return AssetPortfolioSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        portfolio = Portfolio.objects.get(user=request.user)
        data = request.data
        data['portfolio'] = portfolio.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_serializer = AssetPortfolioViewSerializer(instance)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        portfolio = Portfolio.objects.get(user=request.user)
        data = request.data
        data['portfolio'] = portfolio.id
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        response_serializer = AssetPortfolioViewSerializer(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(response_serializer.data)


class GetPortfolioData(APIView):

    def get(self, request):
        user = request.user

        portfolio, _ = Portfolio.objects.get_or_create(user=user)

        worst = get_asset_portfolio_worst_performance(portfolio)
        best = get_asset_portfolio_best_performance(portfolio)
        total_invested = get_total_portfolio_invested_amount(portfolio)

        if total_invested:
            total_invested = price_to_show(total_invested)

        earnings = get_portfolio_earnings(portfolio)
        if earnings:
            earnings = price_to_show(earnings)

        performance = None
        if total_invested and earnings is not None:
            performance = (earnings*100)/total_invested
            performance = round(performance, 2)

        return Response(
            {
                'results': {
                    'performance': performance,
                    'worst': worst.asset.symbol if worst else None,
                    'best': best.asset.symbol if best else None,
                    'earnings': earnings,
                    'total_invested': total_invested,
                }
            },
            status.HTTP_200_OK
        )


class ApplyOptimization(APIView):

    def get(self, request):
        user = request.user
        portfolio = Portfolio.objects.filter(user=user).last()

        result = {}
        if portfolio and not portolfio_is_empty(portfolio):
            portfolio_optimizations = get_optmization_portfolios(portfolio)
            if portfolio_optimizations:
                portoflio_optimization = portfolio_optimizations[0]

                response = apply_optimization(
                    portfolio,
                    portoflio_optimization,
                )

                asset_portfolios = portfolio.assetportfolio_set.all()
                for asset_portfolio in asset_portfolios:
                    total_invested = get_asset_portfolio_invested_amount(
                        asset_portfolio
                    )

                    optimization_result = response.get(
                        asset_portfolio.asset_id
                    )
                    difference = total_invested - Decimal(optimization_result['amount'])
                    result[asset_portfolio.id] = price_to_show(difference)

        return Response({'results': result}, status.HTTP_200_OK)
