"""
Authors: Harrison, Damon, Daniel, Casey
CP3407 EXT GROUP Assignment
This is the main Python/Flask file for the MyClean App
"""

import os, sqlite3, psycopg2, requests
from backend.routes.cleaner_routes import cleaner_bp
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import DATABASE_URL  # Import DATABASE_URL from config.py

# Initialise the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Set Flask's secure key for session management

# Retrieve the database URL from environment variables (used for Render deployment)
from backend.config import DATABASE_URL

# Local database file path
LOCAL_DATABASE = "database_files/MyClean_Database.db"


# Function to get the database connection based on environment
def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect(LOCAL_DATABASE)


def create_table(cursor, query):
    """Create a table using the provided query."""
    print(f"Executing query: {query}")  # Debugging print statement
    cursor.execute(query)


def insert_admin_data(cursor, db_type="sqlite"):
    """Insert admin data into the database, ensuring first entries are admin, cleaner, and customer with appropriate attributes."""
    print("Checking if admin data exists...")  # Debugging print statement
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username IN ('admin', 'cleaner', 'customer')"
    )
    count = cursor.fetchone()[0]

    if count == 0:
        print("Inserting admin and initial data...")  # Debugging print statement

        # Insert admin user into the 'users' table
        if db_type == "postgres":
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', '123'))
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '123'))

        # Get the user_id for the admin
        user_id = cursor.lastrowid  # Works in SQLite for getting the last inserted ID
        if db_type == "postgres":
            cursor.execute("SELECT CURRVAL(pg_get_serial_sequence('users', 'user_id'))")
            user_id = cursor.fetchone()[0]

        # Insert customer data into the 'customers' table
        if db_type == "postgres":
            cursor.execute("INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (%s, %s, %s, %s)",
                           (user_id, 'Customer Name', 'customer123@example.com', '1234567891'))
        else:
            cursor.execute("INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (?, ?, ?, ?)",
                           (user_id, 'Customer Name', 'customer123@example.com', '1234567891'))

        # Insert cleaner data into the 'cleaners' table
        if db_type == "postgres":
            cursor.execute(
                "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3))
        else:
            cursor.execute(
                "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3))

        # Insert dummy booking data with valid cleaner_id and customer_id into the 'bookings' table
        cursor.execute("INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (?, ?, ?, ?)"
                       if db_type == "sqlite" else
                       "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (%s, %s, %s, %s)",
                       (user_id, user_id, '2025-02-21 09:00:00', 'pending'))

        # Commit changes
        if db_type == "postgres":
            cursor.connection.commit()
        else:
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


def init_db():
    """Initialise the database by creating required tables and inserting admin data if not already present."""
    print("Initializing the database...")  # Debugging print statement

    # Choose table creation queries based on database type
    if DATABASE_URL:
        # PostgreSQL-compatible table creation queries
        tables = {
            "users": '''CREATE TABLE IF NOT EXISTS users (
                                user_id SERIAL PRIMARY KEY, 
                                username TEXT UNIQUE NOT NULL, 
                                password TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
            "customers": '''CREATE TABLE IF NOT EXISTS customers (
                                    customer_id SERIAL PRIMARY KEY,
                                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                                    full_name TEXT NOT NULL, 
                                    email TEXT UNIQUE NOT NULL, 
                                    phone_number TEXT UNIQUE NOT NULL,
                                    location TEXT, 
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
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
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
            "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
                                    booking_id SERIAL PRIMARY KEY,
                                    cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
                                    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                                    booking_date TIMESTAMP NOT NULL,
                                    status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''
        }
    else:
        # SQLite-compatible table creation queries
        tables = {
            "users": '''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                username TEXT UNIQUE NOT NULL, 
                                password TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
            "customers": '''CREATE TABLE IF NOT EXISTS customers (
                                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
                                    full_name TEXT NOT NULL, 
                                    email TEXT UNIQUE NOT NULL, 
                                    phone_number TEXT UNIQUE NOT NULL,
                                    location TEXT, 
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
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
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
            "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
                                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    cleaner_id INTEGER NOT NULL REFERENCES cleaners(cleaner_id) ON DELETE CASCADE,
                                    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
                                    booking_date TIMESTAMP NOT NULL,
                                    status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''
        }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if tables already exist (if not, create them)
        print("Checking if tables already exist...")
        for table, query in tables.items():
            cursor.execute(
                f"SELECT to_regclass('{table}');" if DATABASE_URL else f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if cursor.fetchone() is None:
                print(f"Table {table} does not exist. Creating it...")
                create_table(cursor, query)  # Create the table
            else:
                print(f"Table {table} already exists.")

        # Insert dummy admin data only if it does not already exist
        print("Inserting admin data...")
        insert_admin_data(cursor)  # Ensure admin data is inserted

        # Commit changes and close the connection
        conn.commit()
        print("Database initialized successfully.")

    except Exception as e:
        print(f"Error initializing the database: {e}")
    finally:
        cursor.close()
        conn.close()


@app.route("/show_cleaners", methods=["GET"])
def show_cleaners():
    """Fetch cleaners from the API."""
    response = requests.get("http://127.0.0.1:5000/cleaners")
    cleaners = response.json()  # Convert JSON to Python list
    return render_template('index.html', cleaners=cleaners)


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

        cursor.execute(
            "UPDATE cleaners SET full_name = %s, email = %s, phone_number = %s, location = %s, bio = %s, experience_years = %s WHERE cleaner_id = %s",
            (full_name, email, phone_number, location, bio, experience_years, session['cleaner_id']))

        cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (username, session['user_id']))
        session['username'] = username

        conn.commit()
        conn.close()

        return redirect(url_for('show_cleaners'))

    if session['customer_id'] and request.method == "GET":
        return redirect(url_for('show_cleaners'))

    return render_template('edit_profile.html')


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

        cursor.execute(
            "UPDATE customers SET full_name = %s, email = %s, phone_number = %s, location = %s WHERE customer_id = %s",
            (full_name, email, phone_number, location, session['customer_id']))

        cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (username, session['user_id']))

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

        # Retrieve the user from the database
        cursor.execute("SELECT user_id, username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[2]  # Get stored password
            if check_password_hash(stored_hashed_password, password):  # Verify password
                session['user_id'] = user[0]  # Store user ID in session
                session['username'] = user[1]  # Store username in session

                try:  # This is incredibly messy but I promise it works
                    cursor.execute("SELECT cleaner_id FROM cleaners WHERE user_id = %s", (user[0],))
                    session['cleaner_id'] = cursor.fetchone()[0]
                    session['customer_id'] = False
                except TypeError:
                    try:
                        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (user[0],))
                        session['customer_id'] = cursor.fetchone()[0]
                        session['cleaner_id'] = False
                    except TypeError:
                        session['cleaner_id'] = False
                        session['customer_id'] = False
                return redirect(url_for('show_cleaners'))  # Redirect to main page
            else:
                return render_template("login.html", error="Invalid credentials!")
        conn.close()
        return render_template("login.html", error="Invalid credentials!")

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

        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        # Check if email already exists in either customers or cleaners
        cursor.execute("SELECT email FROM customers WHERE email = %s UNION SELECT email FROM cleaners WHERE email = %s",
                       (email, email))
        existing_email = cursor.fetchone()

        # Check if phone number already exists in either customers or cleaners
        cursor.execute(
            "SELECT phone_number FROM customers WHERE phone_number = %s UNION SELECT phone_number FROM cleaners WHERE phone_number = %s",
            (phone_number, phone_number))
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
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id",
            (username, hashed_password)
        )
        user_id = cursor.fetchone()[0]

        # Insert into either customers or cleaners table
        if user_type == 'customer':
            cursor.execute(
                "INSERT INTO customers (user_id, full_name, email, phone_number, location) VALUES (%s, %s, %s, %s, %s)",
                (user_id, full_name, email, phone_number, location))
        else:
            cursor.execute(
                "INSERT INTO cleaners (user_id, full_name, email, phone_number, location, experience_years) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, full_name, email, phone_number, location, experience_years))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))  # Redirect to login page after signup

    return render_template('signup.html')


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
        init_db()

    print("\n=== Registered Routes ===")
    print(app.url_map)  # Forces Flask to print available routes
    print("========================\n")

    app.run(debug=True)
