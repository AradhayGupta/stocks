"""Shared Postgres connection helper."""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set in environment")
    return psycopg2.connect(url)
