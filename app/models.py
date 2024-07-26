from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    Date,
    Float,
    DateTime,
    Text,
    ForeignKey,
    func,
    select,
)
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
from app.enums import RifaStatus

Base = declarative_base()


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
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    token = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())


class Comprador(Base):
    __tablename__ = 'compradores'

    comprador_id = Column(Integer, primary_key=True)

    nome = Column(String(80), nullable=False)
    numero_celular = Column(String(11), nullable=False)
    email = Column(String(255), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Bilhete(Base):
    __tablename__ = 'bilhetes'

    bilhete_id = Column(Integer, primary_key=True)
    rifa_id = Column(Integer, ForeignKey('rifas.rifa_id'), nullable=False)
    comprador_id = Column(
        Integer, ForeignKey('compradores.comprador_id'), nullable=False
    )

    numero = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)

    rifa = relationship("Rifa")
    comprador = relationship("Comprador")

    created_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )


class Rifa(Base):
    __tablename__ = 'rifas'

    rifa_id = Column(Integer, primary_key=True)
    criador_id = Column(String(30), ForeignKey('users.id'), nullable=False)
    nome = Column(String(30), nullable=False)
    descricao = Column(Text)
    status = Column(Integer, nullable=False, default=RifaStatus.DISPONIVEL.value)
    preco_bilhete = Column(Float, nullable=False)
    premio_nome = Column(String(50), nullable=False)
    premio_imagem = Column(String, nullable=False)
    data_sorteio = Column(Date, nullable=False)
    quant_bilhetes = Column(Integer, nullable=False)

    criador = relationship("User")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    @hybrid_property
    def quant_restantes(self):
        return self.quant_bilhetes - self.quant_comprados

    quant_comprados = column_property(
        select(func.count(Bilhete.comprador_id))
        .where(Bilhete.rifa_id == rifa_id)
        .correlate_except(Bilhete)
        .scalar_subquery()
    )


class Pagamento(Base):
    __tablename__ = 'pagamentos'

    pagamento_id = Column(Integer, primary_key=True)
    comprador_id = Column(
        Integer, ForeignKey('compradores.comprador_id'), unique=True, nullable=False
    )
    valor = Column(Float, nullable=False)

    # NOTE Adicionar outras colunas necessárias após descobrir como adicionar pagamento

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
