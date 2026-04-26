"""
Initialize authentication schema.

Creates the `users` table in finance_poc and seeds two demo accounts:
  - admin / admin123
  - cfo   / demo123

Run once:  python -m api.scripts.init_auth
Idempotent: safe to re-run — skips users that already exist.
"""

import sys
from pathlib import Path

# Path fix so we can import agent.db from inside api/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from passlib.context import CryptContext

from agent.db import get_conn


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(64)  UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    full_name       VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(32)  NOT NULL DEFAULT 'viewer',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
"""


DEMO_USERS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "admin123",
        "role": "admin",
    },
    {
        "username": "cfo",
        "email": "cfo@example.com",
        "full_name": "Demo CFO",
        "password": "demo123",
        "role": "viewer",
    },
]


def main():
    print("Connecting to Postgres…")
    with get_conn() as conn:
        with conn.cursor() as cur:
            print("Creating users table (if missing)…")
            cur.execute(CREATE_TABLE_SQL)

            for u in DEMO_USERS:
                cur.execute("SELECT id FROM users WHERE username = %s", (u["username"],))
                if cur.fetchone():
                    print(f"  · {u['username']:<10} already exists — skipping")
                    continue

                hashed = pwd_context.hash(u["password"])
                cur.execute(
                    """
                    INSERT INTO users (username, email, full_name, hashed_password, role)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (u["username"], u["email"], u["full_name"], hashed, u["role"]),
                )
                print(f"  ✓ {u['username']:<10} created  (password: {u['password']})")

        conn.commit()

    print("\nDone. Two accounts ready:")
    print("  admin / admin123")
    print("  cfo   / demo123")


if __name__ == "__main__":
    main()