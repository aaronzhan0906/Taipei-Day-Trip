import os
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)


db_config = {
    "host": os.getenv("DB_HOST"),      
    "user": os.getenv("DB_USER"),      
    "password": os.getenv("DB_PASSWORD"), 
    "database": os.getenv("DB_NAME"), 
}

db_pool = MySQLConnectionPool(
    pool_name="mysql_pool",
    pool_size=30,
    pool_reset_session=True, # Resets the session state when a connection is taken from the pool
    **db_config # Database configuration passed as keyword arguments
)

print("Connection pool created.")

def execute_query(query, params=None):
    """執行查詢操作"""
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"查詢執行錯誤: {str(e)}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_update(query, params=None):
    """execute update operation"""
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"更新執行錯誤: {str(e)}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

