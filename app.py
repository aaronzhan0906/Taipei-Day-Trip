from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api import attractions, booking, orderController, mrts, userController


app=FastAPI()
app.include_router(attractions.router)
app.include_router(mrts.router)
app.include_router(userController.router)
app.include_router(booking.router)
app.include_router(orderController.router)
app.mount("/static", StaticFiles(directory="static"))


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
	with open("./static/public/favicon.ico", "rb") as f:
		favicon = f.read()
	return Response(content=favicon, media_type="image/x-icon")

@app.get("/", include_in_schema=False) # hides the path operation from the schema used to autogenerate API docs.
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")