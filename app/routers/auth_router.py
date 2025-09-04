from fastapi import APIRouter, HTTPException

from app.schemas.user_schema import UserRegSchema


router = APIRouter(prefix="/auth")


# endpoints:

@router.get(
    "",
    tags=["Аутентефикация"],
    summary="",
)
async def get_user():
    pass

@router.post(
    "",
    tags=["Аутентефикация"],
    summary="Добавить нового пользователя в бд",
)
async def add_user(user_data: UserRegSchema):
    pass