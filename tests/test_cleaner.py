import pytest
from werkzeug.security import generate_password_hash
from app import app, get_db_connection


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_cleaner_profile(client, temporary_cleaner):
    """Test that the cleaner profile page loads correctly."""
    response = client.get(f"/cleaner/{temporary_cleaner['cleaner_id']}")
    assert response.status_code == 200
    # Check for the cleaner's full name as rendered on the page
    assert b"Test Cleaner" in response.data


def test_edit_cleaner_profile(client, temporary_cleaner):
    """Test updating cleaner profile."""
    # Simulate a logged-in cleaner by setting session variables.
    with client.session_transaction() as sess:
        sess['cleaner_id'] = temporary_cleaner['cleaner_id']
        sess['user_id'] = temporary_cleaner['user_id']
    # Use the correct route URL for editing a cleaner profile.
    response = client.post(f"/cleaner/{temporary_cleaner['cleaner_id']}/edit", data={
        'username': 'new_cleaner_username',
        'full_name': 'Updated Name',
        'email': 'updated_cleaner@example.com',
        'phone_number': '1112223333',
        'location': 'Updated Town',
        'bio': 'Updated cleaner with more experience',
        'experience_years': 6
    })
    assert response.status_code == 302  # Should redirect after updating
