import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CP3407"  # Flask's secure key

# Determine if running locally or on Render by checking the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Use local SQLite database if not using a PostgreSQL URL from the environment
if DATABASE_URL:
    # Production (Render) - use PostgreSQL
    db_connection = psycopg2.connect(DATABASE_URL)
else:
    # Local environment - use SQLite
    LOCAL_DB_PATH = "database_files/users.db"
    db_connection = sqlite3.connect(LOCAL_DB_PATH)

# Database Initialization
def init_db():
    if DATABASE_URL:  # Use PostgreSQL for production
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY, 
                            username TEXT UNIQUE, 
                            password TEXT)''')
        conn.commit()
        conn.close()
    else:  # Use SQLite for local environment
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            username TEXT UNIQUE, 
                            password TEXT)''')
        conn.commit()
        conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        if DATABASE_URL:  # Use PostgreSQL for production
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
            except psycopg2.IntegrityError:
                return "Username already exists. Try a different one."
            conn.close()
        else:  # Use SQLite for local environment
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
            except sqlite3.IntegrityError:
                return "Username already exists. Try a different one."
            conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if DATABASE_URL:  # Use PostgreSQL for production
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()
        else:  # Use SQLite for local environment
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials, try again."

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return f"Welcome, {session['user']}! <a href='/logout'>Logout</a>"
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
