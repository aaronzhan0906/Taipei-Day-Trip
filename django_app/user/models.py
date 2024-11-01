from django_app.database import execute_query, execute_update
import bcrypt 
import re

class UserModel:
    email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def check_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_user(name: str, email: str, password: str):
        try:
            hashed_password = UserModel.hash_password(password)
            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            params = (name, email, hashed_password)
            return execute_update(query, params)
        except Exception as exception:
            print(f"[create_user] error: {str(exception)}")
            raise exception

    @staticmethod
    def get_user_by_email(email: str):
        try:
            query = "SELECT * FROM users WHERE email = %s"
            params = (email,)
            result = execute_query(query, params)
            return result[0] if result else None
        except Exception as exception:
            print(f"[get_user_by_email] error: {str(exception)}")
            raise exception

    @staticmethod
    def get_user_info(email: str):
        try:
            query = "SELECT user_id, name, email FROM users WHERE email = %s"
            params = (email,)
            result = execute_query(query, params)
            return result[0] if result else None
        except Exception as exception:
            print(f"[get_user_info] error: {str(exception)}")
            raise exception

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(UserModel.email_pattern.match(email))