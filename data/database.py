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

def get_cursor():
    conn = db_pool.get_connection()
    cursor = conn.cursor()
    return cursor, conn

def conn_commit(conn):
    conn.commit()

def conn_close(conn):
    try:
        if conn.is_connected():
            conn.close()
    except Exception as event:
        print("Error closing connection:", event)