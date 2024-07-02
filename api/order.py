from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date
import jwt
from api.user import get_user_info
from api.jwt_utils import update_jwt_payload, SECRET_KEY, ALGORITHM
from data.database import get_cursor, conn_commit, conn_close

router = APIRouter()




class Contact(BaseModel):
    name: str
    email: str
    phone: str

class Order(BaseModel):
    price: int 
    trip: dict
    contact: Contact

class OrderDetail(BaseModel):
    order: Order
    prime: str

# get #
@router.post("/api/orders")
async def post_order(order_detail: OrderDetail, authorization: str = Header(None)):
    if authorization == "null": 
        raise HTTPException(status_code=403, detail={"error": True, "message": "Not logged in."})
    
    if "@" not in order_detail.order.contact.email:
        return JSONResponse(content={"error": True, "message": "電子信箱格式錯誤"}, status_code=400)
    
    if order_detail

    try:


    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)