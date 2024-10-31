from django.http import JsonResponse
from .models import AttractionModel
from mrts.models import MRTModel

class AttractionView:
    @staticmethod
    def attraction_to_dict(attraction):
        return {
            "id": attraction[0],
            "name": attraction[1],
            "category": attraction[2],
            "description": attraction[3],
            "address": attraction[4],
            "transport": attraction[5],
            "mrt": attraction[6],
            "latitude": attraction[7],
            "longitude": attraction[8],
            "images": (lambda images_raw: 
                images_raw.strip('"').replace('\\\\','\\').split('\\n') if images_raw else []
            )(attraction[9])
        }
    
    

    @staticmethod
    def get_attractions(request):
        try:
            page = int(request.GET.get('page', 0))
            keyword = request.GET.get('keyword')
            
            print(keyword)
            limit = 12
            offset = page * limit
            filters = []
            params = []
        
            mrt_stations = MRTModel.get_sorted_mrts()

            if keyword:
                if keyword in mrt_stations: 
                    filters.append("mrt = %s")
                    params.append(keyword) 
                else:
                    filters.append("name LIKE %s")
                    params.append(f"%{keyword}%")
            
            total_count = AttractionModel.get_total_count(filters, params.copy())
            attractions_tuple = AttractionModel.get_attractions(limit, offset, filters, params)
            attractions_list = [AttractionView.attraction_to_dict(attraction) 
                            for attraction in attractions_tuple]
            next_page = page + 1 if total_count >= offset + limit else None

            return JsonResponse({
                "nextPage": next_page,
                "data": attractions_list
            })
        
        except Exception as e:
            print(e)
            return JsonResponse({
                "error": True,
                "message": str(e)
            }, status=500)

    @staticmethod
    def get_attraction(request, attraction_id):
        try:
            attraction = AttractionModel.get_attraction_by_id(attraction_id)

            if attraction:
                attraction_dict = AttractionView.attraction_to_dict(attraction)
                return JsonResponse({"data": attraction_dict})
            else:
                return JsonResponse({
                    "error": True,
                    "message": "Attraction number is incorrect."
                }, status=400)
        
        except Exception as e:
            return JsonResponse({
                "error": True, 
                "message": str(e)
            }, status=500)