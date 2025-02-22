from flask import Blueprint, jsonify
from backend.services.cleaner_service import get_all_cleaners

cleaner_bp = Blueprint("cleaners", __name__)


@cleaner_bp.route("/cleaners", methods=["GET"])
def get_cleaners():
    """API endpoint to get all cleaners"""
    cleaners, status_code = get_all_cleaners()
    return jsonify(cleaners), status_code
