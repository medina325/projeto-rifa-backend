import logging
from sqlalchemy.orm import Session
from app.schemas import UserDB
from app.models import User

logger = logging.getLogger(__name__)

def insert_user_into_db(user_data: UserDB, db: Session):
    user = User(**user_data)
    
    try:
        db.add(user)
        db.commit()
        logger.info(f"User created successfully with id: {user.id}")
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise
