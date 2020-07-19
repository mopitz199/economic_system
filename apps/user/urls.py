from django.conf.urls import url, include
from django.urls import path

from apps.user.api import CreateUserAPI, GetUserData, GetToken


user_urlpatterns = [
    path(
        'user/create-user/',
        CreateUserAPI.as_view()
    ),
    path(
        'user/get-user-data/',
        GetUserData.as_view()
    ),
    path(
        'user/get-token/',
        GetToken.as_view()
    ),
]

url_app = []
url_app += user_urlpatterns
