import pytest

from datetime import datetime, timedelta
from decimal import Decimal
from freezegun import freeze_time
from model_bakery import baker
from unittest import mock

from apps.user.services import create_user, get_or_create_token_from_user


@pytest.mark.django_db
def test_create_user():

    user, token = create_user(
        email='mopitz199@gmail.com',
        username='mopitz',
        password='asdf1234'
    )

    assert user.email == 'mopitz199@gmail.com'
    assert user.username == 'mopitz'
    assert token.key


@pytest.mark.django_db
def test_get_or_create_token_from_user():
    user = baker.make('User')
    token = get_or_create_token_from_user(user)
    assert token.key
