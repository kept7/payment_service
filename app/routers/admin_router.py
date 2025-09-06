import logging

from fastapi import APIRouter, HTTPException, Depends

from app.core.db.db_sessions import db_payment_user
from app.services.authorization_handler import get_current_user
from app.utils.config import settings


logger = logging.getLogger("app.admin")
router = APIRouter(prefix="/admin")


@router.get(
    "/user_payment/all",
    tags=["Пользователь-платеж"],
    summary="Получить все записи пользователь-платёж (для суперпользователя)",
)
async def get_all_payment_user_data(current_user=Depends(get_current_user)):
    logger.debug(
        "Request to get all user-payment records by %s",
        getattr(current_user, "user_email", "anonymous"),
    )

    if current_user.user_email != settings.SU:
        logger.warning(
            "Permission denied for %s when requesting all user-payment records",
            current_user.user_email,
        )
        raise HTTPException(status_code=401, detail="Permission denied")

    try:
        res = await db_payment_user.get_all()
    except Exception as e:
        logger.exception(
            "Database error while fetching all user-payment records requested by %s: %s",
            current_user.user_email,
            e,
        )
        raise HTTPException(status_code=500, detail="Internal server error")

    if res is None or len(res) == 0:
        logger.info(
            "No user-payment records found (db returned None/empty) for requester %s",
            current_user.user_email,
        )
        raise HTTPException(status_code=404, detail="Payments doesn't exist")

    logger.info(
        "Returning %d user-payment records to superuser %s",
        len(res) if isinstance(res, list) else 0,
        current_user.user_email,
    )
    return res
