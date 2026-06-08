"""Verify we can connect to Postgres."""

import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn_string = os.environ["DATABASE_URL"]

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone())