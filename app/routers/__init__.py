from fastapi import FastAPI, APIRouter

from app.routers.auth_router import router as auth_router
from app.routers.payment_router import router as payment_router
from app.routers.admin_router import router as admin_router


main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(payment_router)
main_router.include_router(admin_router)
