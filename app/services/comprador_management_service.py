from sqlalchemy.orm import Session
from app.schemas import CompradorCreate
from app.models import Comprador


def find_comprador(db: Session, comprador: CompradorCreate):
    return (
        db.query(Comprador)
        .filter(
            Comprador.nome == comprador.nome,
            Comprador.numero_celular == comprador.numero_celular,
            Comprador.email == comprador.email,
        )
        .first()
    )
