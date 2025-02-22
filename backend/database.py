import sqlite3
from backend.config import DATABASE_PATH


def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)  # Uses correct database file
        conn.row_factory = sqlite3.Row  # Allows dictionary-like access to rows
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None  # Handle gracefully in calling functions
