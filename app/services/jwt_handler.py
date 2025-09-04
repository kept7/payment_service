from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi.responses import JSONResponse

import jwt

from app.utils.config import settings


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(subj: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: Dict[str, Any] = {
        "sub": subj,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def set_cookies(access_token: str) -> JSONResponse:
    max_age = ACCESS_TOKEN_EXPIRE_MINUTES * 60

    resp = JSONResponse(
        content={
            "ok": True,
            "token_type": "bearer",
            "expires_in": max_age,
        }
    )

    resp.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    return resp
