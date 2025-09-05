import uuid as _uuid

from fastapi import APIRouter, HTTPException, Depends

from app.core.db.db_sessions import db_payment, db_payment_user
from app.schemas.payment_schema import PaymentSchema
from app.models.init_model import PaymentStatus, dec
from app.services.authorization_handler import get_current_user
from app.utils.config import settings

router = APIRouter(prefix="/payment")


@router.post(
    "/",
    tags=["Платежи"],
    summary="Создать платёж",
)
async def create_payment(
    payment_data: PaymentSchema, current_user=Depends(get_current_user)
):
    res = await db_payment.create(payment_data)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to create payment")

    if await db_payment_user.create(current_user.user_email, res.payment_id):
        return {"ok": True, "msg": "Payment was created"}

    await db_payment.delete(res.payment_id)
    raise HTTPException(
        status_code=400, detail="Failed to create payment-user relation"
    )


@router.get(
    "/all",
    tags=["Платежи"],
    summary="Получить все платежи (для суперпользователя)",
)
async def get_payments(current_user=Depends(get_current_user)):
    if current_user.user_email != settings.SU:
        raise HTTPException(status_code=401, detail="Permission denied")

    res = await db_payment.get_all()
    if res is None:
        raise HTTPException(status_code=404, detail="Payments doesn't exist")

    return res


@router.get(
    "/id/{payment_id}",
    tags=["Платежи"],
    summary="Получить информацию о конкретном платеже",
)
async def get_payment(payment_id: _uuid.UUID, current_user=Depends(get_current_user)):
    res = await db_payment.get(payment_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Payment doesn't exist")

    return res


@router.get(
    "/email/{user_email}/all",
    tags=["Платежи"],
    summary="Получить все платежи пользователя",
)
async def get_user_payments(current_user=Depends(get_current_user)):
    res = await db_payment_user.get_by_user(current_user.user_email)
    if res is None:
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []

    for el in res:
        record = await db_payment.get(el.payment_id)
        if record:
            result.append(record)

    return result


@router.get(
    "/email/{user_email}/{status}",
    tags=["Платежи"],
    summary="Получить все платежи пользователя с определённым статусом",
)
async def get_user_payments_by_status(
    status: PaymentStatus, current_user=Depends(get_current_user)
):
    res = await db_payment_user.get_by_user(current_user.user_email)
    if len(res) == 0:
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []

    for el in res:
        record = await db_payment.get_by_status(el.payment_id, status)
        if record:
            result.append(record)

    return result


@router.get(
    "/email/{amount}",
    tags=["Платежи"],
    summary="Получить все платежи пользователя с определённой суммой платежа",
)
async def get_user_payments_by_amount(
    amount: dec, current_user=Depends(get_current_user)
):
    res = await db_payment_user.get_by_user(current_user.user_email)
    if len(res) == 0:
        raise HTTPException(status_code=404, detail="This user has no payments")

    result = []

    for el in res:
        record = await db_payment.get_by_amount(el.payment_id, amount)
        if record:
            result.append(record)

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
    res = await db_payment.get(payment_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Payment doesn't exist")

    if res.status == "Оплачен" or res.status == "Отменен":
        raise HTTPException(status_code=400, detail="Payment complete")

    try:
        await db_payment.update(payment_id, status)
        return {"ok": True, "msg": "Payment status was changed"}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Failed to change payment status: {e}"
        )
