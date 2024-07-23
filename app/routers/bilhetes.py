from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from app.schemas import BilheteDB
from app.models import Bilhete
from app.dependencies import get_current_user
from app.database import get_db

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)])
def read_bilhetes(
    rifa_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[BilheteDB]:
    db_bilhetes = db.query(Bilhete).filter(Bilhete.rifa_id == rifa_id).all()

    if not db_bilhetes:
        raise HTTPException(
            status_code=404, detail=f"Nenhum bilhete vendido para a rifa {rifa_id}"
        )

    return db_bilhetes
