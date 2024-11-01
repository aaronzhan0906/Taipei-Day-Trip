# attractions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_attractions),
    path("<int:attraction_id>", views.get_attraction),
]


"""
request: /api/attractions/      → django_app/urls.py → attractions/urls.py → views.get_attractions
request: /api/attraction/1     → django_app/urls.py → attractions/urls.py → views.get_attraction
"""