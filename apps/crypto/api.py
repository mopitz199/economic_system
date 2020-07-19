from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crypto.models import Ranking
from apps.crypto.serializers.ranking import (
    RankingSerializer,
    RankingFromSymbolSerializer
)

from apps.crypto.factory import RankingFactory


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer


class CreateRankingFromSymbol(APIView):

    def post(self, request):
        data = request.data
        serializer = RankingFromSymbolSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ranking = RankingFactory.create_ranking_from_symbol(data)
        ranking_serilizer = RankingSerializer(ranking)
        return Response(ranking_serilizer.data, status=status.HTTP_201_CREATED)
