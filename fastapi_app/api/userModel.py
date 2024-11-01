from data.database import get_cursor, conn_commit, conn_close
import bcrypt 
import re


# Model
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
        cursor, conn = get_cursor()
        try:
            hashed_password = UserModel.hash_password(password)
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            conn_commit(conn)
            return cursor.fetchone()
        except Exception as exception:
            print(f"[create_user] error: {str(exception)}")
            raise exception
        finally:
            conn_close(conn)

    @staticmethod
    def get_user_by_email(email: str):
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Exception as exception:
            print(f"[get_user_by_email] error: {str(exception)}")
            raise exception
        finally:
            conn_close(conn)

    @staticmethod
    def get_user_info(email: str):
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT user_id, name, email FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Exception as exception:
            print(f"[get_user_info] error: {str(exception)}")
            raise exception
        finally:
            conn_close(conn)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(UserModel.email_pattern.match(email))