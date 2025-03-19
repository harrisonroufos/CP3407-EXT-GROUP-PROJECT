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

        # Attach computed average rating from reviews to each cleaner
        for cleaner in cleaners:
            cleaner['avg_rating'] = get_cleaner_average_rating(cleaner['cleaner_id'])

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

        # Add the computed average rating to the cleaner's profile
        cleaner['avg_rating'] = get_cleaner_average_rating(cleaner_id)

        conn.close()
        return cleaner, 200

    except Exception as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve cleaner profile"}, 500


def get_bookings_by_id(table_id, query):
    """Fetch all bookings by id."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = conn.cursor()
        cursor.execute(query, (table_id,))
        columns = [desc[0] for desc in cursor.description]
        bookings = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return bookings, 200

    except Exception as e:
        print(f"Database query error: {e}")
        return {"error": "Failed to retrieve bookings."}, 500


def get_cleaner_average_rating(cleaner_id):
    """Compute the average rating for a cleaner based on reviews."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"""
            SELECT AVG(r.rating)
            FROM reviews r
            JOIN bookings b ON r.booking_id = b.booking_id
            WHERE b.cleaner_id = {placeholder}
        """
        cursor.execute(query, (cleaner_id,))
        avg_rating = cursor.fetchone()[0]
        conn.close()
        return round(avg_rating, 2) if avg_rating else None
    except Exception as e:
        print(f"Rating fetch error: {e}")
        return None
