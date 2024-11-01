from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MRTModel

@api_view(["GET"])
def get_mrts(request):
    try:
        sorted_mrts_names = MRTModel.get_sorted_mrts()
        return Response({"data": sorted_mrts_names})
    except Exception as e:
        return Response(
            {"error": True, "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )