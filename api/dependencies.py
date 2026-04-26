"""FastAPI dependencies — injected into route handlers."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from api.models.user import UserPublic
from api.security import decode_access_token
from api.services import user_service


# tokenUrl tells Swagger where login lives — for the "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


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

    user = user_service.get_public_by_username(username)
    if user is None or not user.is_active:
        raise credentials_exception
    return user