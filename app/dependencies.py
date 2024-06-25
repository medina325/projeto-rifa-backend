from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
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
