import jwt
import datetime
from datetime import datetime as datetime_m, timedelta
from .config import SECRET_KEY
from sqlalchemy.orm import Session
from app.models import RevokedToken, User
from app.schemas import TokenData
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)

unauthorized_redirect = RedirectResponse(
    'http://localhost:5173',
    status_code=status.HTTP_401_UNAUTHORIZED,
    headers={'Content-Type': 'text/html; charset=utf-8'}
)

def get_authorized_redirect(bearer_token: str):
    response = RedirectResponse(
        f'http://localhost:5173?token={bearer_token}',
        headers={'Content-Type': 'text/html; charset=utf-8'}
    )
    return response

def user_exists(db: Session, _id: str):
    return db.query(User).filter(User.id == _id).first() is not None

def create_access_token(
    sub: str,
    expires_delta: timedelta = timedelta(minutes=15)
):
    expire_date = datetime_m.now(datetime.timezone.utc) + expires_delta
    encoded_jwt = jwt.encode({
        'sub': sub,
        'exp': expire_date.timestamp()    
    }, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return TokenData(**payload)

def get_user_from_token(db: Session, token: str) -> User:
    token_data = decode_token(token)
    return (
        db.query(User)
        .filter(User.id == token_data.sub)
        .first()
    )
    
def is_token_not_expired(token: str) -> bool:
    token_data = decode_token(token)
    current_timespamp = datetime_m.now(datetime.timezone.utc).timestamp()
    return token_data.exp > current_timespamp

def is_token_not_revoked(db: Session, token: str) -> bool:
    revoked_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
    )
    return revoked_token is None

def is_token_valid(db: Session, token: str) -> bool:
    try:
        return is_token_not_expired(token) and is_token_not_revoked(db, token)
    except jwt.JWTError:
        raise credentials_exception