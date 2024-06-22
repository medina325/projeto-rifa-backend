from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Literal

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

class UserDB(BaseUser):
    id: str

class GoogleUserInfoResponse(BaseUser):
    sub: str
    email_verified: bool
    auth_provider: Literal['google'] = 'google'
    token_response: GoogleTokenResponse
