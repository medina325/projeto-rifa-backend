import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    DateTime,
    ForeignKey,
    Text,
    func
)
from sqlalchemy.dialects.sqlite import BLOB
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(30), primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    picture = Column(String(255))
    auth_provider = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    token = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
