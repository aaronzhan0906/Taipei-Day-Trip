from django.db import connection
import redis
import os 
import json

class AttractionModel:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_client = redis.Redis(host=redis_host, port=6379, db=0)

    @staticmethod
    def get_attractions(limit, offset, filters, params):
        cache_key = f"attractions:{limit}:{offset}:{json.dumps(filters)}:{json.dumps(params)}"
        cached_data = AttractionModel.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        with connection.cursor() as cursor:
            base_query = "SELECT * FROM attractions"
            if filters:
                base_query += " WHERE " + " AND ".join(filters)
            base_query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            cursor.execute(base_query, params)
            attractions = cursor.fetchall()

        AttractionModel.redis_client.setex(cache_key, 259200, json.dumps(attractions))
        return attractions

    @staticmethod
    def get_total_count(filters, params):
        cache_key = f"attractions_count:{json.dumps(filters)}:{json.dumps(params)}"
        cached_count = AttractionModel.redis_client.get(cache_key)
        if cached_count:
            return int(cached_count)

        with connection.cursor() as cursor:
            total_count_query = "SELECT COUNT(*) FROM attractions"
            if filters:
                total_count_query += " WHERE " + " AND ".join(filters)
            cursor.execute(total_count_query, params)
            count = cursor.fetchone()[0]

        AttractionModel.redis_client.setex(cache_key, 259200, str(count))
        return count

    @staticmethod
    def get_attraction_by_id(attraction_id):
        cache_key = f"attraction:{attraction_id}"
        cached_attraction = AttractionModel.redis_client.get(cache_key)
        
        if cached_attraction:
            return json.loads(cached_attraction)
        
        with connection.cursor() as cursor:
            query = "SELECT * FROM attractions WHERE attraction_id = %s"
            cursor.execute(query, (attraction_id,))
            attraction = cursor.fetchone()

        if attraction:
            AttractionModel.redis_client.setex(cache_key, 259200, json.dumps(attraction))
        return attraction