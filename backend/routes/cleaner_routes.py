from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from backend.services.cleaner_service import get_all_cleaners, get_cleaner_by_id, get_bookings_by_id

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


@cleaner_bp.route("/bookings/<int:customer_id>", methods=["GET"])
def get_customer_bookings(customer_id):
    """API endpoint to fetch a single customer's bookings."""
    bookings, status_code = get_bookings_by_id(customer_id)
    return jsonify(bookings), status_code
