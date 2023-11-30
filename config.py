import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")
redis_port = os.environ.get("redis_port", "6379")
redis_host = os.environ.get("redis_port", "localhost")
