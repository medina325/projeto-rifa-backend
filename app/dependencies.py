from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Rifa
from app.security import (
    is_token_valid,
    get_user_from_token,
    credentials_exception
)
oauth2_google_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={'openid': '', 'email': '', 'profile': ''},
)

async def get_current_user(
    token: str = Depends(oauth2_google_scheme),
    db: Session = Depends(get_db)
) -> User:
    if is_token_valid(token, db):
        return get_user_from_token(db, token)
    raise credentials_exception

async def get_rifa(
    rifa_id: int,
    db: Session = Depends(get_db)
) -> Rifa | None:
    db_rifa = db.query(Rifa).filter(Rifa.rifa_id == rifa_id).first()
    if db_rifa is None:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")
    return db_rifa

async def get_user_rifas(
    user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 3,
    db: Session = Depends(get_db)
) -> list[Rifa] | None:
    db_rifa = db.query(Rifa) \
        .filter(Rifa.criador_id == user.id) \
        .offset(skip) \
        .limit(limit) \
        .all()
    if db_rifa is None:
        raise HTTPException(status_code=404, detail="Usuário atual não possui rifas")
    return db_rifa
