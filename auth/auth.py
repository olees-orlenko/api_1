from datetime import datetime, timedelta

import jwt
from fastapi import Cookie
from passlib.context import CryptContext

from .database import DATABASE_URL, User

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def verify_user_password(user: User, plain_password: str) -> bool:
    return verify_password(plain_password, user.hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class AuthHandler:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def invalidate_token(self, token):
        pass

    def get_token(self, token: str = Cookie(None)):
        return token
