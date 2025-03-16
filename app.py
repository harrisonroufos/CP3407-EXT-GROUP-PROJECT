"""
Authors: Harrison, Damon, Daniel, Casey
CP3407 EXT GROUP Assignment
This is the main Python/Flask file for the MyClean App
"""

import os, sqlite3, psycopg2, requests
from backend.routes.cleaner_routes import cleaner_bp
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import USE_LOCAL_DB
from backend.database import get_db_connection
import json
from datetime import datetime

# Initialise the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Set Flask's secure key for session management

# Retrieve the database URL from environment variables (used for Render deployment)
from backend.config import DATABASE_URL


def create_table(cursor, query):
    """Create a table using the provided query."""
    print(f"Executing query: {query}")  # Debugging print statement
    cursor.execute(query)


def insert_admin_data(cursor, db_type="sqlite"):
    print("Checking if admin data exists...")
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username IN ('admin', 'cleaner', 'customer')"
    )
    count = cursor.fetchone()[0]

    if count == 0:
        print("Inserting admin and initial data...")

        # Insert admin user into the 'users' table
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

        # Get the user_id for the admin
        user_id = cursor.lastrowid
        if db_type == "postgres":
            cursor.execute("SELECT CURRVAL(pg_get_serial_sequence('users', 'user_id'))")
            user_id = cursor.fetchone()[0]

        # Insert customer data into the 'customers' table and retrieve customer_id
        if db_type == "postgres":
            cursor.execute(
                "INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (%s, %s, %s, %s) RETURNING customer_id",
                (user_id, 'Customer Name', 'customer123@example.com', '1234567891')
            )
            customer_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                "INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (?, ?, ?, ?)",
                (user_id, 'Customer Name', 'customer123@example.com', '1234567891')
            )
            customer_id = cursor.lastrowid

        # Insert cleaner data into the 'cleaners' table and retrieve cleaner_id
        if db_type == "postgres":
            cursor.execute(
                "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (%s, %s, %s, %s, %s, %s) RETURNING cleaner_id",
                (user_id, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3)
            )
            cleaner_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3)
            )
            cleaner_id = cursor.lastrowid

        # Insert dummy booking data using the retrieved cleaner_id and customer_id
        if db_type == "postgres":
            cursor.execute(
                "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (%s, %s, %s, %s)",
                (cleaner_id, customer_id, '2025-02-21 09:00:00', 'pending')
            )
        else:
            cursor.execute(
                "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (?, ?, ?, ?)",
                (cleaner_id, customer_id, '2025-02-21 09:00:00', 'pending')
            )

        # Commit changes
        cursor.connection.commit()


def clear_tables(cursor):
    """Clear the relevant tables to reset the database."""
    print("Clearing tables...")  # Debugging print statement
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM cleaners")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='cleaners'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='bookings'")
    cursor.connection.commit()


