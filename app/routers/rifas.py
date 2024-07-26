import logging
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session
from app.config import get_env_var
from app.models import Rifa, User, Comprador, Bilhete
from app.database import get_db
from app.schemas import (
    RifaCreate,
    RifaInfo,
    BilheteCreate,
    CompradorCreate,
    BilheteComprador,
)
from app.dependencies import get_current_user
import app.services.rifa_management_service as rifa_service
import app.services.comprador_management_service as comprador_service
from pydantic import ValidationError

UPLOAD_DIRECTORY = Path("files")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
MIN_BILHETES_COUNT = get_env_var('MIN_BILHETES_COUNT')
MAX_BILHETES_COUNT = get_env_var('MAX_BILHETES_COUNT')

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/', status_code=201)
async def create_rifa(
    nome: Annotated[str, Form(max_length=30)],
    descricao: Annotated[str | None, Form()],
    premio_nome: Annotated[str, Form(max_length=50)],
    preco_bilhete: Annotated[float, Form(gt=0, le=100)],
    premio_imagem: UploadFile,
    data_sorteio: Annotated[date, Form()],
    quant_bilhetes: Annotated[
        int,
        Form(
            ge=MIN_BILHETES_COUNT,
            le=MAX_BILHETES_COUNT,
            description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes',
        ),
    ],
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RifaInfo:
    file_id = str(uuid.uuid4())
    file_extension = Path(premio_imagem.filename).suffix
    file_name = f"{file_id}{file_extension}"
    file_path = UPLOAD_DIRECTORY / file_name
    file_url = request.url_for(UPLOAD_DIRECTORY.name, path=file_path.name)

    try:
        rifa_pydantic = RifaCreate(
            nome=nome,
            descricao=descricao,
            preco_bilhete=preco_bilhete,
            premio_nome=premio_nome,
            premio_imagem=str(file_path),
            data_sorteio=data_sorteio,
            quant_bilhetes=quant_bilhetes,
        )
        db_rifa = Rifa(
            **rifa_pydantic.model_dump(exclude='premio_imagem'),
            premio_imagem=str(file_url),
            criador_id=user.id,
        )

        db.add(db_rifa)
        db.commit()

        with file_path.open("wb") as f:
            f.write(await premio_imagem.read())

        return db_rifa
    except ValidationError as e:
        rifa_service.clean_failed_rifa_creation(db, file_path)

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": e.errors()}),
        )
    except Exception as e:
        rifa_service.clean_failed_rifa_creation(db, file_path)

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def read_rifas(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 3,
) -> list[RifaInfo]:
    db_rifas = (
        db.query(Rifa)
        .filter(Rifa.criador_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not db_rifas:
        raise HTTPException(status_code=404, detail="Nenhuma rifa encontrada")

    return db_rifas


@router.get('/{rifa_id}', dependencies=[Depends(get_current_user)])
async def get_rifa(rifa_id: int, db: Session = Depends(get_db)) -> RifaInfo:
    db_rifa = db.query(Rifa).filter(Rifa.rifa_id == rifa_id).first()

    if not db_rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")

    return db_rifa


# @router.put("/{rifa_id}")
# def update_rifa(
#     rifa_update: RifaUpdate,
#     db: Annotated[Session, Depends(get_db)],
#     rifa: Annotated[Rifa, Depends(get_rifa)]
# ):
#     for key, value in rifa_update.dict().items():
#         setattr(rifa, key, value)
#     db.commit()
#     db.refresh(rifa)
#     return rifa


@router.delete("/{rifa_id}")
def delete_rifa(
    rifa: Annotated[Rifa, Depends(get_rifa)], db: Session = Depends(get_db)
):
    db.delete(rifa)
    db.commit()
    return rifa


@router.post('/buy_bilhetes', status_code=200)
async def buy_bilhetes(
    comprador: CompradorCreate,
    bilhetes: list[BilheteCreate],
    db: Annotated[Session, Depends(get_db)],
) -> BilheteComprador:
    db_comprador = comprador_service.find_comprador(db, comprador)

    try:
        if not db_comprador:
            db_comprador = Comprador(**comprador.model_dump())
            db.add(db_comprador)
            db.commit()
            db.refresh(db_comprador)

        db_bilhetes = [
            Bilhete(**bilhete.model_dump(), comprador_id=db_comprador.comprador_id)
            for bilhete in bilhetes
        ]

        db.add_all(db_bilhetes)
        db.commit()

        return {'bilhetes': db_bilhetes, 'comprador': db_comprador}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
