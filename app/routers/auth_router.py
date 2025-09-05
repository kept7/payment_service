import logging

from fastapi import APIRouter, HTTPException, Depends, Body

from app.schemas.auth_schema import UserSchema, AuthSchema
from app.core.db.db_sessions import db_auth
from app.services.hash_handler import get_hash, is_hash_eq
from app.services.jwt_handler import create_access_token, set_cookies
from app.services.authorization_handler import get_current_user
from app.utils.config import settings


logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/auth")


@router.post(
    "/registration",
    tags=["Аутентефикация"],
    summary="Добавить нового пользователя",
)
async def add_user(user_data: UserSchema):
    logger.info("Registration attempt for %s", user_data.user_email)
    res = await db_auth.get(user_data.user_email)
    if res is not None:
        logger.warning(
            "Registration failed: user already exists %s", user_data.user_email
        )
        raise HTTPException(status_code=409, detail="User already exist")

    try:
        user_data.user_password = get_hash(user_data.user_password)
        created = await db_auth.create(user_data)
        if created:
            logger.info("User created: %s", user_data.user_email)
            return {"ok": True, "msg": "User was created"}
        logger.error(
            "Failed to create user (db returned falsy) %s", user_data.user_email
        )
        raise HTTPException(status_code=400, detail="Failed to create user")
    except Exception as e:
        logger.exception(
            "Exception during registration for %s: %s", user_data.user_email, e
        )
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


@router.get(
    "/all",
    tags=["Аутентефикация"],
    summary="Получить данные всех пользователей (для суперпользователя)",
)
async def get_users(current_user=Depends(get_current_user)):
    if current_user.user_email != settings.SU:
        raise HTTPException(status_code=401, detail="Permission denied")

    res = await db_auth.get_all()
    if res is None:
        raise HTTPException(status_code=404, detail="Users doesn't exitst")

    return res


@router.put(
    "/{user_email}",
    tags=["Аутентефикация"],
    summary="Изменить пароль пользователя",
)
async def update_password(
    new_user_password: str = Body(..., min_length=4),
    current_user=Depends(get_current_user),
):
    try:
        new_user_password_hash = get_hash(new_user_password)
        await db_auth.update(current_user.user_email, new_user_password_hash)
        return {"ok": True, "msg": "Password was changed"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to change password: {e}")
