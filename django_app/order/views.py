from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.JWTHandler import JWTHandler
from .models import OrderModel



class OrderSerializer(serializers.Serializer):
   price = serializers.IntegerField()
   trip = serializers.DictField()  
   date = serializers.CharField() 
   time = serializers.CharField()
   contact = serializers.DictField()

class OrderDetailSerializer(serializers.Serializer):
   order = OrderSerializer()
   prime = serializers.CharField()

class OrderResponse:
   @staticmethod
   def format_order_data(order):
       return {
           "number": order[0],
           "price": int(order[9]),
           "trip": {
               "attraction": {
                   "id": order[6],
                   "name": order[10],
                   "address": order[11],
                   "image": 'https://' + order[12].strip('"').split('https://')[1].split('\\n')[0]
               },
               "date": order[7],
               "time": order[8]
           },
           "contact": {
               "name": order[3],
               "email": order[4],
               "phone": order[5]
           },
           "status": 0
       }


@api_view(["POST"])
def create_order(request):
   try:
       serializer = OrderDetailSerializer(data=request.data)
       if not serializer.is_valid():
           return Response(
               {"error": True, "message": str(serializer.errors)},
               status=status.HTTP_400_BAD_REQUEST 
           )
      
       order_detail = serializer.validated_data

       authorization = request.headers.get("Authorization")
       if authorization == "null":
           return Response(
               {"error": True, "message": "Not logged in."}, 
               status=status.HTTP_401_UNAUTHORIZED
           )
      
       if not OrderModel.validate_phone(order_detail["order"]["contact"]["phone"]):
           return Response(
               {"error": True, "message": "訂單建立失敗，手機號碼格式錯誤"},
               status=status.HTTP_400_BAD_REQUEST
           )
      
       if not OrderModel.validate_email(order_detail['order']['contact']["email"]):
           return Response(
               {"error": True, "message": "訂單建立失敗，電子信箱格式錯誤"},
               status=status.HTTP_400_BAD_REQUEST
           )
      
       token = authorization.split()[1]
       user_email = JWTHandler.get_user_email(token)
       user_info = OrderModel.get_user_info_in_dict(user_email)
       order_number = OrderModel.generate_order_number()
      
       from asgiref.sync import async_to_sync
       tappay_result = async_to_sync(OrderModel.process_tappay_payment)(
           order_detail, 
           order_number
       )

       response_data = OrderModel.create_order_and_payment(
            order_detail, 
            user_info, 
            order_number, 
            tappay_result
        )
      
       OrderModel.clear_cart(user_info["user_id"])
       return Response({"ok": True, "data": response_data})

   except KeyError as e:
       print(f"[TapPay response missing key]: {str(e)}")
       return Response(
           {"error": True, "message": f"[TapPay response missing key]: {str(e)}"},
           status=status.HTTP_500_INTERNAL_SERVER_ERROR
       )
   except Exception as e:
       print(f"[create_order] error: {str(e)}")
       return Response(
           {"error": True, "message": str(e)},
           status=status.HTTP_500_INTERNAL_SERVER_ERROR
       )

@api_view(["GET"])
def get_order(request, order_number):
   try:
       authorization = request.headers.get("Authorization")
       if authorization == "null":
           return Response(
               {"error": True, "message": "Not logged in."},
               status=status.HTTP_401_UNAUTHORIZED
           )
      
       order = OrderModel.get_order(order_number)
       if not order:
           return Response(
               {"error": True, "message": "Order not found."},
               status=status.HTTP_404_NOT_FOUND
           )
      
       token = authorization.split()[1]
       if not JWTHandler.confirm_same_user_by_jwt(token, order[2]):
           return Response(
               {"error": True, "message": "Unauthorized access to order."},
               status=status.HTTP_403_FORBIDDEN
           )
      
       formatted_order_data = OrderResponse.format_order_data(order)
       return Response({"ok": True, "data": formatted_order_data})
      
   except Exception as e:
       print(f"[get_order] error: {str(e)}")
       return Response(
           {"error": True, "message": str(e)},
           status=status.HTTP_500_INTERNAL_SERVER_ERROR
       )