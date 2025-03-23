"""
Authors: Harrison, Damon, Daniel, Casey
CP3407 EXT GROUP Assignment
This is the main Python/Flask file for the MyClean App
"""

import os, sqlite3, psycopg2, requests
from backend.routes.cleaner_routes import cleaner_bp
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import USE_LOCAL_DB
from backend.database import get_db_connection
from datetime import datetime
from contextlib import contextmanager
import json

# Initialise the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Set Flask's secure key for session management

# Retrieve the database URL from environment variables (used for Render deployment)
from backend.config import DATABASE_URL


@contextmanager
def db_cursor(commit=False):
    """
    Context manager that yields a (connection, cursor) tuple.
    Commits the transaction if commit=True; otherwise, rolls back on error.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_table_definitions():
    """
    Returns a dictionary of table creation queries based on the current environment.
    Uses PostgreSQL-compatible queries if DATABASE_URL is set, otherwise SQLite-compatible queries.
    """
    if DATABASE_URL:
        return {
            "users": '''CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY, 
                username TEXT UNIQUE NOT NULL, 
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "customers": '''CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                full_name TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL, 
                phone_number TEXT UNIQUE NOT NULL,
                location TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "cleaners": '''CREATE TABLE IF NOT EXISTS cleaners (
                cleaner_id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                full_name TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL, 
                phone_number TEXT UNIQUE NOT NULL,
                bio TEXT,
                location TEXT, 
                rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
                experience_years REAL CHECK (experience_years >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
                booking_id SERIAL PRIMARY KEY,
                cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                booking_date TIMESTAMP NOT NULL,
                status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "checklists": '''CREATE TABLE IF NOT EXISTS checklists (
                checklist_id SERIAL PRIMARY KEY,
                booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
                checklist_items JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "customer_checklists": '''CREATE TABLE IF NOT EXISTS customer_checklists (
                checklist_id SERIAL PRIMARY KEY,
                customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                checklist_items JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "reviews": '''CREATE TABLE IF NOT EXISTS reviews (
                review_id SERIAL PRIMARY KEY,
                booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
                question_1 TEXT,
                question_2 TEXT,
                question_3 TEXT,
                question_4 TEXT,
                rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        }
    else:
        return {
            "users": '''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT UNIQUE NOT NULL, 
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "customers": '''CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                full_name TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL, 
                phone_number TEXT UNIQUE NOT NULL,
                location TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "cleaners": '''CREATE TABLE IF NOT EXISTS cleaners (
                cleaner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                full_name TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL, 
                phone_number TEXT UNIQUE NOT NULL,
                bio TEXT,
                location TEXT, 
                rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
                experience_years REAL CHECK (experience_years >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                booking_date TIMESTAMP NOT NULL,
                status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "checklists": '''CREATE TABLE IF NOT EXISTS checklists (
                checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
                checklist_items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "customer_checklists": '''CREATE TABLE IF NOT EXISTS customer_checklists (
                checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                checklist_items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            "reviews": '''CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
                question_1 TEXT,
                question_2 TEXT,
                question_3 TEXT,
                question_4 TEXT,
                rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        }


def create_tables(tables):
    """
    Checks for the existence of each table and creates it if missing.
    Uses different queries for SQLite (local) versus PostgreSQL.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Checking if tables already exist...")
        for table, query in tables.items():
            if USE_LOCAL_DB:
                check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
            else:
                check_query = f"SELECT to_regclass('{table}');"
            cursor.execute(check_query)
            if cursor.fetchone() is None:
                print(f"Table {table} does not exist. Creating it...")
                cursor.execute(query)
            else:
                print(f"Table {table} already exists.")
        conn.commit()
    except Exception as e:
        print(f"❌ Error initializing the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def clear_local_db(cursor):
    """Clear the relevant tables to reset the database."""
    print("Clearing tables...")  # Debugging print statement
    # Delete from child tables first to avoid foreign key constraint errors.
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM checklists")
    cursor.execute("DELETE FROM customer_checklists")
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM cleaners")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM users")

    # If using SQLite, clear the auto-increment sequences as well.
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='reviews'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='checklists'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='customer_checklists'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='bookings'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='cleaners'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")

    cursor.connection.commit()


