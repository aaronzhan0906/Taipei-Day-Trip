from django.db import connection

class MRTModel:
    @staticmethod
    def get_sorted_mrts():
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT mrt FROM taipei_attractions.sorted_mrt_attraction_counts;")
                sorted_mrts_names = [mrt[0] for mrt in cursor.fetchall() if mrt[0]]
                return sorted_mrts_names
            except Exception as e:
                print(f"Error in get_sorted_mrts: {e}")
                raise