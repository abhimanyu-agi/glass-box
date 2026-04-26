"""User CRUD operations."""

from datetime import datetime, timezone

from api.db import get_conn
from api.models.user import UserCreate, UserPublic
from api.security import hash_password, verify_password


def _row_to_public(row) -> UserPublic:
    return UserPublic(
        id=row[0],
        username=row[1],
        email=row[2],
        full_name=row[3],
        role=row[4],
        is_active=row[5],
        created_at=row[6],
        last_login=row[7],
    )


def get_by_username(username: str) -> tuple | None:
    """
    Returns full row (id, username, email, full_name, role, is_active,
    created_at, last_login, hashed_password) — used internally for auth.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, email, full_name, role, is_active,
                       created_at, last_login, hashed_password
                FROM users
                WHERE username = %s
            """, (username,))
            return cur.fetchone()


def get_public_by_username(username: str) -> UserPublic | None:
    row = get_by_username(username)
    return _row_to_public(row) if row else None


def create(user: UserCreate) -> UserPublic:
    hashed = hash_password(user.password)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, email, full_name, hashed_password, role)
                VALUES (%s, %s, %s, %s, 'viewer')
                RETURNING id, username, email, full_name, role, is_active,
                          created_at, last_login
            """, (user.username, user.email, user.full_name, hashed))
            row = cur.fetchone()
            return _row_to_public(row)


def authenticate(username: str, password: str) -> UserPublic | None:
    """Returns the user if password matches AND account is active. Else None."""
    row = get_by_username(username)
    if row is None:
        return None

    user_id, uname, email, full_name, role, is_active, created_at, last_login, hashed_pw = row

    if not is_active:
        return None
    if not verify_password(password, hashed_pw):
        return None

    # Update last_login
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(timezone.utc), user_id),
            )

    return UserPublic(
        id=user_id,
        username=uname,
        email=email,
        full_name=full_name,
        role=role,
        is_active=is_active,
        created_at=created_at,
        last_login=datetime.now(timezone.utc),
    )