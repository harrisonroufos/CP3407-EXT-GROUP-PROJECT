import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# Initialises the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Flask's secure key for session management

# Retrieves the database URL from environment variables (used for Render deployment)
DATABASE_URL = os.getenv("DATABASE_URL")

# Local database file path
LOCAL_DATABASE = "database_files/MyClean_Database.db"

# Chooses the appropriate database connection based on the environment
if DATABASE_URL:
    # Production (Render) - uses PostgreSQL
    db_connection = psycopg2.connect(DATABASE_URL)
else:
    # Local environment - uses SQLite
    db_connection = sqlite3.connect(LOCAL_DATABASE)


def create_table(cursor, query):
    """Helper function to create a table."""
    print(f"Executing query to create table...")  # Debugging statement
    cursor.execute(query)


def insert_admin_data(cursor):
    """Inserts admin data into the database, ensuring first entries are admin, cleaner, and customer with appropriate attributes."""
    print("Inserting admin data...")

    # Check if the admin, cleaner, and customer users already exist and delete them if they do
    cursor.execute(
        "DELETE FROM bookings WHERE cleaner_id IN (SELECT id FROM users WHERE username IN ('admin', 'cleaner', 'customer'))")
    cursor.execute(
        "DELETE FROM cleaners WHERE user_id IN (SELECT id FROM users WHERE username IN ('admin', 'cleaner', 'customer'))")
    cursor.execute(
        "DELETE FROM customers WHERE user_id IN (SELECT id FROM users WHERE username IN ('admin', 'cleaner', 'customer'))")
    cursor.execute("DELETE FROM users WHERE username IN ('admin', 'cleaner', 'customer')")
    cursor.connection.commit()

    # Insert admin, cleaner, and customer into the 'users' table
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '123'))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('cleaner', '123'))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('customer', '123'))
    cursor.connection.commit()

    # Insert corresponding customer data
    cursor.execute("INSERT INTO customers (user_id, full_name, email, phone_number) VALUES (?, ?, ?, ?)",
                   (1, 'Customer Name', 'customer123@example.com', '1234567891'))

    # Insert corresponding cleaner data
    cursor.execute(
        "INSERT INTO cleaners (user_id, full_name, email, phone_number, rating, experience_years) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 'Cleaner Name', 'cleaner123@example.com', '0987654322', 5.0, 3))

    # Insert dummy booking data with valid cleaner_id and customer_id
    cursor.execute("INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) VALUES (?, ?, ?, ?)",
                   (1, 1, '2025-02-21 09:00:00', 'pending'))

    print("Admin data inserted successfully.")


def clear_tables(cursor):
    """Clears the relevant tables to reset the database."""
    print("Clearing existing data...")

    # Delete all data in the 'bookings', 'cleaners', 'customers', and 'users' tables.
    # This will ensure that we are starting with an empty database.
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM cleaners")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM users")

    # Reset auto-incrementing primary key (for SQLite, use 'DELETE' followed by a reset, for PostgreSQL, use 'TRUNCATE')
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='users'")  # For SQLite: Resets the auto-increment value for users table
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='cleaners'")  # For SQLite: Resets the auto-increment value for cleaners table
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='customers'")  # For SQLite: Resets the auto-increment value for customers table
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='bookings'")  # For SQLite: Resets the auto-increment value for bookings table

    # Commit the changes to ensure they are saved
    cursor.connection.commit()

    print("Tables cleared successfully.")


