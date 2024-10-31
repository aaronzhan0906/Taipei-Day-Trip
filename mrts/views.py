from django.http import JsonResponse
from .models import MRTModel

class MRTView:
    @staticmethod
    def ok_response(data=None):
        return JsonResponse(data)
    
    @staticmethod
    def error_response(status_code, message):
        return JsonResponse(
            {"error": True, "message": message}, 
            status=status_code
        )

def get_mrts(request):
    try:
        sorted_mrts_names = MRTModel.get_sorted_mrts()
        return MRTView.ok_response({"data": sorted_mrts_names})
    except Exception as e:
        return MRTView.error_response(500, str(e))