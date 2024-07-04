from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import jwt

router = APIRouter()

SECRET_KEY = "secreeeeet"
ALGORITHM = "HS256"

def create_jwt_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=168)
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
        print(f"JWT更新 form update_jwt_payload:::{updated_token}")

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
        print(f"JWT 已更新，booking 已移除")
        return updated_token

    except jwt.PyJWTError as exception:
        print(f"JWT Error: {exception}")
        return None