def fetch_cleaners_from_postgre():
    """Fetch cleaners directly from the PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("Retrieving cleaner data from PostgreSQL database.")
        cursor.execute("""
            SELECT cleaner_id, full_name, email, phone_number, location, rating, experience_years 
            FROM cleaners
        """)
        return [
            {
                "cleaner_id": row[0],
                "full_name": row[1],
                "email": row[2] or "Not Available",
                "phone_number": row[3] or "Not Available",
                "location": row[4] or "Unknown Location",
                "rating": row[5] if row[5] is not None else "N/A",
                "experience_years": row[6] if row[6] is not None else "No experience listed"
            }
            for row in cursor.fetchall()
        ]
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()


def process_booking_date(bookings):
    for booking in bookings:
        booking_datetime = datetime.strptime(booking["booking_date"], '%a, %d %b %Y %H:%M:%S %Z')
        booking["booking_time"] = datetime.strftime(booking_datetime, '%H:%M')
        booking["booking_date"] = datetime.strftime(booking_datetime, '%d-%m-%Y')


def init_db():
    print("Initializing the database...")
    conn = None
    cursor = None

    if DATABASE_URL:
        # PostgreSQL-compatible table creation queries
        tables = {
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
            )'''
        }
    else:
        # SQLite-compatible table creation queries
        tables = {
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
            )'''
        }

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

        # (Leave the rest of your init_db code here, e.g., inserting admin data, etc.)
        conn.commit()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
    """Fetch bookings from the API."""
    if session['cleaner_id'] or session['customer_id']:
        if session['cleaner_id']:
            response = requests.get("http://127.0.0.1:5000/bookings/cleaner/" + str(session['cleaner_id']))
        if session['customer_id']:
            response = requests.get("http://127.0.0.1:5000/bookings/customer/" + str(session['customer_id']))
        response.raise_for_status()
        bookings = response.json()
        process_booking_date(bookings)
    else:
        return redirect(url_for("show_cleaners"))
    return render_template('manage_bookings.html', bookings=bookings)


# @app.route("/book/<int:cleaner_id>", methods=["GET", "POST"])
# def book_cleaner(cleaner_id):
#     # Only customers can book a cleaner
#     if "customer_id" not in session:
#         return redirect(url_for("login"))
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     placeholder = "?" if USE_LOCAL_DB else "%s"
#
#     if request.method == "POST":
#         booking_date = request.form.get("booking_date")
#         checklist_items = request.form.get("checklist_items", "")
#
#         # Insert booking row
#         if USE_LOCAL_DB:
#             # SQLite
#             query = f"INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
#             cursor.execute(query, (cleaner_id, session["customer_id"], booking_date, "pending"))
#             booking_id = cursor.lastrowid
#         else:
#             # PostgreSQL
#             query = f"INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}) RETURNING booking_id"
#             cursor.execute(query, (cleaner_id, session["customer_id"], booking_date, "pending"))
#             booking_id = cursor.fetchone()[0]
#
#         # Insert into checklists table referencing the new booking_id
#         query = f"INSERT INTO checklists (booking_id, checklist_items) VALUES ({placeholder}, {placeholder})"
#         cursor.execute(query, (booking_id, checklist_items))
#
#         conn.commit()
#         conn.close()
#
#         # Redirect to show cleaners or a booking confirmation page
#         return redirect(url_for("show_cleaners"))
#
#     # GET request: show booking form
#     conn.close()
#     return render_template("book_cleaner.html", cleaner_id=cleaner_id)

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
    """Fetch a cleaner's information from the API."""
    response = requests.get("http://127.0.0.1:5000/cleaners/" + str(cleaner_id))
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Use conditional placeholder
        placeholder = "?" if USE_LOCAL_DB else "%s"
        query = f"SELECT user_id, username, password FROM users WHERE username = {placeholder}"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[2]  # Stored password hash
            if check_password_hash(stored_hashed_password, password):
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
                else:
                    # If not a cleaner, check if user is a customer
                    cursor.execute(f"SELECT customer_id FROM customers WHERE user_id = {placeholder}", (user[0],))
                    customer_result = cursor.fetchone()
                    if customer_result is not None:
                        session['customer_id'] = customer_result[0]
                        session['cleaner_id'] = False
                    else:
                        # If neither table matches, set both to False
                        session['customer_id'] = False
                        session['cleaner_id'] = False

                conn.close()
                # Redirect to main page (show_cleaners)
                return redirect(url_for('show_cleaners'))
            else:
                conn.close()
                return render_template("login.html", error="Invalid credentials!")
        # No matching username found or other error
        conn.close()
        return render_template("login.html", error="Invalid credentials!")

    # If GET request, just show login form
    return render_template('login.html')


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
    """Logout the user by clearing the session."""
    print("Logging out the user.")  # Debugging print statement
    session.pop("user", None)
    return redirect(url_for("login"))


# Register blueprints
app.register_blueprint(cleaner_bp)  # This is required!

# Run the Flask app in debug mode
if __name__ == "__main__":
    if os.environ.get("FLASK_RUN_MAIN") != "true":  # Prevents duplicate execution
        print(f"🔄 Initializing {'local SQLite' if USE_LOCAL_DB else 'PostgreSQL'} database...")
        init_db()

    print("\n=== Registered Routes ===")
    print(app.url_map)  # Forces Flask to print available routes
    print("========================\n")

    app.run(debug=True)
