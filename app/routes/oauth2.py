import requests
from fastapi import Request, APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get('/callback')
async def get_token_callback(request: Request, code: str):
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
    
    token_response_data = token_response.json()
    access_token = token_response_data['access_token']
    id_token = token_response_data['id_token']
    print(token_response_data, '\n\n\n\n')

    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info = user_info_response.json()
    
    # user = User(id=user_info['sub'], email=user_info['email'], name=user_info['name'])
    
    session_token = "generate_your_token_here"
    
    return {"token": session_token, "user": user_info}