def insert_admin_data(cursor, db_type="sqlite"):
    print("Checking if admin data exists...")
    cursor.execute("SELECT COUNT(*) FROM users WHERE username IN ('admin', 'cleaner', 'customer')")
    count = cursor.fetchone()[0]

    if count != 0:
        return

    print("Inserting admin and initial data...")

    # Insert admin user into the 'users' table.
    if db_type == "postgres":
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            ('admin', '123')
        )
    else:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ('admin', '123')
        )

    # Retrieve the generated user_id.
    user_id = cursor.lastrowid
    if db_type == "postgres":
        cursor.execute("SELECT CURRVAL(pg_get_serial_sequence('users', 'user_id'))")
        user_id = cursor.fetchone()[0]

    # Helper to execute an INSERT query and return the generated id.
    def insert_record(query_sqlite, query_postgres, params):
        if db_type == "postgres":
            cursor.execute(query_postgres, params)
            # Check for RETURNING clause to fetch the generated id.
            return cursor.fetchone()[0] if "RETURNING" in query_postgres else None
        else:
            cursor.execute(query_sqlite, params)
            return cursor.lastrowid

    # Insert customer data.
    customer_id = insert_record(
        "INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (?, ?, ?, ?)",
        "INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (%s, %s, %s, %s) RETURNING customer_id",
        (user_id, 'Customer Name', 'customer123@example.com', '1234567891')
    )

    # Insert cleaner data.
    cleaner_id = insert_record(
        "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (?, ?, ?, ?, ?, ?)",
        "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (%s, %s, %s, %s, %s, %s) RETURNING cleaner_id",
        (user_id, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3)
    )

    # Insert dummy booking data.
    booking_id = insert_record(
        "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (?, ?, ?, ?)",
        "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (%s, %s, %s, %s) RETURNING booking_id",
        (cleaner_id, customer_id, '2025-02-21 09:00:00', 'pending')
    )

    # Insert a sample checklist for the new booking.
    if db_type == "postgres":
        cursor.execute(
            "INSERT INTO checklists (booking_id, checklist_items) VALUES (%s, %s)",
            (booking_id, '["Sample Checklist Item"]')
        )
    else:
        cursor.execute(
            "INSERT INTO checklists (booking_id, checklist_items) VALUES (?, ?)",
            (booking_id, '["Sample Checklist Item"]')
        )

    # Commit all changes.
    cursor.connection.commit()


def init_db():
    """
    Orchestrates the database initialization:
      1. Retrieves table definitions.
      2. Checks and creates tables as needed.
      3. (Optional) Clears tables (commented out).
      4. Inserts admin data into local and external databases.
    """
    print("Initializing the database...")

    # Step 1: Get table definitions based on environment.
    tables = get_table_definitions()

    # Step 2: Create tables if they don't exist.
    create_tables(tables)

    # Step 3: (Optional) Clear local DB tables for a fresh start.
    # with db_cursor(commit=True) as (conn, cursor):
    #     clear_tables(cursor)

    # Step 4: Insert admin and initial data.
    with db_cursor(commit=True) as (conn, cursor):
        insert_admin_data(cursor, db_type="sqlite" if USE_LOCAL_DB else "postgres")

    print("✅ Database initialized successfully.")


