import logging
import httpx
from fastapi import Request, APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import ValidationError
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.database import get_db
from app.dependencies import oauth2_google_scheme
from app.schemas import GoogleTokenResponse, GoogleUserInfoResponse, UserDB
from app.services import user_management_service
from app.security import (
    unauthorized_redirect,
    user_exists,
    create_access_token,
    get_authorized_redirect,
    is_token_valid
)

router = APIRouter()
logger = logging.getLogger(__name__)

async def fetch_token(code: str, request: Request) -> GoogleTokenResponse | None:
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': GOOGLE_CLIENT_ID,
                    'client_secret': GOOGLE_CLIENT_SECRET,
                    'redirect_uri': f'{request.base_url}oauth/callback',
                    'grant_type': 'authorization_code',
                }
            )
            token_response.raise_for_status()
            return GoogleTokenResponse(**token_response.json())
        except (httpx.HTTPStatusError, ValidationError) as e:
            logger.error(f"Token request failed: {e}")

async def fetch_user_info(
    token_response: GoogleTokenResponse | None = Depends(fetch_token)
) -> GoogleUserInfoResponse | None:
    """
    """

    if not token_response:
        return
    
    access_token = token_response.access_token
    async with httpx.AsyncClient() as client:
        try:
            user_info_response = await client.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_info_response.raise_for_status()

            return GoogleUserInfoResponse(
                **user_info_response.json(),
                token_response=token_response
            )
        except (httpx.HTTPStatusError, ValidationError) as e:
            logger.error(f"Fetch user credentials failed: {e}")

@router.get('/callback')
async def get_token_callback(
    db: Annotated[Session, Depends(get_db)],
    user_response: GoogleUserInfoResponse | None = Depends(fetch_user_info)
):
    if not user_response:
        return unauthorized_redirect
    
    user_db = UserDB(id=user_response.sub, username=user_response.name, **user_response.model_dump())
    
    if not user_exists(db, user_db.id):
        user_management_service.insert_user_into_db(user_db, db)
    
    jwt_token = create_access_token(
        user_db.id,
        # timedelta(seconds=user_response.token_response.expires_in)
        timedelta(hours=10) # NOTE Para poder testar as telas em paz - remover depois
    )
    
    return get_authorized_redirect(jwt_token)

@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_google_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    if not is_token_valid(token, db):
        return {'Token já foi invalidado'}

    user_management_service.logout_user_jwt(token, db)
    return {'Usuário deslogado, JWT invalidado'}
