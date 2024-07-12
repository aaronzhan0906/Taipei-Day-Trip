from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import jwt

router = APIRouter()

SECRET_KEY = "secreeeeet"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 15/60  
REFRESH_TOKEN_EXPIRE_DAY = 30

def create_jwt_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "type": "access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(email: str) -> str:
    expire_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
    payload = {
        "sub": email,
        "exp": datetime.now(tz=timezone.utc) + expire_delta,
        "type": "refresh"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def update_jwt_payload(token: str, new_data: dict) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "booking" in new_data:
            payload["booking"] = new_data["booking"]

        payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=168)
        updated_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"JWT更新 form update_jwt_payload")

        return updated_token

    except jwt.PyJWTError as exception:
        print(f"JWT Error: {exception}")
        return None


def remove_booking_from_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        del payload["booking"]
        payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=168)
        updated_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"JWT 已更新，booking 已移除 from remove_booking_from_jwt")
        return updated_token

    except jwt.PyJWTError as exception:
        print(f"JWT Error: {exception}")
        return None
    
def confirm_same_user_by_jwt(token: str, user_email: str) -> bool:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    payload["sub"] = user_email
    return True
