import requests
import app.security as security_utils
from fastapi import Request, APIRouter, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.database import get_db
from app.models import RevokedToken, User

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={'openid': '', 'email': '', 'profile': ''},
)

@router.get('/callback')
async def get_token_callback(
    request: Request,
    code: str,
    db: Annotated[Session, Depends(get_db)]
):
    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': f'{request.base_url}oauth/callback',
            'grant_type': 'authorization_code',
        }
    )
    
    if not token_response.ok:
        return security_utils.unauthorized_redirect
    
    token_response_data = token_response.json()
    access_token = token_response_data['access_token']

    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if not user_info_response.ok:
        return security_utils.unauthorized_redirect
        
    user_info = user_info_response.json()

    if not security_utils.user_exists(db, user_info['sub']):
        # NOTE SERVICE -------------------
        print('Criando usuário\n\n\n')
        user = User(
            id=user_info['sub'],
            username=user_info['name'],
            email=user_info['email'],
            first_name=user_info['given_name'],
            last_name=user_info['family_name'],
            picture=user_info['picture'],
            auth_provider='google'
        )
        db.add(user)
        db.commit()
        # ------------------------------
    
    # NOTE como garantir que expires_in existe????????
    # Usar pydantic model para validar DTO né
    # caso validação falhe, como lidar? Subi exceção específica?
    jwt_token = security_utils.create_access_token(
        user_info['sub'],
        timedelta(seconds=token_response_data['expires_in'])
    )
    
    return security_utils.get_authorized_redirect(jwt_token)

@router.get("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    # NOTE service ---------------------------
    revoked_token = RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()
    # ----------------------------------------
    response = RedirectResponse(url="http://localhost:5173")
    response.delete_cookie(key="Authorization")
    return response


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if security_utils.is_token_valid(token, db):
        return security_utils.get_user_from_token(db, token)
    raise security_utils.credentials_exception

@router.get('/users/me')
async def get_user(
    user: Annotated[User, Depends(get_current_user)]
# ) -> User:
):
    return user
