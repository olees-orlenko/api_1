from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi_users.db import SQLAlchemyBaseUserTable
from passlib.context import CryptContext
from sqlalchemy import Boolean, Integer, String, create_engine, or_
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

from .schemas import CreateUserSchema

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base: DeclarativeMeta = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)


def hash_password(hashed_password: str) -> str:
    return pwd_context.hash(hashed_password)


def create_user(user: CreateUserSchema, session: Session):
    existing_user = (
        session.query(User)
        .filter(or_(User.email == user.email, User.username == user.username))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email/username already exists",
        )

    hashed_password = hash_password(user.hashed_password)
    db_user = User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
