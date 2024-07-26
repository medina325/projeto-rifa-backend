import logging
import app.security as security
from sqlalchemy.orm import Session
from app.schemas import UserDB
from app.models import User

logger = logging.getLogger(__name__)


def insert_user_into_db(user_data: UserDB, db: Session):
    user = User(
        **user_data.model_dump(exclude='picture'),
        picture=user_data.picture and str(user_data.picture),
    )

    try:
        db.add(user)
        db.commit()
        logger.info(f"User created successfully with id: {user.id}")
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise
    return user


def user_exists(db: Session, _id: str):
    return db.query(User).filter(User.id == _id).first() is not None


def get_user_from_token(db: Session, token: str) -> User:
    token_data = security.decode_token(token)
    return db.query(User).filter(User.id == token_data.sub).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.password_hash):
        return False
    return user
