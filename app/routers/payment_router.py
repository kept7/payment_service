import logging
import uuid as _uuid

from fastapi import APIRouter, HTTPException, Depends

from app.core.db.db_sessions import db_payment, db_payment_user
from app.schemas.payment_schema import PaymentSchema
from app.models.init_model import PaymentStatus, dec
from app.services.authorization_handler import get_current_user
from app.utils.config import settings


logger = logging.getLogger("app.payment")
router = APIRouter(prefix="/payment")


@router.post(
    "/",
    tags=["Платежи"],
    summary="Создать платёж",
)
async def create_payment(
    payment_data: PaymentSchema, current_user=Depends(get_current_user)
):
    logger.info("Create payment requested by %s", current_user.user_email)
    try:
        res = await db_payment.create(payment_data)
        if not res:
            logger.error(
                "Failed to create payment in db for user %s", current_user.user_email
            )
            raise HTTPException(status_code=400, detail="Failed to create payment")

        rel_created = await db_payment_user.create(
            current_user.user_email, res.payment_id
        )
        if rel_created:
            logger.info(
                "Payment created %s for user %s",
                res.payment_id,
                current_user.user_email,
            )
            return {"ok": True, "msg": "Payment was created"}

        await db_payment.delete(res.payment_id)
        logger.error(
            "Failed to create payment-user relation for payment %s user %s; payment deleted",
            res.payment_id,
            current_user.user_email,
        )
        raise HTTPException(
            status_code=400, detail="Failed to create payment-user relation"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Unexpected error when creating payment for %s: %s",
            current_user.user_email,
            e,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/all",
    tags=["Платежи"],
    summary="Получить все платежи (для суперпользователя)",
)
async def get_payments(current_user=Depends(get_current_user)):
    logger.debug(
        "Get all payments requested by %s",
        getattr(current_user, "user_email", "anonymous"),
    )
    if current_user.user_email != settings.SU:
        logger.warning(
            "Permission denied for %s when requesting all payments",
            current_user.user_email,
        )
        raise HTTPException(status_code=401, detail="Permission denied")

    res = await db_payment.get_all()
    if res is None:
        logger.info("No payments found (db returned None)")
        raise HTTPException(status_code=404, detail="Payments doesn't exist")

    logger.info(
        "Returning %d payments to superuser %s",
        len(res) if isinstance(res, list) else 0,
        current_user.user_email,
    )
    return res


@router.get(
    "/{payment_id}",
    tags=["Платежи"],
    summary="Получить информацию о конкретном платеже",
)
async def get_payment(payment_id: _uuid.UUID, current_user=Depends(get_current_user)):
    logger.debug(
        "Get payment %s requested by %s",
        payment_id,
        getattr(current_user, "user_email", "anonymous"),
    )
    res = await db_payment.get(payment_id)
    if res is None:
        logger.warning("Payment %s not found", payment_id)
        raise HTTPException(status_code=404, detail="Payment doesn't exist")

    logger.info("Returning payment %s to %s", payment_id, current_user.user_email)
    return res


@router.get(
    "/user_email/all",
    tags=["Платежи"],
    summary="Получить все платежи пользователя",
)
async def get_user_payments(current_user=Depends(get_current_user)):
    logger.debug("Get payments for user %s", current_user.user_email)
    res = await db_payment_user.get_by_user(current_user.user_email)
    if res is None or len(res) == 0:
        logger.info("User %s has no payments", current_user.user_email)
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []
    for el in res:
        record = await db_payment.get(el.payment_id)
        if record:
            result.append(record)

    logger.info(
        "Returning %d payments for user %s", len(result), current_user.user_email
    )
    return result


@router.get(
    "/user_email/status/{status}",
    tags=["Платежи"],
    summary="Получить все платежи пользователя с определённым статусом",
)
async def get_user_payments_by_status(
    status: PaymentStatus, current_user=Depends(get_current_user)
):
    logger.debug(
        "Get payments by status=%s for user %s", status, current_user.user_email
    )
    res = await db_payment_user.get_by_user(current_user.user_email)
    if res is None or len(res) == 0:
        logger.info("User %s has no payments", current_user.user_email)
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []
    for el in res:
        record = await db_payment.get_by_status(el.payment_id, status)
        if record:
            result.append(record)

    logger.info(
        "Returning %d payments with status %s for user %s",
        len(result),
        status,
        current_user.user_email,
    )
    return result


@router.get(
    "/user_email/amount/{amount}",
    tags=["Платежи"],
    summary="Получить все платежи пользователя с определённой суммой платежа",
)
async def get_user_payments_by_amount(
    amount: dec, current_user=Depends(get_current_user)
):
    logger.debug(
        "Get payments by amount=%s for user %s", amount, current_user.user_email
    )
    res = await db_payment_user.get_by_user(current_user.user_email)
    if res is None or len(res) == 0:
        logger.info("User %s has no payments", current_user.user_email)
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []
    for el in res:
        record = await db_payment.get_by_amount(el.payment_id, amount)
        if record:
            result.append(record)

    logger.info(
        "Returning %d payments with amount %s for user %s",
        len(result),
        amount,
        current_user.user_email,
    )
    return result


@router.put(
    "/{payment_id}",
    tags=["Платежи"],
    summary="Обновить статус платежа",
)
async def update_payment_status(
    payment_id: _uuid.UUID,
    status: PaymentStatus,
    current_user=Depends(get_current_user),
):
    logger.info(
        "Update payment %s status to %s requested by %s",
        payment_id,
        status,
        current_user.user_email,
    )
    res = await db_payment.get(payment_id)
    if res is None:
        logger.warning("Payment %s not found when updating status", payment_id)
        raise HTTPException(status_code=404, detail="Payment doesn't exist")

    if res.status == "Оплачен" or res.status == "Отменен":
        logger.warning(
            "Attempt to change already final payment %s status=%s",
            payment_id,
            res.status,
        )
        raise HTTPException(status_code=400, detail="Payment complete")

    try:
        await db_payment.update(payment_id, status)
        logger.info(
            "Payment %s status changed to %s by %s",
            payment_id,
            status,
            current_user.user_email,
        )
        return {"ok": True, "msg": "Payment status was changed"}
    except Exception as e:
        logger.exception(
            "Failed to change payment %s status to %s: %s", payment_id, status, e
        )
        raise HTTPException(
            status_code=404, detail=f"Failed to change payment status: {e}"
        )
