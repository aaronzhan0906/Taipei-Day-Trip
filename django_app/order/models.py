# orders/models.py
import os
from dotenv import load_dotenv
import re
import shortuuid
from datetime import datetime
import aiohttp
import asyncio
from typing import Optional, Dict, Any, Tuple
from django_app.database import execute_query, execute_update



current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")

require_env_vars = ["TAPPAY_SANDBOX_URL", "TAPPAY_PARTNER_KEY", "TAPPAY_MERCHANT_ID"]
for var in require_env_vars:
    if os.getenv(var) is None:
        raise ValueError(f"ENV {var} is not set")
    
TAPPAY_SANDBOX_URL = os.getenv("TAPPAY_SANDBOX_URL")
TAPPAY_PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
TAPPAY_MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")

load_dotenv(dotenv_path)

class OrderModel:
   @staticmethod
   def validate_phone(phone: str) -> bool:
       phone_pattern = re.compile(r'^[0-9]{10}$')
       return bool(phone_pattern.match(phone))

   @staticmethod
   def validate_email(email: str) -> bool:
       email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
       return bool(email_pattern.match(email))

   @staticmethod
   def generate_order_number() -> str:
       timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
       short_id = shortuuid.uuid()[:10]
       return f"{timestamp}-{short_id}"

   @staticmethod
   async def process_tappay_payment(order_detail: Any, order_number: str) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": TAPPAY_PARTNER_KEY  
        }
        
        payload = {
            "prime": order_detail["prime"],
            "partner_key": TAPPAY_PARTNER_KEY,  
            "merchant_id": TAPPAY_MERCHANT_ID,  
            "details": "Taipei Day Trip Order",
            "amount": order_detail["order"]["price"],
            "order_number": order_number,
            "cardholder": {
                "phone_number": order_detail["order"]["contact"]["phone"],
                "name": order_detail["order"]["contact"]["name"],
                "email": order_detail["order"]["contact"]["email"],
            },
            "remember": True
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(TAPPAY_SANDBOX_URL, json=payload, headers=headers) as response: 
                    if response.status == 200:
                        return await response.json()
                    error_text = await response.text()
                    raise Exception(f"TapPay API error: {response.status} - {error_text}")
            except aiohttp.ClientError as e:
                raise Exception(f"Network error when contacting TapPay: {str(e)}")
            except asyncio.TimeoutError as e:
                raise Exception(f"Request to TapPay timed out: {str(e)}")

   @staticmethod
   def create_order_and_payment(order_detail: Any, user_info: Dict, order_number: str, tappay_result: Dict) -> Dict:
       try:
           payment_status = "PAID" if tappay_result["status"] == 0 else "UNPAID"
           order_data = (
               order_number,
               payment_status,
               user_info["name"],
               user_info["email"],
               order_detail["order"]["contact"]["name"],
               order_detail["order"]["contact"]["email"],
               order_detail["order"]["contact"]["phone"],
               order_detail["order"]["trip"]["id"],
               order_detail["order"]["date"],
               order_detail["order"]["time"],
               str(order_detail["order"]["price"]),
           )
           OrderModel.create_order(order_data)

           if payment_status == "PAID":
               payment_data = (
                   tappay_result["order_number"],
                   tappay_result["transaction_time_millis"],
                   payment_status,
                   tappay_result["acquirer"],
                   tappay_result["rec_trade_id"],
                   tappay_result["bank_transaction_id"],
                   tappay_result["card_identifier"],
                   tappay_result["card_info"]["last_four"],
                   tappay_result["merchant_id"],
                   tappay_result["auth_code"]
               )
               OrderModel.create_payment(payment_data)

           return {
               "number": order_number,
               "payment": {
                   "status": 0 if tappay_result["status"] == 0 else 1,
                   "message": "付款成功" if tappay_result["status"] == 0 else "付款失敗"
               }
           }
       except Exception as e:
           print(f"[create_order_and_payment] error: {str(e)}")
           raise

   @staticmethod
   def create_order(order_data: Tuple) -> None:
        try:
            query = """
            INSERT INTO orders (
                order_number, payment_status, user_name, user_email, contact_name, 
                contact_email, contact_phone, attraction_id, order_date, order_time, order_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
            """
            execute_update(query, order_data)
        except Exception as e:
            print(f"[create_order] error: {str(e)}")
            raise

   @staticmethod
   def create_payment(payment_data: Tuple) -> None:
        try:
            query = """
            INSERT INTO payments (
                order_number, transaction_time_millis, payment_status, acquirer,
                rec_trade_id, bank_transaction_id, card_identifier, card_last_four,
                merchant_id, auth_code
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_update(query, payment_data)
        except Exception as e:
            print(f"[create_payment] error: {str(e)}")
            raise

   @staticmethod
   def get_order(order_number: str) -> Optional[Tuple]:
        try:
            query = """
            SELECT
                orders.order_number,
                orders.payment_status,
                orders.user_email,
                orders.contact_name,
                orders.contact_email,
                orders.contact_phone,
                orders.attraction_id,
                orders.order_date,
                orders.order_time,
                orders.order_price,
                attractions.name AS attraction_name,
                attractions.address AS attraction_address,
                attractions.images AS attraction_image
            FROM orders 
            JOIN attractions ON orders.attraction_id = attractions.attraction_id
            WHERE orders.order_number = %s
            """
            result = execute_query(query, (order_number,))
            return result[0] if result else None
        except Exception as e:
            print(f"[get_order] error: {str(e)}")
            raise
       

   @staticmethod
   def get_user_info_in_dict(email: str) -> Optional[Dict]:
       query = "SELECT user_id, name, email FROM users WHERE email = %s"
       result = execute_query(query, (email,))
       if result:
           return {
               "user_id": result[0][0],
               "name": result[0][1],
               "email": result[0][2]
           }
       return None

   @staticmethod
   def clear_cart(user_id: str) -> bool:
       try:
           query = """
           UPDATE carts
           SET attraction_id = NULL,
               cart_date = NULL,
               cart_time = NULL,
               cart_price = NULL
           WHERE user_id = %s
           """
           execute_update(query, (user_id,))
           return True
       except Exception as e:
           print(f"[clear_cart] error {e}")
           return False