def init_db():
    """Initialises the database by creating required tables and inserting admin data."""
    print("Initializing database...")

    tables = {
        "users": '''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT UNIQUE NOT NULL, 
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        "customers": '''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
                            full_name TEXT NOT NULL, 
                            email TEXT UNIQUE NOT NULL, 
                            phone_number TEXT UNIQUE NOT NULL,
                            location TEXT, 
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        "cleaners": '''CREATE TABLE IF NOT EXISTS cleaners (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
                            full_name TEXT NOT NULL, 
                            email TEXT UNIQUE NOT NULL, 
                            phone_number TEXT UNIQUE NOT NULL,
                            bio TEXT,
                            location TEXT, 
                            rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
                            experience_years REAL CHECK (experience_years >= 0),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''',
        "bookings": '''CREATE TABLE IF NOT EXISTS bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cleaner_id INTEGER NOT NULL REFERENCES cleaners(id) ON DELETE CASCADE,
                            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                            booking_date TIMESTAMP NOT NULL,
                            status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''
    }

    cursor = db_connection.cursor()

    # Clear all data before initializing the database if there are too many entries
    clear_tables(cursor)

    # Loop through all tables and create them
    for table, query in tables.items():
        print(f"Creating table: {table}")  # Debugging statement
        create_table(cursor, query)

    # Insert dummy admin data after tables are created
    insert_admin_data(cursor)

    # Call the rename_column function to rename 'booking_date' to 'booking_date'
    rename_column(cursor)

    db_connection.commit()  # commits changes to the database
    print("Database initialized, tables created, and admin data inserted.")  # Debugging statement
    cursor.close()  # closes the cursor


def rename_column(cursor):
    """Renames 'booking_date' column to 'booking_date' in 'bookings' table."""
    print("Renaming column...")

    # Step 1: Create a new table with the correct column name
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cleaner_id INTEGER NOT NULL REFERENCES cleaners(id) ON DELETE CASCADE,
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            booking_date TIMESTAMP NOT NULL,  -- Updated column name
            status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Step 2: Copy data from the old table to the new table
    cursor.execute('''
        INSERT INTO bookings_new (id, cleaner_id, customer_id, booking_date, status, created_at)
        SELECT id, cleaner_id, customer_id, booking_date, status, created_at
        FROM bookings
    ''')

    # Step 3: Drop the old bookings table
    cursor.execute('DROP TABLE bookings')

    # Step 4: Rename the new table to 'bookings'
    cursor.execute('ALTER TABLE bookings_new RENAME TO bookings')

    cursor.connection.commit()
    print("Column renamed successfully.")


# Run the database initialization when the app starts
init_db()


@app.route("/homepage", methods=["GET"])
def home():
    # Renders the index.html homepage
    print("Rendering homepage")  # Debugging statement
    return render_template("index.html")


@app.route("/", methods=["GET", "POST"])
def signup():
    # handles the signup form submission (GET for rendering the form, POST for handling the form data)
    if request.method == "POST":
        username = request.form["username"]  # retrieves the username from the form
        password = request.form["password"]  # retrieves the password from the form
        print(f"Received signup request for username: {username}")  # Debugging statement
        hashed_password = generate_password_hash(password)  # hashes the password before storing it

        if DATABASE_URL:  # uses PostgreSQL for production
            print("Using PostgreSQL for signup")
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            try:
                # attempts to insert the username and hashed password into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()  # commits the changes
                print(f"User {username} created successfully in PostgreSQL")  # Debugging statement
            except psycopg2.IntegrityError:
                # handles the case where the username already exists
                print(f"Username {username} already exists in PostgreSQL")  # Debugging statement
                return "Username already exists. Try a different one."
            conn.close()  # closes the connection
        else:  # uses SQLite for local environment
            print("Using SQLite for signup")
            conn = sqlite3.connect(LOCAL_DATABASE)
            cursor = conn.cursor()
            try:
                # attempts to insert the username and hashed password into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()  # commits the changes
                print(f"User {username} created successfully in SQLite")  # Debugging statement
            except sqlite3.IntegrityError:
                # handles the case where the username already exists
                print(f"Username {username} already exists in SQLite")  # Debugging statement
                return "Username already exists. Try a different one."
            conn.close()  # closes the connection

        # redirects to the login page after successful signup
        print(f"Redirecting to login page after signup of {username}")  # Debugging statement
        return redirect(url_for("login"))

    return render_template("signup.html")  # renders the signup page template


@app.route("/login", methods=["GET", "POST"])
def login():
    # handles the login form submission (GET for rendering the form, POST for handling the form data)
    if request.method == "POST":
        username = request.form["username"]  # retrieves the username from the form
        password = request.form["password"]  # retrieves the password from the form
        print(f"Received login attempt for username: {username}")  # Debugging statement

        if DATABASE_URL:  # uses PostgreSQL for production
            print("Using PostgreSQL for login")
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            # fetches the stored password hash from the database based on the username
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()  # retrieves the first matching record
            conn.close()  # closes the connection
        else:  # uses SQLite for local environment
            print("Using SQLite for login")
            conn = sqlite3.connect(LOCAL_DATABASE)
            cursor = conn.cursor()
            # fetches the stored password hash from the database based on the username
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()  # retrieves the first matching record
            conn.close()  # closes the connection

        # checks if a matching user was found and if the password hash matches
        if user and check_password_hash(user[0], password):
            session["user"] = username  # stores the username in the session
            print(f"Login successful for {username}")  # Debugging statement
            return redirect(url_for("home"))  # redirects to the dashboard if login is successful
        else:
            print(f"Login failed for {username}")  # Debugging statement
            return "Invalid credentials, try again."  # returns an error message if login fails

    return render_template("login.html")  # renders the login page template


@app.route("/logout")
def logout():
    # removes the user from the session to log them out
    print(f"Logging out user: {session.get('user', 'unknown')}")  # Debugging statement
    session.pop("user", None)
    return redirect(url_for("login"))  # redirects to the login page after logging out


# runs the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
