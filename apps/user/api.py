from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user.serializers import (
    CreateUserRequest,
    UserSerializer,
    LoginSerializer,
)
from apps.user.services import (
    create_user,
    get_or_create_token_from_user,
)


class CreateUserAPI(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateUserRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user, token = create_user(
            username=data['email'],
            email=data['email'],
            password=data['password']
        )

        user_serializer = UserSerializer(user)
        repsonse_data = {
            'user': user_serializer.data,
            'token': token.key
        }
        return Response(
            {'results': repsonse_data},
            status=status.HTTP_201_CREATED
        )


class GetToken(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = authenticate(
            username=data['username'],
            password=data['password']
        )

        token = None
        if user:
            token = get_or_create_token_from_user(user)

        return Response(
            {'results': token.key if token else None},
            status=status.HTTP_201_CREATED
        )


class GetUserData(APIView):

    def get(self, request):
        print("Holaaa")
        user_serializer = UserSerializer(request.user)
        return Response(
            {'results': user_serializer.data},
            status=status.HTTP_201_CREATED
        )
