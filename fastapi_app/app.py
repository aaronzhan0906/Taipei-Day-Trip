from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api import attractions, booking, orderController, mrts, userController
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(attractions.router)
app.include_router(mrts.router)
app.include_router(userController.router)
app.include_router(booking.router)
app.include_router(orderController.router)

# 獲取靜態文件目錄路徑
static_dir = os.getenv("STATIC_FILES_DIR", "../static")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory=static_dir))

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(static_dir, "public/favicon.ico")
    try:
        with open(favicon_path, "rb") as f:
            favicon = f.read()
        return Response(content=favicon, media_type="image/x-icon")
    except FileNotFoundError:
        return Response(status_code=404)

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse(os.path.join(static_dir, "index.html"), media_type="text/html")

@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse(os.path.join(static_dir, "attraction.html"), media_type="text/html")

@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse(os.path.join(static_dir, "booking.html"), media_type="text/html")

@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse(os.path.join(static_dir, "thankyou.html"), media_type="text/html")