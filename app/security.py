import jwt
import datetime
import logging
from datetime import datetime as datetime_m, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import RevokedToken
from app.config import get_env_var
from app.schemas import TokenData
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = get_env_var('SECRET_KEY')

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)

unauthorized_redirect = RedirectResponse(
    'http://localhost:5173', headers={'Content-Type': 'text/html; charset=utf-8'}
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_authorized_redirect(bearer_token: str):
    return RedirectResponse(
        f'http://localhost:5173/login?token={bearer_token}',
        headers={'Content-Type': 'text/html; charset=utf-8'},
    )


def create_access_token(sub: str, expires_delta: timedelta = timedelta(minutes=15)):
    expire_date = datetime_m.now(datetime.timezone.utc) + expires_delta
    encoded_jwt = jwt.encode(
        {'sub': sub, 'exp': expire_date.timestamp()}, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return TokenData(**payload)


def is_token_not_expired(token: str) -> bool:
    token_data = decode_token(token)
    current_timespamp = datetime_m.now(datetime.timezone.utc).timestamp()
    return token_data.exp > current_timespamp


def is_token_not_revoked(db: Session, token: str) -> bool:
    revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    return revoked_token is None


def is_token_valid(token: str, db: Session) -> bool:
    try:
        return is_token_not_expired(token) and is_token_not_revoked(db, token)
    except jwt.PyJWTError:
        raise credentials_exception


def logout_user_jwt(token: str, db: Session):
    try:
        revoked_token = RevokedToken(token=token)
        db.add(revoked_token)
        db.commit()
    except Exception as e:
        logger.error(f"Não foi possível revogar o token: {e}")
        db.rollback()


def logout(token: str, db: Session):
    if not is_token_valid(token, db):
        return {'Token já foi invalidado'}

    logout_user_jwt(token, db)
    return {'Usuário deslogado, JWT invalidado'}
