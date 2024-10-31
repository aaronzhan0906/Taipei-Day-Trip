from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_mrts, name='get_mrts'),
]