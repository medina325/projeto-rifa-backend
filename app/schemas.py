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

class RifaBase(BaseModel):
    nome: str
    descricao: str | None = None
    status: Literal[1,2,3] = RifaStatus.DISPONIVEL.value
    preco_bilhete: float = Field(gt=0, le=100)
    premio_nome: str
    premio_imagem: str
    data_sorteio: date

    @field_validator('data_sorteio')
    def check_date_is_not_in_the_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('A data não pode estar no passado')
        return v

    @field_validator('data_sorteio')
    def check_date_is_not_more_than_a_month_ahead(cls, v: date) -> date:
        threshold_date = date.today() + timedelta(weeks=4)
        if v > threshold_date:
            raise ValueError('A data não pode estar mais de um mês no futuro')
        return v


class RifaInDB(RifaBase):
    rifa_id: int
    quant_bilhetes: int

class RifaInfo(RifaBase):
    rifa_id: int
    status: str
    quant_bilhetes: int = Field(
        ge=MIN_BILHETES_COUNT,
        description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes'
    )
    quant_comprados: int
    quant_restantes: int
    
    @field_validator('status', mode='before')
    def convert_status(cls, value):
        return RifaStatus(value).description()

class RifaCreate(RifaBase):
    quant_bilhetes: int = Field(
        ge=MIN_BILHETES_COUNT,
        description=f'A rifa deve ter no mínimo {MIN_BILHETES_COUNT} bilhetes'
    )
