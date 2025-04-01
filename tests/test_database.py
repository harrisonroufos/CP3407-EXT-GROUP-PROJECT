import pytest
from app import get_db_connection, get_table_definitions, init_db


def test_db_connection():
    """Test that a database connection can be established."""
    conn = get_db_connection()
    assert conn is not None, "Failed to get a database connection."
    conn.close()


def test_tables_exist():
    """Test that all expected tables exist in the database after initialization."""
    # Initialize the database so tables are created.
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    tables = get_table_definitions()
    for table in tables.keys():
        try:
            cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
        except Exception as e:
            pytest.fail(f"Table '{table}' does not exist or is inaccessible: {e}")
    conn.close()


def test_admin_data_exists():
    """Test that admin data is inserted during initialization."""
    # Ensure tables and admin data are initialized.
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    # For simplicity, we check for a user with username 'admin'
    cursor.execute("SELECT username FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    assert admin is not None, "Admin data not inserted."
    conn.close()
