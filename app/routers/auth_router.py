from fastapi import APIRouter, HTTPException

from app.schemas.auth_schema import UserSchema, AuthSchema
from app.core.db_sessions import db_auth

from app.services.hash_handler import get_hash, is_hash_eq
from app.services.jwt_handler import create_access_token, set_cookies


router = APIRouter(prefix="/auth")


@router.get(
    "/",
    tags=["Аутентефикация"],
    summary="Получить данные всех пользователей",
)
async def get_users():
    # здесь будет проверка jwt-токена на пользователя admin@admin.com
    res = await db_auth.get_all()
    if res is None:
        raise HTTPException(status_code=404, detail="Users doesn't exitst")
    else:
        return res


@router.post(
    "/registration",
    tags=["Аутентефикация"],
    summary="Добавить нового пользователя",
)
async def add_user(user_data: UserSchema):
    res = await db_auth.get(user_data.user_email)
    if res is not None:
        raise HTTPException(status_code=409, detail="User already exist")

    user_data.user_password = get_hash(user_data.user_password)
    if await db_auth.create(user_data):
        return {"ok": True, "msg": "User was created"}
    raise HTTPException(status_code=400, detail="Failed to create user")


@router.post(
    "/authentication",
    tags=["Аутентефикация"],
    summary="Аутентефикация пользователя в системе и выдача jwt-токена",
)
async def authentication(auth_data: AuthSchema):
    res = await db_auth.get(auth_data.user_email)
    if res is None:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    if is_hash_eq(auth_data.user_password, res.user_password_hash):
        access_token = create_access_token(subj=auth_data.user_email)
        return set_cookies(access_token)
    raise HTTPException(status_code=401, detail="Incorrect credentials")
