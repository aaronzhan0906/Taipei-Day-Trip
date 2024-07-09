from fastapi import *
from fastapi.responses import JSONResponse
from data.database import get_cursor, conn_commit, conn_close
from api.models.mrtsModel import MRTModel

# Model
class AttractionModel:
    @staticmethod
    def get_attractions_with_count(page, keyword):
        try:
            cursor, conn = get_cursor()
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
            
            total_count = AttractionModel._get_total_count(cursor, filters, params)
            attractions_tuple = AttractionModel._get_attractions(cursor, limit, offset, filters, params)
            
            conn_commit(conn)
            conn_close(conn)
            
            return attractions_tuple, total_count, limit
        except Exception as exception:
            raise exception

    @staticmethod
    def get_attraction_by_id(attraction_id):
        try:
            cursor, conn = get_cursor()
            query = "SELECT * FROM attractions WHERE attraction_id = %s"
            cursor.execute(query, (attraction_id,))
            attraction = cursor.fetchone()
            
            conn_commit(conn)
            conn_close(conn)
            
            return attraction
        except Exception as exception:
            raise exception

    @staticmethod
    def _get_attractions(cursor, limit, offset, filters, params):
        base_query = "SELECT * FROM attractions"
        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        base_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(base_query, params)
        return cursor.fetchall()

    @staticmethod
    def _get_total_count(cursor, filters, params):
        total_count_query = "SELECT COUNT(*) FROM attractions"
        if filters:
            total_count_query += " WHERE " + " AND ".join(filters)
        cursor.execute(total_count_query, params)
        return cursor.fetchone()[0]




# Controller
router = APIRouter()

@router.get("/api/attractions")
async def attractions(page: int = Query(0, ge=0), keyword: str = Query(None)):
    try:
        attractions_tuple, total_count, limit = AttractionModel.get_attractions_with_count(page, keyword)
        
        attractions_list = [AttractionView.attraction_to_dict(attraction) for attraction in attractions_tuple]
        next_page = page + 1 if total_count > (page + 1) * limit else None
        
        return AttractionView.attractions_response(next_page, attractions_list)
    
    except Exception as exception:
        return AttractionView.error_response(str(exception), 500)

@router.get("/api/attraction/{attractionId}")
async def attraction(attractionId: int):
    try:
        attraction = AttractionModel.get_attraction_by_id(attractionId)

        if attraction:
            attraction_dict = AttractionView.attraction_to_dict(attraction)
            return AttractionView.attraction_response(attraction_dict)
        else:
            return AttractionView.error_response("Attraction number is incorrect.", 400)
    
    except Exception as exception:
        return AttractionView.error_response(str(exception), 500)




# View
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
    def attractions_response(next_page, attractions_list):
        return JSONResponse(content={"nextPage": next_page, "data": attractions_list}, status_code=200)

    @staticmethod
    def attraction_response(attraction_dict):
        return JSONResponse({"data": attraction_dict}, status_code=200)

    @staticmethod
    def error_response(message, status_code):
        return JSONResponse(content={"error": True, "message": message}, status_code=status_code)