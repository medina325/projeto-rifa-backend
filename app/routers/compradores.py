import logging
import uuid
import os
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pathlib import Path
from sqlalchemy.orm import Session
from app.config import get_env_var
from app.models import User, Comprador
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

from pydantic import BaseModel, EmailStr

class CompradorCreate(BaseModel):
    nome: str
    numero_celular: str
    email: EmailStr
    rifa_id: int

@router.post('/', status_code=200, dependencies=[Depends(get_current_user)])
async def create_comprador(
    comprador: CompradorCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CompradorCreate:
    try:
        db_comprador = Comprador(
            **comprador.model_dump(),
        )
        
        db.add(db_comprador)
        db.commit()
        
        return comprador
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
