from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

def serve_static_html(request, path):
    return serve(request, path, document_root=STATIC_DIR)

urlpatterns = [
    # Page Routes 
    path("", lambda r: serve_static_html(r, "index.html")),
    path("attraction/<int:id>", lambda r, id: serve_static_html(r, "attraction.html")),
    path("booking", lambda r: serve_static_html(r, "booking.html")),
    path("thankyou", lambda r: serve_static_html(r, "thankyou.html")),
    path("favicon.ico", lambda r: serve_static_html(r, "public/favicon.ico")),
    
    # API Routes
    path("api/attractions", include("attractions.urls")),  
    path("api/attraction/", include("attractions.urls")),
    path("api/mrts", include("mrts.urls")),
    path("api/user", include("user.urls")),
    path("api/booking", include("booking.urls")),
    path("api/orders", include("order.urls")),
    path("api/order/", include("order.urls")),
]

if settings.DEBUG: # Only serve static files in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=STATIC_DIR)