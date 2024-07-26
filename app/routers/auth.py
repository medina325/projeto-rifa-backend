import uuid
import app.services.user_management_service as user_service
import app.security as security
from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import BaseUser, UserDB, Token, RegisterUser, LoginUser
from app.database import get_db
from app.dependencies import oauth2_google_scheme

router = APIRouter()


@router.post("/register", response_model=BaseUser)
async def register(
    user: RegisterUser,
    db: Annotated[Session, Depends(get_db)],
):
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail=f"Nome de usuário {user.username} já registrado"
        )
    user.password_hash = security.hash_password(user.password)
    db_user = UserDB(
        id=str(uuid.uuid4()),
        **user.model_dump(),
    )

    return user_service.insert_user_into_db(user_data=db_user, db=db)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: LoginUser,
    db: Annotated[Session, Depends(get_db)],
):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        sub=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_google_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    return security.logout(token, db)