def fetch_cleaners_from_postgre():
    """Fetch cleaners with avg_rating using a single DB connection."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("Retrieving cleaner data from PostgreSQL database.")
        cursor.execute("""
            SELECT c.cleaner_id, c.full_name, c.email, c.phone_number, c.location,
                   c.rating, c.experience_years, AVG(r.rating)
            FROM cleaners c
            LEFT JOIN bookings b ON c.cleaner_id = b.cleaner_id
            LEFT JOIN reviews r ON b.booking_id = r.booking_id
            GROUP BY c.cleaner_id
        """)
        cleaners = []
        for row in cursor.fetchall():
            cleaner = {
                "cleaner_id": row[0],
                "full_name": row[1],
                "email": row[2] or "Not Available",
                "phone_number": row[3] or "Not Available",
                "location": row[4] or "Unknown Location",
                "rating": row[5] if row[5] is not None else "N/A",
                "experience_years": row[6] if row[6] is not None else "No experience listed",
                "avg_rating": round(row[7], 2) if row[7] is not None else None
            }
            cleaners.append(cleaner)

        return cleaners

    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()


def process_booking_date(bookings):
    for booking in bookings:
        # Get the booking date value
        booking_date = booking["booking_date"]

        # If it's a string, parse it; if it's already a datetime, use it directly.
        if isinstance(booking_date, str):
            try:
                booking_datetime = datetime.strptime(booking_date, '%a, %d %b %Y %H:%M:%S %Z')
            except ValueError:
                # Fallback: try ISO format if the above format doesn't match
                booking_datetime = datetime.fromisoformat(booking_date)
        elif isinstance(booking_date, datetime):
            booking_datetime = booking_date
        else:
            # Optionally, handle unexpected types
            booking_datetime = datetime.fromisoformat(str(booking_date))

        booking["booking_time"] = booking_datetime.strftime('%H:%M')
        booking["booking_date"] = booking_datetime.strftime('%d-%m-%Y')


# def init_db():
#     print("Initialising the database...")
#     conn = None
#     cursor = None
#
#     if DATABASE_URL:
#         # PostgreSQL-compatible table creation queries
#         tables = {
#             "users": '''CREATE TABLE IF NOT EXISTS users (
#                 user_id SERIAL PRIMARY KEY,
#                 username TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "customers": '''CREATE TABLE IF NOT EXISTS customers (
#                 customer_id SERIAL PRIMARY KEY,
#                 user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
#                 full_name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 phone_number TEXT UNIQUE NOT NULL,
#                 location TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "cleaners": '''CREATE TABLE IF NOT EXISTS cleaners (
#                 cleaner_id SERIAL PRIMARY KEY,
#                 user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
#                 full_name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 phone_number TEXT UNIQUE NOT NULL,
#                 bio TEXT,
#                 location TEXT,
#                 rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
#                 experience_years REAL CHECK (experience_years >= 0),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
#                 booking_id SERIAL PRIMARY KEY,
#                 cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
#                 customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
#                 booking_date TIMESTAMP NOT NULL,
#                 status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "checklists": '''CREATE TABLE IF NOT EXISTS checklists (
#                 checklist_id SERIAL PRIMARY KEY,
#                 booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
#                 checklist_items JSON NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "customer_checklists": '''CREATE TABLE IF NOT EXISTS customer_checklists (
#                 checklist_id SERIAL PRIMARY KEY,
#                 customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
#                 checklist_items JSON NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 )''',
#             "reviews": '''CREATE TABLE IF NOT EXISTS reviews (
#                 review_id SERIAL PRIMARY KEY,
#                 booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
#                 question_1 TEXT,
#                 question_2 TEXT,
#                 question_3 TEXT,
#                 question_4 TEXT,
#                 rating REAL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )'''
#         }
#     else:
#         # SQLite-compatible table creation queries
#         tables = {
#             "users": '''CREATE TABLE IF NOT EXISTS users (
#                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "customers": '''CREATE TABLE IF NOT EXISTS customers (
#                 customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
#                 full_name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 phone_number TEXT UNIQUE NOT NULL,
#                 location TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "cleaners": '''CREATE TABLE IF NOT EXISTS cleaners (
#                 cleaner_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
#                 full_name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 phone_number TEXT UNIQUE NOT NULL,
#                 bio TEXT,
#                 location TEXT,
#                 rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
#                 experience_years REAL CHECK (experience_years >= 0),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
#                 booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
#                 customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
#                 booking_date TIMESTAMP NOT NULL,
#                 status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "checklists": '''CREATE TABLE IF NOT EXISTS checklists (
#                 checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
#                 checklist_items TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "customer_checklists": '''CREATE TABLE IF NOT EXISTS customer_checklists (
#                 checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 customer_id INTEGER UNIQUE NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
#                 checklist_items TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )''',
#             "reviews": '''CREATE TABLE IF NOT EXISTS reviews (
#                 review_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
#                 question_1 TEXT,
#                 question_2 TEXT,
#                 question_3 TEXT,
#                 question_4 TEXT,
#                 rating REAL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )'''
#         }
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         print("Checking if tables already exist...")
#         for table, query in tables.items():
#             if USE_LOCAL_DB:
#                 check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
#             else:
#                 check_query = f"SELECT to_regclass('{table}');"
#
#             cursor.execute(check_query)
#             if cursor.fetchone() is None:
#                 print(f"Table {table} does not exist. Creating it...")
#                 cursor.execute(query)
#             else:
#                 print(f"Table {table} already exists.")
#
#         # (Leave the rest of your init_db code here, e.g., inserting admin data, etc.)
#         conn.commit()
#         print("✅ Database initialized successfully.")
#     except Exception as e:
#         print(f"❌ Error initializing the database: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


@app.route("/show_cleaners", methods=["GET"])
def show_cleaners():
    """Fetch cleaners from the API in local development, or directly from the database in production."""

    if DATABASE_URL:  # If running on Render (PostgreSQL)
        print("Using external environment PostgreSQL.")
        cleaners = fetch_cleaners_from_postgre()  # Query database on Render
    else:  # If using SQLite (local development), call the webhook
        print("Using local environment MySQLite.")
        try:
            response = requests.get("http://127.0.0.1:5000/cleaners")
            response.raise_for_status()
            cleaners = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cleaners: {e}")
            cleaners = []  # Return an empty list if there's an error

    return render_template('index.html', cleaners=cleaners)


@app.route("/manage_bookings", methods=["GET"])
def manage_bookings():
    """Fetch bookings directly from the database and include the full name."""
    if session.get('cleaner_id') or session.get('customer_id'):
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"

        if session.get('cleaner_id'):
            # If a cleaner is logged in, fetch bookings with the customer's name.
            query = f"""
                SELECT b.*, cu.full_name, cu.location
                FROM bookings b
                JOIN customers cu ON b.customer_id = cu.customer_id
                WHERE b.cleaner_id = {placeholder}
            """
            cursor.execute(query, (session['cleaner_id'],))
        elif session.get('customer_id'):
            # If a customer is logged in, fetch bookings with the cleaner's name.
            query = f"""
                SELECT b.*, c.full_name, c.location
                FROM bookings b
                JOIN cleaners c ON b.cleaner_id = c.cleaner_id
                WHERE b.customer_id = {placeholder}
            """
            cursor.execute(query, (session['customer_id'],))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        bookings = [dict(zip(columns, row)) for row in rows]
        process_booking_date(bookings)
        conn.close()
    else:
        return redirect(url_for("show_cleaners"))

    return render_template('manage_bookings.html', bookings=bookings)


@app.route("/delete_booking/<int:booking_id>", methods=["GET"])
def delete_booking(booking_id):
    if session.get('cleaner_id') or session.get('customer_id'):
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"
        cursor.execute(f"""DELETE FROM bookings WHERE booking_id = {placeholder}""", (booking_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("manage_bookings"))
    else:
        return redirect(url_for("show_cleaners"))


@app.route("/book/<int:cleaner_id>", methods=["GET", "POST"])
def book_cleaner(cleaner_id):
    if "customer_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["customer_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine correct placeholder syntax
    placeholder = "?" if USE_LOCAL_DB else "%s"

    # Validate if the cleaner exists
    query = f"SELECT full_name, location FROM cleaners WHERE cleaner_id = {placeholder}"
    cursor.execute(query, (cleaner_id,))
    cleaner = cursor.fetchone()

    if not cleaner:
        abort(404)  # Cleaner not found → return 404 error.

    if request.method == "POST":
        booking_date = request.form.get("booking_date")
        checklist_items = request.form.get("checklist_items", "").strip()

        # Validate date format
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%dT%H:%M")

        # Insert booking into database
        if USE_LOCAL_DB:
            query = f"""
                INSERT INTO bookings (cleaner_id, customer_id, booking_date, status, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (cleaner_id, customer_id, booking_date, "pending"))
            booking_id = cursor.lastrowid  # Get last inserted row ID for SQLite
        else:
            query = f"""
                INSERT INTO bookings (cleaner_id, customer_id, booking_date, status, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, NOW()) RETURNING booking_id
            """
            cursor.execute(query, (cleaner_id, customer_id, booking_date, "pending"))
            booking_id = cursor.fetchone()[0]  # Get booking ID for PostgreSQL

        # Insert checklist items if any
        if checklist_items:
            checklist_lines = [item.strip() for item in checklist_items.split("\n") if item.strip()]
            for item in checklist_lines:
                query = f"INSERT INTO checklists (booking_id, checklist_items) VALUES ({placeholder}, {placeholder})"
                cursor.execute(query, (booking_id, item))

        conn.commit()
        conn.close()

        print(f"✅ Booking created! Redirecting to payment page with ID: {booking_id}")
        return redirect(url_for("payment", booking_id=booking_id))

    conn.close()
    return render_template("book_cleaner.html", cleaner_id=cleaner_id)


