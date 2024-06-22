from fastapi import APIRouter, Depends
from app.models import User
from typing import Annotated
from app.dependencies import get_current_user

router = APIRouter()

@router.get('/me')
async def get_user(
    user: Annotated[User, Depends(get_current_user)]
# ) -> User:
):
    return user
