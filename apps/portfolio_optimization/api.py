from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.portfolio_optimization.api_serializers import (
    PortfolioOptimizationSerializer,
    RequestCreatePortfolioOptimizationSerializer,
    RequestOptimizationSerializer,
)
from apps.portfolio_optimization.models import PortfolioOptimization
from apps.portfolio_optimization.services import (
    create_or_update_portfolio_optimization,
    optimize_model,
)


class PortfolioOptimizationAPI(APIView):

    def get(self, request, id=None):
        if id:
            portfolio_optimization = get_object_or_404(
                PortfolioOptimization,
                pk=id,
                user=request.user
            )
        else:
            portfolio_optimization = PortfolioOptimization.objects.filter(
                user=request.user
            ).first()

        serializer = PortfolioOptimizationSerializer(portfolio_optimization)
        return Response(
            {'results': serializer.data},
            status=status.HTTP_201_CREATED
        )

    def post(self, request, id=None):
        data = request.data
        data['user'] = request.user.id
        if id:
            data['id'] = id
        serializer = RequestCreatePortfolioOptimizationSerializer(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        create_or_update_portfolio_optimization(serializer)

        return Response(
            {'results': {}},
            status=status.HTTP_201_CREATED
        )


class GenerateOptimizationAPI(APIView):

    def post(self, request):

        serializer = RequestOptimizationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                response = optimize_model(serializer)
            except Exception as e:
                if str(e) == ' @error: Solution Not Found\n':
                    response = {'detail': 'Solution Not Found'}
                    return Response(
                        {'results': response},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                else:
                    raise(e)
            return Response(
                {'results': response},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'results': serializer.errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
