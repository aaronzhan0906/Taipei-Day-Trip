from utils.JWTHandler import JWTHandler, SECRET_KEY, ALGORITHM
from .models import UserModel
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from typing import Dict, Any

def error_response(status_code: int, message: str) -> JsonResponse:
    return JsonResponse(
        {"error": True, "message": message}, 
        status=status_code
    )

def ok_response(status_code: int, message: str, data: Dict[str, Any] = None, token: str = None) -> JsonResponse:
    content = {"ok": True, "message": message}
    if data:
        content["data"] = data
    if token:
        content["token"] = token
    response = JsonResponse(content, status=status_code)
    if token:
        response["Authorization"] = f"Bearer {token}"
    return response

@csrf_exempt
@require_http_methods(["POST"])
def signup_user(request):
    """
    POST /api/user
    """
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return error_response(400, "資料不完整，請確認所有欄位都已填寫")

        if not UserModel.is_valid_email(email):
            return error_response(400, "電子信箱格式錯誤")

        if UserModel.get_user_by_email(email):
            return error_response(400, "此電子信箱已被註冊")

        UserModel.create_user(name, email, password)
        return ok_response(201, "註冊成功")

    except json.JSONDecodeError:
        return error_response(400, "無效的請求格式")
    except Exception as e:
        print(f"[signup] error: {str(e)}")
        return error_response(500, "系統錯誤，請稍後再試")
    
@csrf_exempt
def handle_auth(request):
    if request.method == "GET":
        return get_user_info(request)
    elif request.method == "PUT":
        return signin_user(request)
    
    return error_response(405, "方法不允許")

@require_http_methods(["GET"])
def get_user_info(request):
    """
    GET /api/user/auth
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return error_response(401, "請先登入")

        if auth_header == "null":
            return error_response(401, "無效的認證令牌")
        
        token = auth_header.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_info = {
            "id": payload.get("user_id"),
            "name": payload.get("name"),
            "email": payload.get("sub")
        }

        return ok_response(200, "成功獲取用戶信息", data=user_info)

    except ExpiredSignatureError:
        print("[Auth] Token 已過期")
        return error_response(401, "登入已過期，請重新登入")
    except InvalidTokenError:
        print("[Auth] 無效的 Token")
        return error_response(401, "無效的認證令牌")
    except Exception as e:
        print(f"[get_user] error: {str(e)}")
        return error_response(500, "系統錯誤，請稍後再試")


@require_http_methods(["PUT"])
def signin_user(request):
    """
    PUT /api/user/auth
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        print(email, password)

        if not all([email, password]):
            return error_response(400, "請輸入電子信箱和密碼")

        user_data = UserModel.get_user_by_email(email)
        if not user_data or not UserModel.check_password(user_data[3], password):
            return error_response(401, "電子信箱或密碼錯誤")
        
        jwt_token = JWTHandler.create_jwt_token(
            email=user_data[2],
            user_id=str(user_data[0]),
            name=user_data[1]
        )
        print(jwt_token)
        return ok_response(200, "登入成功", token=jwt_token)

    except json.JSONDecodeError:
        return error_response(400, "無效的請求格式")
    except Exception as e:
        print(f"[login] error: {str(e)}")
        return error_response(500, "系統錯誤，請稍後再試")
