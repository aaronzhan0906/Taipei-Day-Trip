from fastapi import APIRouter, Header
from pydantic import BaseModel
from api.JWTHandler import JWTHandler, SECRET_KEY, ALGORITHM
from api.userModel import UserModel
from api.userView import UserView
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError




# Controller
router = APIRouter()

class UserSignUp(BaseModel):
    name: str
    email: str
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str

@router.post("/api/user")
async def signup_user(user: UserSignUp):
    if not all([user.name, user.email, user.password]):
            return UserView.error_response(400, "Missing required fields")
    try:
        if not UserModel.is_valid_email(user.email):
            return UserView.error_response(400, "電子信箱格式錯誤")

        if UserModel.get_user_by_email(user.email):
            return UserView.error_response(400, "電子信箱已被註冊")

        UserModel.create_user(user.name, user.email, user.password)
        return UserView.ok_response(200, message="!!! User signed up successfully !!!")
    except Exception as exception:
        print(f"[signup_user] error {exception}")
        return UserView.error_response(500, str(exception))

@router.get("/api/user/auth")
async def get_user_info(authorization: str = Header(...)):
    if authorization == "null":
        return UserView.error_response(400, "No JWT checked from backend.")
    
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_info = {
            "user_id": payload.get("user_id"),
            "name": payload.get("name"),
            "email": payload.get("sub")
        }

        return UserView.ok_response(200, data=user_info, message="User is found.")
    except ExpiredSignatureError:
        print("[ExpiredSignatureError] Token has expired.")
        return UserView.error_response(400, "Token has expired.")
    except InvalidTokenError:
        print("[InvalidTokenError] Invalid token.")
        return UserView.error_response(400, "Invalid token.")
    except Exception as exception:
        print(f"[get_user_info] error {exception}")
        return UserView.error_response(500, str(exception))

@router.put("/api/user/auth")
async def signin_user(user: UserSignIn):
    if not all([user.email, user.password]):
        return UserView.error_response(400, "The logged-in user did not enter a username or password.")
    try:
        user_data = UserModel.get_user_by_email(user.email)
        if not user_data or not UserModel.check_password(user_data[3], user.password):
            return UserView.error_response(400, "The username or password is incorrect.")
        
        email = user_data[2]
        name = user_data[1]
        user_id = user_data[0]
        jwt_token = JWTHandler.create_jwt_token(email, str(user_id), name)
        return UserView.ok_response(200, message="!!! User signed in successfully !!!", token=jwt_token)
    except Exception as exception:
        print(f"[signin_user] error {exception}")
        return UserView.error_response(500, str(exception))