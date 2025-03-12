import os
import sqlite3
import psycopg2
from backend.config import DATABASE_URL, USE_LOCAL_DB


def get_db_connection():
    """Connect to SQLite or PostgreSQL based on `USE_LOCAL_DB` flag."""
    print(f"📌 Connecting to {'SQLite' if USE_LOCAL_DB else 'PostgreSQL'}")

    try:
        if USE_LOCAL_DB:
            conn = sqlite3.connect(DATABASE_URL)  # ✅ Correct SQLite connection (file path)
        else:
            conn = psycopg2.connect(DATABASE_URL)  # ✅ Correct PostgreSQL connection

        print("✅ Database connection successful!")
        return conn

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None
