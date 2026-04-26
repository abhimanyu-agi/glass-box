"""
Shared database utilities.
Every node that hits Postgres uses these, so we have ONE connection policy.
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_conn(dict_cursor: bool = False):
    """
    Open a new Postgres connection.

    dict_cursor=True returns RealDictCursor (rows as dicts).
    Default is tuple rows (faster for pandas consumption).
    """
    kwargs = dict(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    if dict_cursor:
        kwargs["cursor_factory"] = RealDictCursor
    return psycopg2.connect(**kwargs)