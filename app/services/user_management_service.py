import logging
from sqlalchemy.orm import Session
from app.schemas import UserDB
from app.models import User, RevokedToken

logger = logging.getLogger(__name__)

def insert_user_into_db(user_data: UserDB, db: Session):
    user = User(
        id=user_data.id,
        username=user_data.name,
        email=user_data.email,
        first_name=user_data.given_name,
        last_name=user_data.family_name,
        picture=str(user_data.picture),
    )
    
    try:
        db.add(user)
        db.commit()
        logger.info(f"User created successfully with id: {user.id}")
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise

def logout_user_jwt(token: str, db: Session):
    try:
        revoked_token = RevokedToken(token=token)
        db.add(revoked_token)
        db.commit()
    except Exception as e:
        logger.error(f"Não foi possível revogar o token: {e}")
        db.rollback()
