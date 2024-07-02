from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from app.models import Rifa, User, Bilhete
from app.database import get_db
from app.schemas import RifaCreate, RifaBase, RifaInfo
from app.dependencies import get_rifa, get_current_user, get_user_rifas

router = APIRouter()

@router.post("/", status_code=201)
def create_rifa(
    rifa: RifaCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RifaBase:
    # TODO Adicionar validação de rifa repetida
    # campos criado_id, nome -> validar apenas rifas com status Disponível
    # adicionar try catch
    
    db_rifa = Rifa(**rifa.model_dump(exclude='quant_bilhetes'))
    db_rifa.criador = user
    db.add(db_rifa)
    db.commit()
    db.refresh(db_rifa)
    
    # NOTE pensar se isso é necessário mesmo
    for _ in range(rifa.quant_bilhetes):
        db_bilhete = Bilhete(rifa_id=db_rifa.rifa_id)
        db.add(db_bilhete)
    db.commit()

    return db_rifa

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
