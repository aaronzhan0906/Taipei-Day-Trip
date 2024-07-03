from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date, datetime
import re._compiler
import requests
import re
import shortuuid
import json
from api.user import get_user_info
from api.jwt_utils import update_jwt_payload, SECRET_KEY, ALGORITHM
from data.database import get_cursor, conn_commit, conn_close

router = APIRouter()

class Order(BaseModel):
    price: int 
    trip: dict
    date: str
    time: str
    contact: dict

class OrderDetail(BaseModel):
    order: Order
    prime: str


# get #
@router.post("/api/orders")
async def post_order(order_detail: OrderDetail, authorization: str = Header(...)):
    if authorization == "null": 
        raise HTTPException(status_code=403, detail={"error": True, "message": "Not logged in."})
    
    phone_pattern = re.compile(r'^[0-9]{10}$')
    if not phone_pattern.match(order_detail.order.contact["phone"]):
        raise HTTPException(status_code=400, detail={"error": True, "message": "手機號碼格式錯誤"})
    
    email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    if not email_pattern.match(order_detail.order.contact["email"]):
        raise HTTPException(status_code=400, detail={"error": True, "message": "電子信箱格式錯誤"})


    try: 
        cursor, conn = get_cursor() 
        user_info_response = await get_user_info(authorization)
        user_info = json.loads(user_info_response.body)["data"]

        order_number = generate_order_number()
        user_name = user_info["name"]
        user_email = user_info["email"]


        tappay_result = process_tappay_payment(order_detail, order_number)
        # print(tappay_result)
        payment_status = "PAID" if tappay_result["status"] == 0 else "UNPAID"
        insert_order_query = """
        INSERT INTO orders (
            order_number, payment_status, user_name, user_email, contact_name, 
            contact_email, contact_phone, attraction_id, order_date, order_time, order_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """
        order_data = (
            order_number,
            payment_status,
            user_name,
            user_email,
            order_detail.order.contact["name"],
            order_detail.order.contact["email"],
            order_detail.order.contact["phone"],
            order_detail.order.trip["id"],
            order_detail.order.date,
            order_detail.order.time,
            str(order_detail.order.price),
        )

        cursor.execute(insert_order_query, order_data)

        conn_commit(conn)
        return JSONResponse(content={"ok": True})

    except Exception as exception:
        print(f"exception {str(exception)}")
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)

TAPPAY_SANDBOX_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
TAPPAY_PARTNER_KEY = "partner_p1becyZviOfzZZHeDntgb8WpTLd8UsRYdp1ikOk0y7AqxiwUyQWLiguI"  
TAPPAY_MERCHANT_ID = "aaronzhan0906_GP_POS_3"  

def process_tappay_payment(order_detail, order_number):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": TAPPAY_PARTNER_KEY
    }
    payload = {
        "prime": order_detail.prime,
        "partner_key": TAPPAY_PARTNER_KEY,
        "merchant_id": TAPPAY_MERCHANT_ID,
        "details": "Taipei One Day Trip Order",
        "amount": order_detail.order.price,  
        "order_number": order_number,
        "cardholder": {
            "phone_number": order_detail.order.contact["phone"],
            "name": order_detail.order.contact["name"], 
            "email": order_detail.order.contact["email"],
        },
        "remember": True 
    }

    response = requests.post(TAPPAY_SANDBOX_URL, json=payload, headers=headers)
    return response.json()

def generate_order_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    short_id = shortuuid.uuid()[:10]
    return f"{timestamp}-{short_id}"