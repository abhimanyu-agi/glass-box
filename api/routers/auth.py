"""/auth/* — register, login, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from api.config import settings
from api.dependencies import get_current_user
from api.models.user import Token, UserCreate, UserPublic
from api.security import create_access_token, hash_password, verify_password
from api.services import user_service
from api.db import get_conn


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
def register(user: UserCreate):
    """Create a new user account."""
    existing = user_service.get_public_by_username(user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already taken",
        )
    return user_service.create(user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2-compatible login (username + password).
    Returns JWT bearer token + user info.
    """
    user = user_service.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=user.username,
        extra_claims={"user_id": user.id, "role": user.role},
    )
    return Token(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        user=user,
    )


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: UserPublic = Depends(get_current_user)):
    """Return the user corresponding to the current JWT."""
    return current_user

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password:     str = Field(..., min_length=6, max_length=128)


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    current_user: UserPublic = Depends(get_current_user),
):
    """Change the logged-in user's password."""
    # Re-fetch the full row to get the current hashed_password
    row = user_service.get_by_username(current_user.username)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = row[8]  # last column from get_by_username SELECT

    if not verify_password(body.current_password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    new_hash = hash_password(body.new_password)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET hashed_password = %s WHERE id = %s",
                (new_hash, current_user.id),
            )
    # 204 = success with no body
    return None