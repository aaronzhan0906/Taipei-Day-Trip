import re
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import bcrypt 
from data.database import get_cursor, conn_commit, conn_close
from api.jwt_utils import create_jwt_token, SECRET_KEY, ALGORITHM

# Model
class UserModel:
    email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def check_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_user(cursor, name: str, email: str, password: str):
        hashed_password = UserModel.hash_password(password)
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))

    @staticmethod
    def get_user_by_email(cursor, email: str):
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()

    @staticmethod
    def get_user_info(cursor, email: str):
        cursor.execute("SELECT user_id, name, email FROM users WHERE email = %s", (email,))
        return cursor.fetchone()

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(UserModel.email_pattern.match(email))

# View
class UserSignUp(BaseModel):
    name: str
    email: str
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str

class UserView:
    @staticmethod
    def error_response(status_code: int, message: str):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})

    @staticmethod
    def success_response(status_code: int, message: str, data: dict = None, token: str = None):
        content = {"ok": True, "message": message}
        if data:
            content["data"] = data
        if token:
            content["token"] = token
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return JSONResponse(status_code=status_code, content=content, headers=headers)

# Controller
router = APIRouter()

@router.post("/api/user")
async def signup_user(user: UserSignUp):
    cursor, conn = get_cursor()
    try:
        if not all([user.name, user.email, user.password]):
            return UserView.error_response(400, "Missing required fields")

        if not UserModel.is_valid_email(user.email):
            return UserView.error_response(400, "電子信箱格式錯誤")

        if UserModel.get_user_by_email(cursor, user.email):
            return UserView.error_response(400, "電子信箱已被註冊")

        UserModel.create_user(cursor, user.name, user.email, user.password)
        conn_commit(conn)
        return UserView.success_response(200, "!!! User signed up successfully !!!")
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    finally:
        conn_close(conn)

@router.get("/api/user/auth")
async def get_user_info(authorization: str = Header(...)):
    cursor, conn = get_cursor()
    try:
        if authorization == "null":
            return UserView.error_response(400, "No JWT checked from backend.")

        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        user_data = UserModel.get_user_info(cursor, email)
        if user_data:
            user_info = {
                "user_id": user_data[0],
                "name": user_data[1],
                "email": user_data[2]
            }
            return UserView.success_response(200, "User is found.", user_info)
        else:
            return UserView.error_response(400, "User not found.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    finally:
        conn_close(conn)

@router.put("/api/user/auth")
async def signin_user(user: UserSignIn):
    cursor, conn = get_cursor()
    try:
        if not all([user.email, user.password]):
            return UserView.error_response(400, "The logged-in user did not enter a username or password.")

        user_data = UserModel.get_user_by_email(cursor, user.email)
        if not user_data or not UserModel.check_password(user_data[3], user.password):
            return UserView.error_response(400, "The username or password is incorrect.")

        jwt_token = create_jwt_token(user.email)
        return UserView.success_response(200, "!!! User signed in successfully !!!", token=jwt_token)
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    finally:
        conn_close(conn)