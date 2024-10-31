# booking/views.py
from django.http import JsonResponse
import json
from pydantic import BaseModel, ValidationError
from datetime import date
from .models import BookingModel
from typing import List

# Pydantic Models for request validation
class BookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int

    def validate_booking(self) -> List[str]:
        time_slot_prices = {"morning": 2000, "afternoon": 2500}
        errors = []
        
        if self.time not in time_slot_prices:
            errors.append("Invalid time slot")
        elif self.price != time_slot_prices[self.time]:
            errors.append(f"Incorrect price for {self.time} slot")
        return errors

# Response helper
class BookingResponse:
    @staticmethod
    def error_response(status_code, message):
        return JsonResponse(
            {"error": True, "message": message}, 
            status=status_code
        )
    
    @staticmethod
    def ok_response(status_code=200, data=None, message=None):
        content = {"ok": True}
        if data is not None:
            content["data"] = data
        if message is not None:
            content["message"] = message
        return JsonResponse(content, status=status_code)

# Views
def booking_view(request):
    if request.method == 'GET':
        try:
            authorization = request.headers.get('Authorization')
            user_id = BookingModel.get_user_id_from_token(authorization)
            if user_id is None:
                return BookingResponse.error_response(401, "Not logged in.")

            cart_detail = BookingModel.get_cart_details(user_id)
            if not cart_detail:
                return BookingResponse.ok_response(data=None)
            return BookingResponse.ok_response(data=cart_detail)
        except ValueError as e: 
            return BookingResponse.error_response(401, str(e))
        except Exception as e:
            print(f"[get_order] error {e}")
            return BookingResponse.error_response(500, str(e))

    elif request.method == 'POST':
        try:
            authorization = request.headers.get('Authorization')
            user_id = BookingModel.get_user_id_from_token(authorization)
            if user_id is None:
                return BookingResponse.error_response(403, "Not logged in.")

            # Pydantic validation
            try:
                booking_data = json.loads(request.body)
                booking = BookingInfo(**booking_data)
            except ValidationError as ve:
                error_messages = "; ".join(str(error) for error in ve.errors())
                return BookingResponse.error_response(400, f"建立失敗，輸入不正確: {error_messages}")

            # Business logic validation
            errors = booking.validate_booking()
            if errors:
                return BookingResponse.error_response(400, f"建立失敗，輸入不正確: {'; '.join(errors)}")

            if BookingModel.create_new_cart(user_id, booking):
                return BookingResponse.ok_response(message="成功加入購物車")
            return BookingResponse.error_response(500, "Failed to create booking")

        except Exception as e:
            print(f"[post_order] error: {e}")
            return BookingResponse.error_response(500, "Internal server error")

    elif request.method == 'DELETE':
        try:
            authorization = request.headers.get('Authorization')
            user_id = BookingModel.get_user_id_from_token(authorization)
            if user_id is None:
                return BookingResponse.error_response(403, "Not logged in.")

            if BookingModel.clear_cart(user_id):
                return BookingResponse.ok_response(message="刪除購物車裡的項目")
            return BookingResponse.error_response(500, "Failed to delete booking")

        except Exception as e:
            print(f"[delete_order] error {e}")
            return BookingResponse.error_response(500, "Internal server error")