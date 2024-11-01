from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.JWTHandler import JWTHandler, SECRET_KEY, ALGORITHM
from .models import UserModel
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

@api_view(["POST"])
def signup_user(request):
    """
    POST /api/user
    """
    try:
        name = request.data.get("name")
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([name, email, password]):
            return Response(
                {"error": True, "message": "Missing required fields"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not UserModel.is_valid_email(email):
            return Response(
                {"error": True, "message": "電子信箱格式錯誤"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if UserModel.get_user_by_email(email):
            return Response(
                {"error": True, "message": "電子信箱已被註冊"},
                status=status.HTTP_400_BAD_REQUEST
            )

        UserModel.create_user(name, email, password)
        return Response(
            {"ok": True, "message": "User signed up successfully"},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        print(f"[signup] error: {str(e)}")
        return Response(
            {"error": True, "message": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET", "PUT"])
def handle_auth(request):
    """
    GET/PUT /api/user/auth
    """
    if request.method == "GET":
        return get_user_info(request)
    elif request.method == "PUT":
        return signin_user(request)

def get_user_info(request):
    """
    GET /api/user/auth
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                {"error": True, "message": "Not logged in"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if auth_header == "null":
            return Response(
                {"error": True, "message": "Invalid token"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        token = auth_header.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_info = {
            "id": payload.get("user_id"),
            "name": payload.get("name"),
            "email": payload.get("sub")
        }

        return Response({
            "ok": True,
            "message": "成功獲取用戶信息",
            "data": user_info
        })

    except ExpiredSignatureError:
        print("[ExpiredSignatureError] Token has expired.")
        return Response(
            {"error": True, "message": "Token has expired"},
            status=status.HTTP_403_FORBIDDEN
        )
    except InvalidTokenError:
        print("[InvalidTokenError] Invalid Token")
        return Response(
            {"error": True, "message": "Invalid token"},
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        print(f"[get_user_info] error: {str(e)}")
        return Response(
            {"error": True, "message": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def signin_user(request):
    """
    PUT /api/user/auth
    """
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([email, password]):
            return Response(
                {"error": True, "message": "The logged-in user did not enter a username or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_data = UserModel.get_user_by_email(email)
        if not user_data or not UserModel.check_password(user_data[3], password):
            return Response(
                {"error": True, "message": "The username or password is incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jwt_token = JWTHandler.create_jwt_token(
            email=user_data[2],
            user_id=str(user_data[0]),
            name=user_data[1]
        )

        response = Response({
            "ok": True,
            "message": "User logged in successfully",
            "token": jwt_token
        })
        response["Authorization"] = f"Bearer {jwt_token}"
        return response

    except Exception as e:
        print(f"[signin_user] error: {str(e)}")
        return Response(
            {"error": True, "message": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )