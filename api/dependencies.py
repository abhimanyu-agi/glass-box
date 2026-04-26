"""FastAPI dependencies — injected into route handlers."""

from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from threading import Lock

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from api.models.user import UserPublic
from api.security import decode_access_token
from api.services import user_service


# tokenUrl tells Swagger where login lives — for the "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Short TTL cache so dashboard fan-out (5 parallel requests) doesn't hit the DB
# 5x for user lookup. Trade-off: account disable / role change can take up to
# `ttl` seconds to propagate to in-flight tokens.
_user_cache: TTLCache = TTLCache(maxsize=512, ttl=60)
_user_cache_lock = Lock()


@cached(_user_cache, key=lambda username: hashkey(username), lock=_user_cache_lock)
def _cached_user_for_auth(username: str) -> UserPublic | None:
    return user_service.get_public_by_username(username)


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    """
    Validates JWT, loads user. Raises 401 if anything is wrong.
    Use on any endpoint that requires auth:
        def my_endpoint(user: UserPublic = Depends(get_current_user)):
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = _cached_user_for_auth(username)
    if user is None or not user.is_active:
        raise credentials_exception
    return user