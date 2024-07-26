from fastapi import APIRouter, Depends
from typing import Annotated
from app.models import User
from app.schemas import BaseUser
from app.dependencies import get_current_user

router = APIRouter()


@router.get('/me')
async def get_user(user: Annotated[User, Depends(get_current_user)]) -> BaseUser:
    return BaseUser(
        name=user.username,
        given_name=user.first_name,
        family_name=user.last_name,
        picture=user.picture,
        email=user.email,
    )
