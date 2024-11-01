from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BookingModel

class BookingSerializer(serializers.Serializer):
    attractionId = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.CharField()
    price = serializers.IntegerField()

    def validate(self, data):
        time_slot_prices = {"morning": 2000, "afternoon": 2500}
        
        if data["time"] not in time_slot_prices:
            raise serializers.ValidationError("Invalid time slot")
        elif data["price"] != time_slot_prices[data["time"]]:
            raise serializers.ValidationError(f"Incorrect price for {data["time"]} slot")
        return data

@api_view(["GET", "POST", "DELETE"])
def booking_view(request):
    """Router"""
    handlers = {
        "GET": get_order,
        "POST": post_order,
        "DELETE": delete_order
    }
    
    handler = handlers.get(request.method)
    if not handler:
        return Response(
            {"error": True, "message": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
        
    return handler(request)

def get_order(request):
    try:
        authorization = request.headers.get("Authorization")
        user_id = BookingModel.get_user_id_from_token(authorization)
        if user_id is None:
            return Response(
                {"error": True, "message": "Not logged in."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        cart_detail = BookingModel.get_cart_details(user_id)
        if not cart_detail:
            return Response({"data": None})
        return Response({"data": cart_detail})
    
    except ValueError as e: 
        return Response(
            {"error": True, "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"[get_cart] error {e}")
        return Response(
            {"error": True, "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def post_order(request):
    try:
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": True, "message": f"建立失敗，輸入不正確: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        authorization = request.headers.get("Authorization")
        user_id = BookingModel.get_user_id_from_token(authorization)
        if user_id is None:
            return Response(
                {"error": True, "message": "Not logged in."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if BookingModel.create_new_cart(user_id, serializer.validated_data):
            return Response(
                {"ok": True, "message": "成功加入購物車"}
            )
    except ValueError as e: 
        return Response(
            {"error": True, "message": str(e)},
            status=status.HTTP_403_FORBIDDEN
        )

    except Exception as e:
        print(f"[create_cart] error: {e}")
        return Response(
            {"error": True, "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def delete_order(request):
    try:
        authorization = request.headers.get("Authorization")
        user_id = BookingModel.get_user_id_from_token(authorization)
        if user_id is None:
            return Response(
                {"error": True, "message": "Not logged in."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if BookingModel.clear_cart(user_id):
            return Response(
                {"ok": True, "message": "刪除購物車裡的項目"}
            )
            
        return Response(
            {"error": True, "message": "Failed to delete booking"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        print(f"[clear_cart] error {e}")
        return Response(
            {"error": True, "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )