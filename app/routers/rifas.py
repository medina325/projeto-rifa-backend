import logging
from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from app.config import get_env_var
from app.models import Rifa, User
from app.database import get_db
from app.schemas import RifaCreate, RifaInfo
from app.dependencies import get_rifa, get_current_user, get_user_rifas
# NOTE rifas/v2 imports
from fastapi import Form, UploadFile, Request, HTTPException
from datetime import date
from pathlib import Path
import uuid
import os

UPLOAD_DIRECTORY = Path("files")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
MIN_BILHETES_COUNT = get_env_var('MIN_BILHETES_COUNT')
MAX_BILHETES_COUNT = get_env_var('MAX_BILHETES_COUNT')

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", status_code=201)
def create_rifa(
    rifa: RifaCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RifaInfo:
    
    db_rifa = Rifa(**rifa.model_dump(exclude='premio_imagem'))
    db_rifa.criador = user
    db.add(db_rifa)
    db.commit()
    db.refresh(db_rifa)

    return db_rifa

# TODO -- ainda não finalizado
@router.post('/upload_prize_image', status_code=201, dependencies=[Depends(get_current_user)])
async def upload_prize_images(
    rifa_id: Annotated[int, Form()],
    file_name: Annotated[str, Form()],
    premio_imagem: UploadFile,
    db: Annotated[Session, Depends(get_db)],
):
    rifa = db.query(Rifa).filter(Rifa.rifa_id == rifa_id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail='Não há rifa a ser relacionada com o arquivo')
    file_path = UPLOAD_DIRECTORY / file_name
    with file_path.open("wb") as f:
        f.write(await premio_imagem.read())
    return {
        'filename': file_path
    }

@router.post('/v2', status_code=201)
async def create_rifa(
    nome: Annotated[str, Form(max_length=30)],
    descricao: Annotated[str | None, Form()],
    premio_nome: Annotated[str, Form(max_length=50)],
    preco_bilhete: Annotated[float, Form(gt=0, le=100)],
    premio_imagem: UploadFile,
    data_sorteio: Annotated[date, Form()],
    quant_bilhetes: Annotated[int, Form(
        ge=MIN_BILHETES_COUNT,
        le=MAX_BILHETES_COUNT,
        description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes'
    )],
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
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
            premio_imagem=str(file_url),
            data_sorteio=data_sorteio,
            quant_bilhetes=quant_bilhetes,
        )
        db_rifa = Rifa(
            **rifa_pydantic.model_dump(),
            criador_id=user.id
        )
        
        db.add(db_rifa)
        db.commit()
        
        with file_path.open("wb") as f:
            f.write(await premio_imagem.read())
        
        return {
            'filename': premio_imagem.filename,
            **rifa_pydantic
        }
    except Exception as e:
        db.rollback()
        if file_path.is_file():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def read_rifas(
    # db: Annotated[Session, Depends(get_db)],
    rifas: Annotated[list[Rifa], Depends(get_user_rifas)],
) -> list[RifaInfo]:
    
    # Adicionar qnt de bilhetes
    return rifas

@router.get('/{rifa_id}', dependencies=[Depends(get_current_user)])
async def read_rifa(rifa: Annotated[Rifa, Depends(get_rifa)]):
    return rifa

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
    rifa: Annotated[Rifa, Depends(get_rifa)],
    db: Session = Depends(get_db)
):
    db.delete(rifa)
    db.commit()
    return rifa
