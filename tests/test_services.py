import pytest
from datetime import datetime
from app import process_booking_date


def test_process_booking_date_iso_format():
    """Test that an ISO-format string is correctly processed."""
    bookings = [{"booking_date": "2025-05-01T10:00"}]
    process_booking_date(bookings)
    dt = datetime.fromisoformat("2025-05-01T10:00")
    expected_date = dt.strftime("%d-%m-%Y")
    expected_time = dt.strftime("%H:%M")
    assert bookings[0]["booking_date"] == expected_date
    assert bookings[0]["booking_time"] == expected_time


def test_process_booking_date_datetime_input():
    """Test that a datetime object is processed without modification."""
    dt = datetime(2025, 5, 1, 10, 0)
    bookings = [{"booking_date": dt}]
    process_booking_date(bookings)
    expected_date = dt.strftime("%d-%m-%Y")
    expected_time = dt.strftime("%H:%M")
    assert bookings[0]["booking_date"] == expected_date
    assert bookings[0]["booking_time"] == expected_time


def test_process_booking_date_invalid_input():
    """Test that an invalid date string raises a ValueError."""
    bookings = [{"booking_date": "not a valid date"}]
    with pytest.raises(ValueError):
        process_booking_date(bookings)
