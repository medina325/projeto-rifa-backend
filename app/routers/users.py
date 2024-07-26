from fastapi import APIRouter, Depends
from typing import Annotated
from app.models import User
from app.schemas import BaseUser
from app.dependencies import get_current_user

router = APIRouter()


@router.get('/me')
async def get_user(user: Annotated[User, Depends(get_current_user)]):
    return user
