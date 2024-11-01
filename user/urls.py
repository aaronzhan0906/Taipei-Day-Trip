# user/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path("", views.signup_user),
    path("/auth", views.handle_auth),
]