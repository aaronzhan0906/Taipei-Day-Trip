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
    def create_jwt_token(email: str, user_id: str, name: str) -> str:
        payload = {
            "sub": email,
            "user_id": user_id,
            "name": name,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_TIME),
            "type": "access"
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def confirm_same_user_by_jwt(token: str, user_email: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload["sub"] == user_email
        except (jwt.ExpiredSignatureError, jwt.PyJWTError):
            return False
    
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
    def get_user_id(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload["user_id"]
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
        
    