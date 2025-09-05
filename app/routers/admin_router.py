from fastapi import APIRouter, HTTPException, Depends

from app.core.db.db_sessions import db_payment_user
from app.services.authorization_handler import get_current_user
from app.utils.config import settings


router = APIRouter(prefix="/admin")


@router.get(
    "/admin/user_payment/all",
    tags=["Пользователь-платеж"],
    summary="Получить все записи пользователь-платёж (для суперпользователя)",
)
async def get_all_payment_user_data(current_user=Depends(get_current_user)):
    if current_user.user_email != settings.SU:
        raise HTTPException(status_code=401, detail="Permission denied")

    res = await db_payment_user.get_all()

    if res is None:
        raise HTTPException(status_code=404, detail="Payments doesn't exist")

    return res
