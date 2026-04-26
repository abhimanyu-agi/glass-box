"""
Shared database utilities.

Uses a lazily-initialized SimpleConnectionPool so the agent reuses connections
across nodes (retrieve + execute, plus repair re-execs) and across requests
when invoked from FastAPI. Standalone CLI scripts get the same benefit —
the pool initializes on first call.
"""

import os
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2 import pool as pg_pool

load_dotenv()


_pool: pg_pool.SimpleConnectionPool | None = None


def _get_pool() -> pg_pool.SimpleConnectionPool:
    global _pool
    if _pool is None:
        _pool = pg_pool.SimpleConnectionPool(
            minconn=1,
            maxconn=int(os.getenv("AGENT_POOL_MAX", "10")),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
    return _pool


@contextmanager
def get_conn():
    """
    Yields a pooled Postgres connection. Commits on success, rolls back on error,
    and always returns the connection to the pool.

    Callers that need dict rows should pass cursor_factory at cursor creation:
        with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
    """
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
