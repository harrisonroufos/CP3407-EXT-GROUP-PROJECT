import psycopg2
from backend.database import get_db_connection
from backend.config import USE_LOCAL_DB


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


def get_cleaner_by_id(cleaner_id):
    """Fetch a single cleaner's profile based on their ID."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"""
        SELECT cleaner_id, full_name, email, phone_number, bio, 
               location, rating, experience_years
        FROM cleaners
        WHERE cleaner_id = {placeholder}
        """
        cursor.execute(query, (cleaner_id,))
        row = cursor.fetchone()

        if not row:
            return {"error": "Cleaner not found"}, 404

        columns = [desc[0] for desc in cursor.description]
        cleaner = dict(zip(columns, row))

        conn.close()
        return cleaner, 200

    except Exception as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve cleaner profile"}, 500


def get_bookings_by_id(customer_id):
    """Fetch all of a customer's bookings."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"""
        SELECT b.booking_id, b.cleaner_id, b.booking_date, b.status, c.full_name
        FROM bookings b
        JOIN cleaners c ON b.cleaner_id = c.cleaner_id
        WHERE b.customer_id = {placeholder}
        """
        cursor.execute(query, (customer_id,))
        columns = [desc[0] for desc in cursor.description]
        bookings = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return bookings, 200

    except Exception as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve bookings"}, 500
