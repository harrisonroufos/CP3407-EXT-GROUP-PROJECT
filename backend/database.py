import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Connect to PostgreSQL database with debugging."""
    print(f"📌 Attempting to connect to: {DATABASE_URL}")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None
