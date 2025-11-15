from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException
from jose import jwt

from app.config import settings
from app.models import User


def create_jwt(user_id: str):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=2),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(x_access_token: str = Header(...)) -> User:
    try:
        payload = jwt.decode(
            x_access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="invalid token")
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="user not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


async def require_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="requires superuser")
    return current_user
