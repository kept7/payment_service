import logging

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

import jwt

from app.utils.config import settings


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(subj: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: Dict[str, Any] = {
        "sub": subj,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


logger = logging.getLogger(__name__)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    logger.info("now_utc: %s", datetime.now().isoformat())
    logger.debug("token: %s...", token[:40])

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


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


def get_token_from_cookie(
    request: Request, cookie_name: str = "access_token"
) -> Optional[str]:
    return request.cookies.get(cookie_name)
