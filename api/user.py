from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import jwt
import bcrypt 
from data.database import get_cursor, conn_commit, conn_close
from api.jwt_utils import create_jwt_token, SECRET_KEY, ALGORITHM
router = APIRouter()

class UserSignUp(BaseModel):
    name: str
    email: str
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str


# bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"),salt)
    return hashed.decode("utf-8")

def check_password(hashed_password: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# POST__SIGNUP
@router.post("/api/user")
async def signup_user(user: UserSignUp):
    cursor, conn = get_cursor()

    if user.name =="" or user.email == "" or user.password == "" :
        return JSONResponse(content={"error": True, "message": "Missing required fields"}, status_code=400)

    if "@" not in user.email:
        return JSONResponse(content={"error": True, "message": "電子信箱格式錯誤"}, status_code=400)

    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (user.email,))
        email_count = cursor.fetchone()[0]
        if email_count > 0: 
            raise HTTPException(status_code=400, detail={"error": True, "message": "電子信箱已被註冊"})

        hashed_password = hash_password(user.password)
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (user.name, user.email, hashed_password))
        conn_commit(conn)

        return JSONResponse(status_code=200, content={"ok": True, "message": "!!! User signed up successfully !!!"})
    

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)

    

# GET__USER-INFO
@router.get("/api/user/auth")
async def get_user_info(authorization: str = Header(...)):
    if authorization == "null": 
        print("未登入")
        return JSONResponse(content={"data": "null", "message":"No JWT checked from backend."})
    print("/api/user/auth 驗證")
    cursor, conn = get_cursor()
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()

        if user_data:
            user_info = {
                "id": user_data[0],
                "name": user_data[1],
                "email": user_data[2]
            }
            return JSONResponse(status_code=200, content={"ok": True, "data": user_info, "message": "User is found."})
        else:
            raise HTTPException(status_code=400, detail={"error": True, "message": "User not found."})

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})

    finally:
        conn_close(conn)



# PUT__SIGNIN
@router.put("/api/user/auth")
async def signin_user(user: UserSignIn, response: Response):
    cursor, conn = get_cursor()

    if user.email == "" or user.password == "":
        raise HTTPException(status_code=400, detail={"error": True, "message": "The logged-in user did not enter a username or password."})
    
    try: 
        cursor.execute("SELECT * FROM users WHERE email= %s", (user.email,))
        user_data = cursor.fetchone()
        if not user_data or not check_password(user_data[3], user.password):
            raise HTTPException(status_code=400, content={"error": True, "message": "The username or password is incorrect."})
        
        jwt_token = create_jwt_token(user.email)
        print(jwt_token)
        
        # response.set_cookie(key="jwt" ,value="jwt_token" ,httponly=True, )  待實作 access token 和 refresh token
        
        return JSONResponse(status_code=200, content={"ok": True, "message": "!!! User signed in successfully !!!", "token": jwt_token}, headers={"Authorization": f"Bearer {jwt_token}"})
    
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)



from fastapi import FastAPI, Response

app = FastAPI()

@router.get("/api/set-cookie")
def set_cookie(response: Response):
    print("hello")
    response.set_cookie(key="my_cookie", value="cookie_value", httponly=True)
    return {"message": "Cookie set successfully!"}

