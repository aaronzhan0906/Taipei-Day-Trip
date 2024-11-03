from django.urls import path
from . import views

urlpatterns = [
    path("", views.booking_view),  # GET / POST / DELETE
]