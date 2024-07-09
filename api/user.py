from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from data.database import get_cursor, conn_commit, conn_close
from api.jwt_utils import create_jwt_token, SECRET_KEY, ALGORITHM
import jwt
import bcrypt 
import re


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
    def create_user(name: str, email: str, password: str):
        cursor, conn = get_cursor()
        try:
            hashed_password = UserModel.hash_password(password)
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            conn_commit(conn)
            return cursor.fetchone()
        except Exception as exception:
            raise exception
        finally:
            conn_close(conn)

    @staticmethod
    def get_user_by_email(email: str):
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Exception as exception:
            raise exception
        finally:
            conn_close(conn)

            

    @staticmethod
    def get_user_info(email: str):
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT user_id, name, email FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Exception as exception:
            raise exception
        finally:
            conn_close(conn)



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
    def ok_response(status_code: int, message: str, data: dict = None, token: str = None):
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
    try:
        if not all([user.name, user.email, user.password]):
            return UserView.error_response(400, "Missing required fields")

        if not UserModel.is_valid_email(user.email):
            return UserView.error_response(400, "電子信箱格式錯誤")

        if UserModel.get_user_by_email(user.email):
            return UserView.error_response(400, "電子信箱已被註冊")

        UserModel.create_user(user.name, user.email, user.password)
        return UserView.ok_response(200, "!!! User signed up successfully !!!")
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})

@router.get("/api/user/auth")
async def get_user_info(authorization: str = Header(...)):
    if authorization == "null":
            return UserView.error_response(400, "No JWT checked from backend.")
    
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        user_data = UserModel.get_user_info(email)
        if user_data:
            user_info = {
                "user_id": user_data[0],
                "name": user_data[1],
                "email": user_data[2]
            }
            return UserView.ok_response(200, "User is found.", user_info)
        else:
            return UserView.error_response(400, "User not found.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})

@router.put("/api/user/auth")
async def signin_user(user: UserSignIn):
    if not all([user.email, user.password]):
        return UserView.error_response(400, "The logged-in user did not enter a username or password.")
    
    try:
        user_data = UserModel.get_user_by_email(user.email)
        if not user_data or not UserModel.check_password(user_data[3], user.password):
            return UserView.error_response(400, "The username or password is incorrect.")

        jwt_token = create_jwt_token(user.email)
        return UserView.ok_response(200, "!!! User signed in successfully !!!", token=jwt_token)
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})