import pytest
from app import app
from backend.database import get_db_connection
import json


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test the home page route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Signup" in response.data


def test_booking_creation(client):
    """Test that a booking can be created successfully."""
    response = client.post("/book/1", data={
        'booking_date': '2025-05-01T10:00',
        'checklist_items': 'item1\nitem2'
    })
    assert response.status_code == 302  # Redirect to login page (before payment)
    assert b"/login" in response.headers["Location"].encode()  # Decode Location header properly


def test_database_connection():
    """Test the database connection."""
    conn = get_db_connection()
    assert conn is not None
    conn.close()

# Add more tests as needed
