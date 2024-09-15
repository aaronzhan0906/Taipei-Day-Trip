from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import jwt
import os
from dotenv import load_dotenv

router = APIRouter()

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")

load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_TIME"))

class JWTHandler:


    @staticmethod
    def create_jwt_token(email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_TIME),
            "type": "access"
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def update_jwt_payload(token: str, new_data: dict) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if "booking" in new_data:
                payload["booking"] = new_data["booking"]

            payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_TIME)
            updated_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            print(f"JWT更新 form update_jwt_payload")

            return updated_token

        except jwt.PyJWTError as exception:
            print(f"JWT Error: {exception}")
            return None

    @staticmethod
    def remove_booking_from_jwt(token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            del payload["booking"]
            payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_TIME)
            updated_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            print(f"JWT 已更新，booking 已移除 from remove_booking_from_jwt")
            return updated_token

        except jwt.PyJWTError as exception:
            print(f"JWT Error: {exception}")
            return None
    
    @staticmethod
    def confirm_same_user_by_jwt(token: str, user_email: str) -> bool:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["sub"] = user_email
        return True
    
    @staticmethod
    def get_user_email(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def is_token_expired(token: str) -> bool:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.PyJWTError:
            return True
        
    