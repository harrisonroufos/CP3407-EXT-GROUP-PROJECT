import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
