# booking/models.py
from django.db import connection
import jwt
from django.conf import settings
from typing import Optional, Dict, Any

class BookingModel:
   @staticmethod
   def get_user_id_from_token(authorization: str) -> int:
        if authorization == "null":
            raise ValueError("Not logged in.")
        
        try:
            token = authorization.split()[1]
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload["user_id"]
        except IndexError:
            raise ValueError("Invalid authorization header")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except KeyError:
            raise ValueError("Token payload is invalid")

   @staticmethod
   def get_cart_details(user_id):
       with connection.cursor() as cursor:
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
           
               return {
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
           except Exception as e:
               print(f"[get_cart_details] error: {e}")
               return None

   @staticmethod
   def create_new_cart(user_id, booking):
       with connection.cursor() as cursor:
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
               cursor.execute(query, (
                   user_id, 
                   booking.attractionId,
                   booking.date,
                   booking.time,
                   booking.price
               ))
               connection.commit()
               return True
           except Exception as e:
               print(f"[create_new_cart] error: {e}")
               return False

   @staticmethod
   def clear_cart(user_id: int) -> bool:
       with connection.cursor() as cursor:
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
               connection.commit()
               return True
           except Exception as e:
               print(f"[clear_cart] error {e}")
               return False