"""
URL configuration for taipeidaytrip project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.http import FileResponse
from django.conf import settings
from django.conf.urls.static import static

def index(request):
    return FileResponse(open('static/index.html', 'rb'), content_type='text/html')

def attraction_page(request, id):
    return FileResponse(open('static/attraction.html', 'rb'), content_type='text/html')

def booking_page(request):
    return FileResponse(open('static/booking.html', 'rb'), content_type='text/html')

def thankyou_page(request):
    return FileResponse(open('static/thankyou.html', 'rb'), content_type='text/html')

def favicon(request):
    return FileResponse(open('static/public/favicon.ico', 'rb'), content_type='image/x-icon')

# django_app/urls.py
urlpatterns = [
    # Page Route
    path('', index),
    path('attraction/<int:id>', attraction_page),
    path('booking', booking_page),
    path('thankyou', thankyou_page),
    path('favicon.ico', favicon),
    
    # API Route
    path('api/attractions', include('attractions.urls')),  
    path('api/attraction/', include('attractions.urls')),   # Because of refactor from FastAPI
    path('api/mrts', include('mrts.urls')),
    path("api/user", include("user.urls")),
    path("api/booking", include("booking.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])