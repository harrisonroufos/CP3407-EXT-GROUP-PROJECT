from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from backend.services.cleaner_service import get_all_cleaners, get_cleaner_by_id, get_bookings_by_id
from backend.config import USE_LOCAL_DB

cleaner_bp = Blueprint("cleaners", __name__)


@cleaner_bp.route("/cleaners", methods=["GET"])
def get_cleaners():
    """API endpoint to get all cleaners"""
    cleaners, status_code = get_all_cleaners()
    return jsonify(cleaners), status_code


@cleaner_bp.route("/cleaners/<int:cleaner_id>", methods=["GET"])
def get_cleaner_profile(cleaner_id):
    """API endpoint to fetch a single cleaner's profile."""
    cleaner, status_code = get_cleaner_by_id(cleaner_id)
    return jsonify(cleaner), status_code


@cleaner_bp.route("/bookings/customer/<int:customer_id>", methods=["GET"])
def get_customer_bookings(customer_id):
    """API endpoint to fetch a single customer's bookings."""
    placeholder = "?" if USE_LOCAL_DB else "%s"
    query = f"""
            SELECT b.booking_id, b.cleaner_id, b.booking_date, b.status, c.full_name, c.location
            FROM bookings b
            JOIN cleaners c ON b.cleaner_id = c.cleaner_id
            WHERE b.customer_id = {placeholder}
            """
    bookings, status_code = get_bookings_by_id(customer_id, query)
    return jsonify(bookings), status_code


@cleaner_bp.route("/bookings/cleaner/<int:cleaner_id>", methods=["GET"])
def get_cleaner_bookings(cleaner_id):
    """API endpoint to fetch a single customer's bookings."""
    placeholder = "?" if USE_LOCAL_DB else "%s"
    query = f"""
            SELECT b.booking_id, b.cleaner_id, b.booking_date, b.status, cu.full_name, cl.location
            FROM bookings b
            JOIN customers cu ON b.customer_id = cu.customer_id
            JOIN cleaners cl ON b.cleaner_id = cl.cleaner_id
            WHERE b.cleaner_id = {placeholder}
            """
    bookings, status_code = get_bookings_by_id(cleaner_id, query)
    return jsonify(bookings), status_code
