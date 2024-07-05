from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator
from typing import Literal
from datetime import date, timedelta
from app.config import get_env_var
from app.enums import RifaStatus

class TokenData(BaseModel):
    sub: str
    exp: float

class GoogleTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: Literal['Bearer']
    scope: str | None = None

class BaseUser(BaseModel):
    name: str
    given_name: str
    family_name: str
    picture: HttpUrl
    email: EmailStr

    class ConfigDict:
        from_attributes = True

class UserDB(BaseUser):
    id: str

class GoogleUserInfoResponse(BaseUser):
    sub: str
    email_verified: bool
    auth_provider: Literal['google'] = 'google'
    token_response: GoogleTokenResponse

MIN_BILHETES_COUNT = get_env_var('MIN_BILHETES_COUNT')

class RifaInDB(BaseModel):
    rifa_id: int
    nome: str
    descricao: str | None
    status: RifaStatus
    preco_bilhete: float = Field(gt=0, le=100)
    premio_nome: str
    premio_imagem: str
    data_sorteio: date
    quant_bilhetes: int

    @field_validator('data_sorteio')
    def check_date_is_not_in_the_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('A data não pode estar no passado')
        return v

    @field_validator('data_sorteio')
    def check_date_is_not_more_than_a_month_ahead(cls, v: date) -> date:
        threshold_date = date.today() + timedelta(weeks=4)
        if v > threshold_date:
            raise ValueError('A data não pode estar mais de uma mês no futuro')
        return v

class RifaInfo(BaseModel):
    rifa_id: int
    nome: str
    descricao: str | None
    status: RifaStatus
    preco_bilhete: float = Field(gt=0, le=100)
    premio_nome: str
    premio_imagem: str
    data_sorteio: date
    quant_bilhetes: int = Field(
        ge=MIN_BILHETES_COUNT,
        description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes'
    )
    quant_comprados: int
    quant_restantes: int
    
    @field_validator('data_sorteio')
    def check_date_is_not_in_the_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('A data não pode estar no passado')
        return v

    @field_validator('data_sorteio')
    def check_date_is_not_more_than_a_month_ahead(cls, v: date) -> date:
        threshold_date = date.today() + timedelta(weeks=4)
        if v > threshold_date:
            raise ValueError('A data não pode estar mais de uma mês no futuro')
        return v

class RifaCreate(BaseModel):
    nome: str
    descricao: str | None
    preco_bilhete: float = Field(gt=0, le=100)
    premio_nome: str
    premio_imagem: str
    data_sorteio: date
    quant_bilhetes: int = Field(
        ge=MIN_BILHETES_COUNT,
        description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes'
    )
    
    @field_validator('data_sorteio')
    def check_date_is_not_in_the_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('A data não pode estar no passado')
        return v

    @field_validator('data_sorteio')
    def check_date_is_not_more_than_a_month_ahead(cls, v: date) -> date:
        threshold_date = date.today() + timedelta(weeks=4)
        if v > threshold_date:
            raise ValueError('A data não pode estar mais de uma mês no futuro')
        return v

class RifaUpdate():
    pass
