from typing import Dict, Any

from fastapi import HTTPException, Request

from app.core.db_sessions import db_auth
from app.services.jwt_handler import get_token_from_cookie, verify_jwt_token


async def get_current_user(request: Request) -> Dict[str, Any]:
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_jwt_token(token)
    user_email = payload.get("sub")

    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await db_auth.get(user_email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
