from datetime import datetime, timedelta

import jwt
import redis
from fastapi import Cookie
from passlib.context import CryptContext

from config import REDIS_HOST, REDIS_PASS, REDIS_PORT

from .database import User

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
REDIS_URL = f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}"


class AuthHandler:
    def __init__(self, secret_key, redis_url):
        self.secret_key = secret_key
        self.redis_db = redis.StrictRedis.from_url(REDIS_URL)

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def verify_user_password(self, user: User, plain_password: str) -> bool:
        return self.verify_password(plain_password, user.hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        self.redis_db.setex(encoded_jwt, timedelta(minutes=30), "invalid")
        return encoded_jwt

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def invalidate_token(self, token):
        if token is not None:
            self.redis_db.delete(token)

    def get_token(self, token: str = Cookie(None)):
        if token is not None and self.redis_db.exists(token):
            return token
        else:
            return None
