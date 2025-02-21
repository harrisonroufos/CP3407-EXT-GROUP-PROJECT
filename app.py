"""
Authors: Harrison, Damon, Daniel, Casey
CP3407 EXT GROUP Assignment
This is the main Python/Flask file for the MyClean App
"""

import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# To-do:
# 1. Stop the database from locking itself after a sign-in user already exists
# 2. Show 'pop-up' JavaScript messages to report errors/issues
# 3. Test request information from tables besides 'users'

# Initialise the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Set Flask's secure key for session management

# Retrieve the database URL from environment variables (used for Render deployment)
DATABASE_URL = os.getenv("DATABASE_URL")

# Local database file path
LOCAL_DATABASE = "database_files/MyClean_Database.db"

# Choose the appropriate database connection based on the environment
if DATABASE_URL:
    # Production (Render) - uses PostgreSQL
    db_connection = psycopg2.connect(DATABASE_URL)
else:
    # Local environment - uses SQLite
    db_connection = sqlite3.connect(LOCAL_DATABASE)


def create_table(cursor, query):
    """Create a table using the provided query."""
    print(f"Executing query: {query}")  # Debugging print statement
    cursor.execute(query)


def insert_admin_data(cursor):
    """Insert admin data into the database, ensuring first entries are admin, cleaner, and customer with appropriate attributes."""
    print("Checking if admin data exists...")  # Debugging print statement
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username IN ('admin', 'cleaner', 'customer')")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Inserting admin and initial data...")  # Debugging print statement
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '123'))
        cursor.connection.commit()

        # Insert customer data into the 'customers' table
        cursor.execute("INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (?, ?, ?, ?)",
                       (1, 'Customer Name', 'customer123@example.com', '1234567891'))

        # Insert cleaner data into the 'cleaners' table
        cursor.execute(
            "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (?, ?, ?, ?, ?, ?)",
            (1, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3))

        # Insert dummy booking data with valid cleaner_id and customer_id into the 'bookings' table
        cursor.execute("INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (?, ?, ?, ?)",
                       (1, 1, '2025-02-21 09:00:00', 'pending'))


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
        # Connect to the appropriate database
        conn = psycopg2.connect(DATABASE_URL) if DATABASE_URL else sqlite3.connect(LOCAL_DATABASE)
        cursor = conn.cursor()

        # Clear all data before initializing the database (if required)
        # !!! THIS CANNOT BE ACTIVATED WHEN CREATING THE DATABASE FOR THE FIRST TIME !!!
        # clear_tables(cursor)

        # Check if tables already exist (if not, create them)
        print("Checking if tables already exist...")
        for table in tables.keys():
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';" if not DATABASE_URL else f"SELECT to_regclass('{table}');")
            if cursor.fetchone() is None:
                print(f"Table {table} does not exist. Creating it...")
                create_table(cursor, tables[table])  # Assuming 'create_table' is defined elsewhere
            else:
                print(f"Table {table} already exists.")

        # Insert dummy admin data only if it does not already exist
        print("Inserting admin data...")
        insert_admin_data(cursor)  # Assuming 'insert_admin_data' is defined elsewhere

        # Commit changes and close the connection
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing the database: {e}")
        # JavaScript pop-up error notification on frontend:
        # You can implement this on the frontend for user-facing error handling,
        # for example, by injecting a script to show an alert message
        # alert("Database initialization failed. Please try again.");
    finally:
        cursor.close()
        conn.close()


@app.route("/homepage", methods=["GET"])
def home():
    """Render the homepage view."""
    print("Rendering the homepage.")  # Debugging print statement
    return render_template("index.html")


@app.route("/", methods=["GET", "POST"])
def signup():
    """Handle the user signup process."""
    print("Accessing signup route.")  # Debugging print statement

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        try:
            print(f"Attempting to insert user: {username}")  # Debugging print statement

            if DATABASE_URL:
                # Connect to the PostgreSQL database
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                                   (username, hashed_password))
                    conn.commit()
                except psycopg2.IntegrityError:
                    return render_template("signup.html", error_message="Username already exists. Try a different one.")
                conn.close()
            else:
                # Connect to the SQLite database
                conn = sqlite3.connect(LOCAL_DATABASE)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                    conn.commit()
                except sqlite3.IntegrityError:
                    return render_template("signup.html", error_message="Username already exists. Try a different one.")
                conn.close()

            print("User created successfully.")  # Debugging print statement
            return redirect(url_for("login"))

        except Exception as e:
            print(f"Error: {e}")  # Debugging print statement
            return render_template("signup.html", error_message="An error occurred. Please try again.")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle the user login process."""
    print("Accessing login route.")  # Debugging print statement
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check user credentials against the database
        try:
            print(f"Attempting login for: {username}")  # Debugging print statement
            if DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                conn.close()
            else:
                conn = sqlite3.connect(LOCAL_DATABASE)
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                conn.close()

            # Check if the password matches
            if user and check_password_hash(user[0], password):
                session["user"] = username
                return redirect(url_for("home"))
            else:
                print("Login failed.")  # Debugging print statement
                return render_template("login.html", error_message="Invalid credentials. Try again.")
        except Exception as e:
            print(f"Error: {e}")  # Debugging print statement
            return render_template("login.html", error_message="An error occurred, please try again later.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout the user by clearing the session."""
    print("Logging out the user.")  # Debugging print statement
    session.pop("user", None)
    return redirect(url_for("login"))


# Run the Flask app in debug mode
if __name__ == "__main__":
    init_db()  # Initialise the database before starting the app
    app.run(debug=True)
