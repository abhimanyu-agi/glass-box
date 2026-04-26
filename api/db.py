"""
Postgres connection pool for FastAPI.

One pool, shared across all requests. Handles concurrent
dashboard queries + chat queries + auth lookups without
opening a new connection per request.
"""

from contextlib import contextmanager
from psycopg2 import pool as pg_pool

from api.config import settings


_pool: pg_pool.SimpleConnectionPool | None = None


def init_pool():
    """Called once at FastAPI startup."""
    global _pool
    if _pool is None:
        _pool = pg_pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )


def close_pool():
    """Called once at FastAPI shutdown."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_conn():
    """
    Usage:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """
    if _pool is None:
        raise RuntimeError("DB pool not initialized. Call init_pool() first.")
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)