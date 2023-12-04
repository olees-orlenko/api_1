from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from config import redis_url

from .auth import SECRET_KEY, AuthHandler
from .database import create_user, get_db, get_user
from .schemas import CreateUserSchema, Token, UserLoginSchema

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30
auth_handler = AuthHandler(secret_key=SECRET_KEY, redis_url=redis_url)


@router.post("/create/", response_model=CreateUserSchema, tags=["Auth"])
def create_user_endpoint(user: CreateUserSchema, session: Session = Depends(get_db)):
    db_user = create_user(user, session)
    return db_user


@router.post("/login/", response_model=Token, tags=["Auth"])
def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if db_user is None or not auth_handler.verify_password(
        user.hashed_password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_handler.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout/", tags=["Auth"])
def logout(response: Response, token: str = Depends(auth_handler.get_token)):
    auth_handler.invalidate_token(token)
    return {"message": "Successfully logged out"}
