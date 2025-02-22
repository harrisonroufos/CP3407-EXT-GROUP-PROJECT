import sqlite3
from backend.database import get_db_connection


def get_all_cleaners():
    """Fetch all cleaners from the database with error handling."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = conn.cursor()
        query = """
        SELECT cleaner_id, full_name, email, phone_number, bio, 
               location, rating, experience_years
        FROM cleaners
        """
        cursor.execute(query)
        cleaners = cursor.fetchall()
        conn.close()

        return [dict(cleaner) for cleaner in cleaners], 200  # Return JSON & status code

    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve cleaners"}, 500