@app.route("/payment/<int:booking_id>", methods=["GET", "POST"])
def payment(booking_id):
    if request.method == "POST":
        # Simulate a successful payment
        print(f"✅ Payment simulated for Booking ID: {booking_id}")
        return redirect(url_for("booking_confirmation", booking_id=booking_id))

    return render_template("payment.html", booking_id=booking_id)


@app.route("/booking-confirmation/<int:booking_id>")
def booking_confirmation(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine the correct placeholder syntax
    placeholder = "?" if USE_LOCAL_DB else "%s"

    try:
        # Fetch booking details along with cleaner name and location
        query = f"""
            SELECT b.booking_id, b.booking_date, c.full_name, c.location
            FROM bookings b
            JOIN cleaners c ON b.cleaner_id = c.cleaner_id
            WHERE b.booking_id = {placeholder}
        """
        cursor.execute(query, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            abort(404)  # Booking not found → return 404 error.

        # Fix the error: Convert string to datetime if needed
        booking_date = booking[1]

        # If booking_date is a string (likely in SQLite), parse it correctly
        if isinstance(booking_date, str):
            try:
                # Handle 'YYYY-MM-DDTHH:MM' format from form input
                if "T" in booking_date:
                    booking_date = datetime.strptime(booking_date, "%Y-%m-%dT%H:%M")
                else:
                    # Handle standard SQLite format 'YYYY-MM-DD HH:MM:SS'
                    booking_date = datetime.strptime(booking_date, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"⚠️ Date parsing error: {e}")  # Debugging
                abort(500)  # Internal Server Error if parsing fails

        return render_template("booking_confirmation.html",
                               booking_id=booking[0],
                               booking_date=booking_date.strftime("%Y-%m-%d %H:%M"),
                               cleaner_name=booking[2], location=booking[3])

    finally:
        conn.close()


@app.route("/cleaner/<int:cleaner_id>", methods=["GET"])
def show_cleaner_profile(cleaner_id):
    """Fetch a cleaner's information, using direct DB query for production and API call for local."""
    if DATABASE_URL:
        # Production environment: query the database directly.
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"""
            SELECT cleaner_id, user_id, full_name, email, phone_number, location, bio, rating, experience_years
            FROM cleaners
            WHERE cleaner_id = {placeholder}
        """
        cursor.execute(query, (cleaner_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            cleaner = dict(zip(columns, row))
        else:
            cleaner = {}
        conn.close()
    else:
        # Local environment: call the local API endpoint.
        response = requests.get("http://127.0.0.1:5000/cleaners/" + str(cleaner_id))
        response.raise_for_status()
        cleaner = response.json()

    return render_template('profile.html', cleaner=cleaner)


@app.route("/cleaner/<int:cleaner_id>/edit", methods=["GET", "POST"])
def edit_cleaner_profile(cleaner_id):
    if session['cleaner_id'] != cleaner_id and request.method == "GET":
        return redirect(url_for('show_cleaners'))

    if session['cleaner_id'] == cleaner_id and request.method == "POST":
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        location = request.form['location']
        bio = request.form['bio']
        experience_years = request.form.get('experience_years', 0)  # Default to 0 if not provided

        conn = get_db_connection()
        cursor = conn.cursor()

        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"UPDATE cleaners SET full_name = {placeholder}, email = {placeholder}, phone_number = {placeholder}, location = {placeholder}, bio = {placeholder}, experience_years = {placeholder} WHERE cleaner_id = {placeholder}"
        cursor.execute(query, (full_name, email, phone_number, location, bio, experience_years, session['cleaner_id']))

        query = f"UPDATE users SET username = {placeholder} WHERE user_id = {placeholder}"
        cursor.execute(query, (username, session['user_id']))
        session['username'] = username

        conn.commit()
        conn.close()

        return redirect(url_for('show_cleaners'))

    if session['customer_id'] and request.method == "GET":
        return redirect(url_for('show_cleaners'))

    return render_template('edit_cleaner_info.html')


@app.route("/customer/edit", methods=["GET", "POST"])
def edit_customer_info():
    if request.method == "POST":
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        location = request.form['location']

        conn = get_db_connection()
        cursor = conn.cursor()

        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"UPDATE customers SET full_name = {placeholder}, email = {placeholder}, phone_number = {placeholder}, location = {placeholder} WHERE customer_id = {placeholder}"
        cursor.execute(query, (full_name, email, phone_number, location, session['customer_id']))

        query = f"UPDATE users SET username = {placeholder} WHERE user_id = {placeholder}"
        cursor.execute(query, (username, session['user_id']))

        session['username'] = username

        conn.commit()
        conn.close()

        return redirect(url_for('show_cleaners'))

    if session['cleaner_id'] and request.method == "GET":
        return redirect(url_for('show_cleaners'))

    return render_template('edit_customer_info.html')


@app.route('/booking_review/<int:booking_id>')
def booking_review(booking_id):
    session['booking_id'] = booking_id
    return redirect(url_for('review'))


@app.route('/review')
def review():
    if 'booking_id' not in session:
        flash("No booking selected for review.", "error")
        return redirect(url_for("show_cleaners"))
    return render_template('review.html')


@app.route("/submit_review", methods=["POST"])
def submit_review():
    # Retrieve form data from the reviews.html page
    booking_id = request.form.get("booking_id")
    question_1 = request.form.get("question_1")
    question_2 = request.form.get("question_2")
    question_3 = request.form.get("question_3")
    question_4 = request.form.get("question_4")
    rating = request.form.get("rating")

    # Convert the received values to the correct types.
    # Since the sliders provide values as strings, convert them to integers.
    try:
        booking_id = int(booking_id)
        question_1 = int(question_1)
        question_2 = int(question_2)
        question_3 = int(question_3)
        question_4 = int(question_4)
        rating = float(rating)  # Using float in case you want decimal ratings later.
    except Exception as e:
        flash("Invalid review data provided.", "error")
        return redirect(url_for("review"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine the correct placeholder syntax for the current DB.
    placeholder = "?" if USE_LOCAL_DB else "%s"

    # Insert the review data into the 'reviews' table.
    query = (
        f"INSERT INTO reviews (booking_id, question_1, question_2, question_3, question_4, rating) "
        f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
    )

    try:
        cursor.execute(query, (booking_id, question_1, question_2, question_3, question_4, rating))
        conn.commit()
        flash("Review submitted successfully!", "success")
    except Exception as e:
        print(f"Error inserting review: {e}")
        conn.rollback()
        flash("There was an error submitting your review. Please try again.", "error")
    finally:
        cursor.close()
        conn.close()

    # Redirect the user to the cleaners page (or another confirmation page as desired)
    return redirect(url_for("show_cleaners"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Login POST triggered.")
        username = request.form['username']
        password = request.form['password']
        print(f"Username entered: {username}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Use conditional placeholder
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"SELECT user_id, username, password FROM users WHERE username = {placeholder}"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            print("🔍 User found in DB.")
            stored_hashed_password = user[2]  # Stored password hash

            if check_password_hash(stored_hashed_password, password):
                print("✅ Password matches.")
                # Successful login; set session data
                session['user_id'] = user[0]
                session['username'] = user[1]

                # Determine whether the user is a cleaner or a customer
                cursor.execute(f"SELECT cleaner_id FROM cleaners WHERE user_id = {placeholder}", (user[0],))
                cleaner_result = cursor.fetchone()

                if cleaner_result is not None:
                    # User is a cleaner
                    session['cleaner_id'] = cleaner_result[0]
                    session['customer_id'] = False
                    print(f"🔍 Cleaner record found: cleaner_id = {cleaner_result[0]}")
                else:
                    print("ℹ️ No cleaner record found for this user.")
                    # If not a cleaner, check if user is a customer
                    cursor.execute(f"SELECT customer_id FROM customers WHERE user_id = {placeholder}", (user[0],))
                    customer_result = cursor.fetchone()
                    if customer_result is not None:
                        session['customer_id'] = customer_result[0]
                        session['cleaner_id'] = False
                        print(f"🔍 Customer record found: customer_id = {customer_result[0]}")
                    else:
                        # If neither table matches, set both to False
                        session['customer_id'] = False
                        session['cleaner_id'] = False
                        print("⚠️ No cleaner or customer record found for this user.")

                conn.close()
                print("🚀 Redirecting to show_cleaners.")
                return redirect(url_for('show_cleaners'))
            else:
                print("❌ Password mismatch.")
                conn.close()
                return render_template("login.html", error="❌ Invalid credentials!")
        else:
            print("❌ Username not found.")
            conn.close()
            return render_template("login.html", error="❌ Invalid credentials!")

    print("Login GET triggered.")
    return render_template('login.html')


@app.route('/aboutus')
def about_us():
    return render_template('about_us.html')


@app.route('/view_checklist')
def view_checklist():
    if not session.get("cleaner_id"):
        flash("Access restricted to cleaners only.", "error")
        return redirect(url_for("login"))

    booking_id = request.args.get("booking_id", type=int)
    if not booking_id:
        flash("No booking selected for review.", "error")
        return redirect(url_for("manage_bookings"))

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = "?" if USE_LOCAL_DB else "%s"

    # Get customer_id from the booking
    cursor.execute(f"SELECT customer_id FROM bookings WHERE booking_id = {placeholder}", (booking_id,))
    booking = cursor.fetchone()
    if not booking:
        flash("Booking not found.", "error")
        cursor.close()
        conn.close()
        return redirect(url_for("manage_bookings"))
    customer_id = booking[0]

    # Retrieve the customer's name
    cursor.execute("SELECT full_name FROM customers WHERE customer_id = " + placeholder, (customer_id,))
    customer = cursor.fetchone()
    customer_name = customer[0] if customer else "Customer"

    # Retrieve the checklist for the customer
    cursor.execute("SELECT checklist_items FROM customer_checklists WHERE customer_id = " + placeholder, (customer_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    checklist_items = (
        json.loads(row[0]) if row and isinstance(row[0], str) else row[0] if row else []
    )

    return render_template("view_checklist.html", checklist_items=checklist_items, customer_name=customer_name)


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user_type = request.form['user_type']
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        location = request.form['location']
        experience_years = request.form.get('experience_years', 0)  # Default to 0 if not provided

        conn = get_db_connection()
        cursor = conn.cursor()

        placeholder = "?" if USE_LOCAL_DB else "%s"
        # Check if username already exists
        query = f"SELECT username FROM users WHERE username = {placeholder}"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()

        # Check if email already exists in either customers or cleaners
        query = f"SELECT email FROM customers WHERE email = {placeholder} UNION SELECT email FROM cleaners WHERE email = {placeholder}"
        cursor.execute(query, (email, email))
        existing_email = cursor.fetchone()

        # Check if phone number already exists in either customers or cleaners
        query = f"SELECT phone_number FROM customers WHERE phone_number = {placeholder} UNION SELECT phone_number FROM cleaners WHERE phone_number = {placeholder}"
        cursor.execute(query, (phone_number, phone_number))
        existing_phone = cursor.fetchone()

        if existing_user:
            conn.close()
            return render_template("signup.html", error="Username already exists!")

        if existing_email:
            conn.close()
            return render_template("signup.html", error="Email is already registered!")

        if existing_phone:
            conn.close()
            return render_template("signup.html", error="Phone number is already in use!")

        # Insert into users table
        if USE_LOCAL_DB:
            query = f"INSERT INTO users (username, password) VALUES ({placeholder}, {placeholder})"
            cursor.execute(query, (username, hashed_password))
            user_id = cursor.lastrowid
        else:
            query = f"INSERT INTO users (username, password) VALUES ({placeholder}, {placeholder}) RETURNING user_id"
            cursor.execute(query, (username, hashed_password))
            user_id = cursor.fetchone()[0]

        # Insert into either customers or cleaners table
        if user_type == 'customer':
            query = f"INSERT INTO customers (user_id, full_name, email, phone_number, location) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
            cursor.execute(query, (user_id, full_name, email, phone_number, location))
        else:
            query = f"INSERT INTO cleaners (user_id, full_name, email, phone_number, location, experience_years) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
            cursor.execute(query, (user_id, full_name, email, phone_number, location, experience_years))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))  # Redirect to login page after signup

    return render_template('signup.html')


@app.route("/custom_checklist", methods=["GET", "POST"])
def custom_checklist():
    if "customer_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["customer_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = "?" if USE_LOCAL_DB else "%s"

    if request.method == "POST":
        # Retrieve checklist items from the form
        checklist_items = request.form.getlist("checklist_items")
        checklist_json = json.dumps(checklist_items)

        # Check if a checklist for this customer already exists
        cursor.execute("SELECT checklist_id FROM customer_checklists WHERE customer_id = " + placeholder,
                       (customer_id,))
        row = cursor.fetchone()

        if row:
            # Update existing checklist
            update_query = ("UPDATE customer_checklists SET checklist_items = " + placeholder +
                            ", updated_at = CURRENT_TIMESTAMP WHERE checklist_id = " + placeholder)
            cursor.execute(update_query, (checklist_json, row[0]))
        else:
            # Insert new checklist record for the customer
            insert_query = ("INSERT INTO customer_checklists (customer_id, checklist_items) VALUES (" +
                            placeholder + ", " + placeholder + ")")
            cursor.execute(insert_query, (customer_id, checklist_json))
        conn.commit()
        conn.close()
        flash("Checklist saved successfully!", "success")
        return redirect(url_for("custom_checklist"))

    # Retrieve existing checklist for GET request
    cursor.execute("SELECT checklist_items FROM customer_checklists WHERE customer_id = " + placeholder, (customer_id,))
    row = cursor.fetchone()
    if row:
        # For SQLite, the JSON is stored as a string, so we parse it; PostgreSQL returns a native type.
        if isinstance(row[0], str):
            checklist_items = json.loads(row[0])
        else:
            checklist_items = row[0]
    else:
        checklist_items = []
    conn.close()
    return render_template("custom_checklist.html", checklist_items=checklist_items)


@app.route("/logout")
def logout():
    print("Logging out the user.")  # Debugging print statement
    session.clear()
    return redirect(url_for("login"))


# Register blueprints
app.register_blueprint(cleaner_bp)  # This is required!

# Run the Flask app in debug mode
if __name__ == "__main__":
    if os.environ.get("FLASK_RUN_MAIN") != "true":  # Prevents duplicate execution
        print(f"🔄 Initialising {'local SQLite' if USE_LOCAL_DB else 'PostgreSQL'} database...")
        init_db()

    print("\n=== Registered Routes ===")
    print(app.url_map)  # Forces Flask to print available routes
    print("========================\n")

    app.run(debug=True)
