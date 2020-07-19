from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from apps.portfolio_optimization.services import (
    create_empty_portoflio_optimization
)


def create_user(email: str, username: str, password: str) -> User:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    create_empty_portoflio_optimization(user)
    token = get_or_create_token_from_user(user)
    return user, token


def get_or_create_token_from_user(user: User) -> str:
    token, created = Token.objects.get_or_create(user=user)
    return token
