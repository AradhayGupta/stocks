"""Run schema.sql against the configured Postgres database.

Usage:
    python db/migrate.py

Reads DATABASE_URL from environment (or .env file).
"""
import os
import pathlib

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SCHEMA = pathlib.Path(__file__).with_name("schema.sql").read_text()


def migrate():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set in environment")

    conn = psycopg2.connect(url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA)
        print("Migration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
