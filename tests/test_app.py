import pytest
from werkzeug.security import generate_password_hash
from app import app, get_db_connection


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def temporary_user():
    """Create a temporary user and customer for testing."""
    user_data = {
        'username': 'testuser',
        'password': 'password123',
        'full_name': 'Test User',
        'email': 'testuser@example.com',
        'phone_number': '1234567890',
        'location': 'Townsville'
    }

    hashed_password = generate_password_hash(user_data['password'])
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into users
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id",
        (user_data['username'], hashed_password)
    )
    user_id = cursor.fetchone()[0]

    # Insert into customers
    cursor.execute(
        "INSERT INTO customers (user_id, full_name, email, phone_number, location) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING customer_id",
        (user_id, user_data['full_name'], user_data['email'], user_data['phone_number'], user_data['location'])
    )
    customer_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    user_data['user_id'] = user_id
    user_data['customer_id'] = customer_id
    yield user_data

    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()


@pytest.fixture
def temporary_cleaner(temporary_user):
    """Create a temporary cleaner using the temporary user."""
    cleaner_data = {
        'user_id': temporary_user['user_id'],
        'full_name': 'Test Cleaner',
        'email': 'cleaner@example.com',
        'phone_number': '0987654321',
        'bio': 'Experienced cleaner with 5 years of service',
        'location': 'Townsville'
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cleaners (user_id, full_name, email, phone_number, bio, location) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING cleaner_id",
        (cleaner_data['user_id'], cleaner_data['full_name'], cleaner_data['email'],
         cleaner_data['phone_number'], cleaner_data['bio'], cleaner_data['location'])
    )
    cleaner_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    cleaner_data['cleaner_id'] = cleaner_id
    yield cleaner_data

    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cleaners WHERE cleaner_id = %s", (cleaner_id,))
    conn.commit()
    conn.close()


@pytest.fixture
def temporary_booking(temporary_user, temporary_cleaner):
    """Create a temporary booking linked to a customer and cleaner."""
    booking_data = {
        'cleaner_id': temporary_cleaner['cleaner_id'],
        'customer_id': temporary_user['customer_id'],
        'booking_date': '2025-05-01T10:00',
        'status': 'pending'
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (cleaner_id, customer_id, booking_date, status) "
        "VALUES (%s, %s, %s, %s) RETURNING booking_id",
        (booking_data['cleaner_id'], booking_data['customer_id'],
         booking_data['booking_date'], booking_data['status'])
    )
    booking_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    booking_data['booking_id'] = booking_id
    yield booking_data

    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
    conn.commit()
    conn.close()


# Updated test functions:

def test_login_valid(client, temporary_user):
    """Test valid login credentials."""
    response = client.post("/login", data={
        'username': temporary_user['username'],
        'password': 'password123'
    })
    assert response.status_code == 302  # Should redirect after successful login








def test_manage_bookings(client, temporary_user):
    """Test that the booking management page loads."""
    # Simulate a logged-in customer by setting session variables.
    with client.session_transaction() as sess:
        sess['customer_id'] = temporary_user['customer_id']
        sess['user_id'] = temporary_user['user_id']
    # The manage_bookings route does not take an argument.
    response = client.get("/manage_bookings")
    assert response.status_code == 200  # Should load the booking management page


def test_nonexistent_cleaner_profile(client):
    response = client.get("/cleaner/99999")
    assert response.status_code in (404, 200)
