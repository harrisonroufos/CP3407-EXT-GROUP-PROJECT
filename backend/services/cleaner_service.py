import psycopg2
from backend.database import get_db_connection


def get_all_cleaners():
    """Fetch all cleaners from the PostgreSQL database with error handling."""
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

        # Fetch column names
        columns = [desc[0] for desc in cursor.description]

        # Fetch all rows and convert them into a list of dictionaries
        cleaners = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return cleaners, 200  # Return JSON & status code

    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve cleaners"}, 500
