from datetime import datetime
import math
from flask import Blueprint, Flask, jsonify, request
import pytz
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS
import logging

# -------------------------------
# Setup & Config
# -------------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)
guest_blueprint = Blueprint("guest", __name__)
logging.basicConfig(level=logging.INFO)

# -------------------------------
# Helper: Get Singapore Time
# -------------------------------

def get_singapore_time():
    return datetime.now(pytz.timezone('Asia/Singapore'))

# -------------------------------
# ROUTES
# -------------------------------

@guest_blueprint.route("", methods=["POST"])
def create_guest():
    try:
        data = request.get_json()
        required_fields = {"guest_name", "guest_email", "guest_tele","guest_password",}

        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields"}), 400

        response = supabase.table("guest").insert(data).execute()

        if response.data:
            return jsonify({"message": "Guest created successfully"}), 201
        return jsonify({"error": "Failed to create guest"}), 400
    except Exception as e:
        logging.exception("Failed to create guest")
        return jsonify({"error": "Internal server error"}), 500


@guest_blueprint.route("", methods=["GET"])
def get_all_guests():
    try:
        response = supabase.table("guest").select("*").execute()
        if response.data:
            return jsonify(response.data), 200
        return jsonify({"error": "No guests found"}), 404
    except Exception as e:
        logging.exception("Failed to fetch all guests")
        return jsonify({"error": "Internal server error"}), 500


@guest_blueprint.route("/<int:guest_id>", methods=["GET"])
def get_guest(guest_id):
    try:
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        guest = response.data[0]
        field = request.args.get("field")

        return jsonify({field: guest[field]} if field and field in guest else {"guest": guest}), 200
    except Exception as e:
        logging.exception(f"Failed to fetch guest {guest_id}")
        return jsonify({"error": "Internal server error"}), 500


@guest_blueprint.route("/<int:guest_id>", methods=["PUT"])
def update_guest(guest_id):
    try:
        data = request.get_json()
        required_fields = {
            "guest_name", "guest_email", "guest_tele",
            "wallet", "otp", "loyalty_points", "otp_valid_datetime", "chat_id"
        }

        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            data["otp_valid_datetime"] = datetime.strptime(
                data["otp_valid_datetime"], "%Y-%m-%dT%H:%M:%S%z"
            ).isoformat()
        except ValueError:
            return jsonify({"error": "Invalid datetime format for 'otp_valid_datetime'"}), 400

        response = supabase.table("guest").update(data).eq("guest_id", guest_id).execute()
        if response.data:
            return jsonify({"message": "Guest updated successfully"}), 200
        return jsonify({"error": "Failed to update guest"}), 400

    except Exception as e:
        logging.exception(f"Failed to update guest {guest_id}")
        return jsonify({"error": "Internal server error"}), 500

@guest_blueprint.route("/login", methods=["POST"])
def guest_login():
    try:
        data = request.get_json()
        email = data.get("guest_email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Fetch guest by email
        response = supabase.table("guest").select("*").eq("guest_email", email).execute()

        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        guest = response.data[0]

        # Basic password check (plaintext)
        if guest.get("password") != password:
            return jsonify({"error": "Invalid password"}), 401

        # Return success + guest ID
        return jsonify({
            "message": "Login successful",
            "guest_id": guest["guest_id"]
        }), 200

    except Exception as e:
        logging.exception("Guest login failed")
        return jsonify({"error": "Internal server error"}), 500


# -------------------------------
# Register Blueprint & Run
# -------------------------------

app.register_blueprint(guest_blueprint, url_prefix="/guest")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
