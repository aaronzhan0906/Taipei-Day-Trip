# user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.signup_user),  # POST /api/user signup
    path("/auth", views.handle_auth),  # GET,PUT /api/user/auth login and get info
]