from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path
import aiofiles

# Get the correct static files directory path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

async def async_serve_html(request, html_file, **kwargs):  # 加入 **kwargs 來接收任何額外參數
    """Asynchronously serve HTML files"""
    try:
        file_path = STATIC_DIR / html_file
        async with aiofiles.open(file_path, mode="rb") as f:
            content = await f.read()
            return HttpResponse(content, content_type="text/html")
    except FileNotFoundError:
        from django.http import Http404
        raise Http404(f"HTML file not found: {html_file}")

async def async_serve_favicon(request):
    """Asynchronously serve favicon.ico"""
    try:
        file_path = STATIC_DIR / "public" / "favicon.ico"
        async with aiofiles.open(file_path, mode="rb") as f:
            content = await f.read()
            return HttpResponse(content, content_type="image/x-icon")
    except FileNotFoundError:
        from django.http import Http404
        raise Http404("Favicon not found")

# Wrapper function to handle route parameters
def serve_html(html_file):
    async def wrapper(request, *args, **kwargs):
        return await async_serve_html(request, html_file)
    return wrapper

# django_app/urls.py
urlpatterns = [
    # Page Route
    path("", async_serve_html, {"html_file": "index.html"}),
    path("attraction/<int:id>", async_serve_html, {"html_file": "attraction.html"}),
    path("booking", async_serve_html, {"html_file": "booking.html"}),
    path("thankyou", async_serve_html, {"html_file": "thankyou.html"}),
    path("favicon.ico", async_serve_favicon),
    
    # API Route
    path("api/attractions", include("attractions.urls")),  
    path("api/attraction/", include("attractions.urls")),
    path("api/mrts", include("mrts.urls")),
    path("api/user", include("user.urls")),
    path("api/booking", include("booking.urls")),
    path("api/orders", include("order.urls")),
    path("api/order/", include("order.urls")),
]

# Static file handling for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=STATIC_DIR)