from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_order),              # POST /api/orders
    path("<str:order_number>", views.get_order),  # GET /api/order/{orderNumber}
]