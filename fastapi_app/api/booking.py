from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError 
from typing import List
from datetime import date
from api.JWTHandler import JWTHandler, SECRET_KEY, ALGORITHM
from data.database import get_cursor, conn_commit, conn_close
import jwt


##################### Model #####################
class BookingModel:
    @staticmethod
    def get_user_id_from_token(authorization: str) -> int:
        if authorization == "null":
            raise HTTPException(status_code=401, detail="Not logged in.")
        
        try:
            token = authorization.split()[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload["user_id"]
        except IndexError:
            raise HTTPException(status_code=403, detail="Invalid authorization header")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token")
        except KeyError:
            raise HTTPException(status_code=403, detail="Token payload is invalid")

    @staticmethod
    def get_cart_details(user_id):
        cursor, conn = get_cursor()
        try:
            query = """
            SELECT c.attraction_id, c.cart_date, c.cart_time, c.cart_price,
                a.name, a.address, a.images
            FROM carts c
            JOIN attractions a ON c.attraction_id = a.attraction_id
            WHERE c.user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return None  
            
            attraction_id, cart_date, cart_time, cart_price, name, address, images = result

            image_url = 'https://' + images.strip('"').split('https://')[1].split('\\n')[0]
        
            booking_detail = {
                "attraction": {
                    "id": attraction_id,
                    "name": name,
                    "address": address,
                    "image": image_url
                },
                "date": str(cart_date),
                "time": cart_time,
                "price": cart_price
            }
        
            return booking_detail
        except Exception as e:
            print(f"[get_cart_details] error: {e}")
            return None
        finally:
            conn_close(conn)
  

    @staticmethod
    def create_new_cart(user_id, booking):
        cursor, conn = get_cursor()
        try: 
            query = """
            INSERT INTO carts(user_id, attraction_id, cart_date, cart_time, cart_price)
            VALUES(%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE 
                user_id = VALUES(user_id),
                attraction_id = VALUES(attraction_id),
                cart_date = VALUES(cart_date),
                cart_time = VALUES(cart_time),
                cart_price = VALUES(cart_price)
            """
            cursor.execute(query, (user_id, booking.attractionId,
                                   booking.date, booking.time, booking.price))
            conn_commit(conn)

        except Exception as e:
            conn.rollback()
            print(f"[create_new_cart] error: {e}")
        finally:
            conn_close(conn)

    def clear_cart(user_id):
        cursor, conn = get_cursor()
        try: 
            query = """
            UPDATE carts
            SET attraction_id = NULL,
                cart_date = NULL,
                cart_time = NULL,
                cart_price = NULL
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            conn_commit(conn)

        except Exception as e:
            conn.rollback()
            print(f"[clear_cart] error {e}")
            return None  
        finally:
            conn_close(conn)
    
class BookingView:
    @staticmethod
    def error_response(status_code, message):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})
    
    @staticmethod
    def ok_response(status_code, data=None, token=None, message=None):
        content={"ok":True}
        if data is not None:
            content["data"] = data
        if message is not None:
            content["message"] = message
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return JSONResponse(status_code=status_code, content=content, headers=headers)


##################### CONTROLLER #####################

router = APIRouter()
class BookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int

def validate_booking(booking: BookingInfo) -> List[str]:
    time_slot_prices = {"morning": 2000, "afternoon": 2500}
    errors = []
    
    if booking.time not in time_slot_prices:
        errors.append("Invalid time slot")
    elif booking.price != time_slot_prices[booking.time]:
        errors.append(f"Incorrect price for {booking.time} slot")
    return errors


@router.get("/api/booking")
async def get_order(authorization: str = Header(...)):   
    try:
        user_id = BookingModel.get_user_id_from_token(authorization)
        cart_detail = BookingModel.get_cart_details(user_id)

        if not cart_detail:
            return BookingView.ok_response(200, data=None)
        return BookingView.ok_response(200, data=cart_detail)
    
    except HTTPException as he:
        return BookingView.error_response(he.status_code, he.detail)
    except Exception as exception:
        print(f"[get_order] error {exception}")
        return BookingView.error_response(500, str(exception))

@router.post("/api/booking")
async def post_order(authorization: str = Header(...), booking: BookingInfo = None):
    try:
        user_id = BookingModel.get_user_id_from_token(authorization)
        BookingModel.create_new_cart(user_id, booking)
        return BookingView.ok_response(200, message="成功加入購物車")
    
    except HTTPException as he:
        return BookingView.error_response(he.status_code, he.detail)
    except ValidationError as ve: # pydantic check
        error_messages = "; ".join(error["msg"] for error in ve.errors())
        return BookingView.error_response(400, f"建立失敗，輸入不正確: {error_messages}")
    except Exception as exception:
        print(f"[post_order] error: {exception}")
        return BookingView.error_response(500, "Internal server error")

@router.delete("/api/booking")
async def delete_order(authorization: str = Header(...)):
    try:
        user_id = BookingModel.get_user_id_from_token(authorization)
        BookingModel.clear_cart(user_id)
        return BookingView.ok_response(200, message="刪除購物車裡的項目")
    
    except HTTPException as he:
        return BookingView.error_response(he.status_code, he.detail)
    except Exception as exception:
        print(f"[delete_order] error {exception}")
        return BookingView.error_response(500, "Internal server error")