"""
Authors: Harrison, Damon, Daniel, Casey
CP3407 EXT GROUP Assignment
This is the main app python file
"""

import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# initialises the Flask app
app = Flask(__name__)
app.secret_key = "CP3407"  # Flask's secure key for session management

# retrieves the database URL from environment variables (used for Render deployment)
DATABASE_URL = os.getenv("DATABASE_URL")

# chooses the appropriate database connection based on the environment
if DATABASE_URL:
    # Production (Render) - uses PostgreSQL
    db_connection = psycopg2.connect(DATABASE_URL)
else:
    # Local environment - uses SQLite
    LOCAL_DB_PATH = "database_files/users.db"  # path to local SQLite database file
    db_connection = sqlite3.connect(LOCAL_DB_PATH)


# initialises the database (creates tables if they do not exist)
def init_db():
    if DATABASE_URL:  # uses PostgreSQL for production
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY, 
                            username TEXT UNIQUE, 
                            password TEXT)''')  # creates the users table with a unique username
        conn.commit()  # commits changes to the database
        conn.close()  # closes the connection to the database
    else:  # uses SQLite for local environment
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            username TEXT UNIQUE, 
                            password TEXT)''')  # creates the users table with a unique username
        conn.commit()  # commits changes to the database
        conn.close()  # closes the connection to the database


# call the init_db function to initialize the database
init_db()


@app.route("/", methods=["GET", "POST"])
def signup():
    # handles the signup form submission (GET for rendering the form, POST for handling the form data)
    if request.method == "POST":
        username = request.form["username"]  # retrieves the username from the form
        password = request.form["password"]  # retrieves the password from the form
        hashed_password = generate_password_hash(password)  # hashes the password before storing it

        if DATABASE_URL:  # uses PostgreSQL for production
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            try:
                # attempts to insert the username and hashed password into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()  # commits the changes
            except psycopg2.IntegrityError:
                # handles the case where the username already exists
                return "Username already exists. Try a different one."
            conn.close()  # closes the connection
        else:  # uses SQLite for local environment
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            try:
                # attempts to insert the username and hashed password into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()  # commits the changes
            except sqlite3.IntegrityError:
                # handles the case where the username already exists
                return "Username already exists. Try a different one."
            conn.close()  # closes the connection

        # redirects to the login page after successful signup
        return redirect(url_for("login"))

    return render_template("signup.html")  # renders the signup page template


@app.route("/login", methods=["GET", "POST"])
def login():
    # handles the login form submission (GET for rendering the form, POST for handling the form data)
    if request.method == "POST":
        username = request.form["username"]  # retrieves the username from the form
        password = request.form["password"]  # retrieves the password from the form

        if DATABASE_URL:  # uses PostgreSQL for production
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            # fetches the stored password hash from the database based on the username
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()  # retrieves the first matching record
            conn.close()  # closes the connection
        else:  # uses SQLite for local environment
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            # fetches the stored password hash from the database based on the username
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()  # retrieves the first matching record
            conn.close()  # closes the connection

        # checks if a matching user was found and if the password hash matches
        if user and check_password_hash(user[0], password):
            session["user"] = username  # stores the username in the session
            return redirect(url_for("dashboard"))  # redirects to the dashboard if login is successful
        else:
            return "Invalid credentials, try again."  # returns an error message if login fails

    return render_template("login.html")  # renders the login page template


@app.route("/dashboard")
def dashboard():
    # checks if the user is logged in by looking for the username in the session
    if "user" in session:
        # returns a welcome message with a logout link if the user is logged in
        return f"Welcome, {session['user']}! <a href='/logout'>Logout</a>"
    return redirect(url_for("login"))  # redirects to the login page if the user is not logged in


@app.route("/logout")
def logout():
    # removes the user from the session to log them out
    session.pop("user", None)
    return redirect(url_for("login"))  # redirects to the login page after logging out


# runs the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
