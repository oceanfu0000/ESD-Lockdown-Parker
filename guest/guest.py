from datetime import datetime
import math
import os
import pytz
from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

# Set up Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create and configure Flask app
app = Flask(__name__)
CORS(app)
Swagger(app)

# Create Blueprint for guest routes
guest_blueprint = Blueprint("guest", __name__)


def error_response(e):
    """Helper to return a JSON error response."""
    return jsonify({"error": str(e)}), 500


def validate_fields(data, required_fields):
    """Helper to check that all required fields exist in the JSON payload."""
    return all(field in data for field in required_fields)


# =========================
# Guest Management Endpoints
# =========================

@guest_blueprint.route('', methods=["POST"])
def create_guest():
    """
    Create a new guest
    ---
    tags:
      - Guest Management
    parameters:
      - in: body
        name: body
        description: Guest object that needs to be added
        required: true
        schema:
          type: object
          required:
            - guest_name
            - guest_email
            - guest_tele
          properties:
            guest_name:
              type: string
              example: John Doe
            guest_email:
              type: string
              example: john.doe@example.com
            guest_tele:
              type: string
              example: "+1234567890"
    responses:
      201:
        description: Guest created successfully
      400:
        description: Missing required fields or creation failed
      500:
        description: Internal server error
    """
    try:
        data = request.json
        required = ["guest_name", "guest_email", "guest_tele"]
        if not validate_fields(data, required):
            return jsonify({"error": "Missing required fields"}), 400

        response = supabase.table("guest").insert({
            "guest_name": data["guest_name"],
            "guest_email": data["guest_email"],
            "guest_tele": data["guest_tele"]
        }).execute()

        if response.data:
            return jsonify({"message": "Guest created successfully"}), 201
        return jsonify({"error": "Failed to create guest"}), 400
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('', methods=["GET"])
def get_all_guests():
    """
    Retrieve all guests
    ---
    tags:
      - Guest Management
    responses:
      200:
        description: List of guests
      404:
        description: No guests found
      500:
        description: Internal server error
    """
    try:
        response = supabase.table("guest").select("*").execute()
        if response.data:
            return jsonify(response.data), 200
        return jsonify({"error": "No guests found"}), 404
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/<int:guest_id>', methods=['GET'])
def get_guest(guest_id):
    """
    Retrieve a specific guest by ID
    ---
    tags:
      - Guest Management
    parameters:
      - name: guest_id
        in: path
        type: integer
        required: true
        description: ID of the guest to retrieve
      - name: field
        in: query
        type: string
        required: false
        description: Specific field to retrieve
    responses:
      200:
        description: Guest details returned successfully
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()
        if not response.data:
            return jsonify({"error": "No guest found"}), 404

        guest = response.data[0]
        field = request.args.get('field')
        if field and field in guest:
            return jsonify({field: guest[field]}), 200
        return jsonify({"guest": guest}), 200
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    """
    Update guest details by ID
    ---
    tags:
      - Guest Management
    parameters:
      - name: guest_id
        in: path
        type: integer
        required: true
        description: ID of the guest to update
      - in: body
        name: body
        description: Guest object with updated details
        required: true
        schema:
          type: object
          required:
            - guest_name
            - guest_email
            - guest_tele
            - wallet
            - otp
            - loyalty_points
            - otp_valid_datetime
            - chat_id
          properties:
            guest_name:
              type: string
              example: Jane Doe
            guest_email:
              type: string
              example: jane.doe@example.com
            guest_tele:
              type: string
              example: "+1234567890"
            wallet:
              type: number
              example: 100
            otp:
              type: string
              example: "123456"
            loyalty_points:
              type: integer
              example: 50
            otp_valid_datetime:
              type: string
              example: "2025-03-19T10:00:00+00:00"
            chat_id:
              type: integer
              example: 12345678
    responses:
      200:
        description: Guest updated successfully
      400:
        description: Missing required fields or update failed
      500:
        description: Internal server error
    """
    try:
        data = request.json
        required = {"guest_name", "guest_email", "guest_tele", "wallet",
                    "otp", "loyalty_points", "otp_valid_datetime", "chat_id"}
        if not required.issubset(data):
            return jsonify({"error": "Missing required fields"}), 400

        otp_valid_datetime = datetime.strptime(
            data["otp_valid_datetime"], "%Y-%m-%dT%H:%M:%S%z"
        ).isoformat()

        response = supabase.table("guest").update({
            "guest_name": data["guest_name"],
            "guest_email": data["guest_email"],
            "guest_tele": data["guest_tele"],
            "wallet": data["wallet"],
            "otp": data["otp"],
            "loyalty_points": data["loyalty_points"],
            "otp_valid_datetime": otp_valid_datetime,
            "chat_id": data["chat_id"]
        }).eq("guest_id", guest_id).execute()

        if response.data:
            return jsonify({"message": "Guest updated successfully"}), 200
        return jsonify({"error": "Failed to update guest"}), 400
    except Exception as e:
        return error_response(e)


@guest_blueprint.route("/<int:guest_id>", methods=["DELETE"])
def delete_guest(guest_id):
    """
    Delete a guest by ID
    ---
    tags:
      - Guest Management
    parameters:
      - name: guest_id
        in: path
        type: integer
        required: true
        description: ID of the guest to delete
    responses:
      200:
        description: Guest deleted successfully
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()
        if response.data:
            delete_response = supabase.table("guest").delete().eq("guest_id", guest_id).execute()
            if delete_response.data:
                return jsonify({"message": "Guest deleted successfully"}), 200
            return jsonify({"error": "Failed to delete guest"}), 400
        return jsonify({"error": "Guest not found"}), 404
    except Exception as e:
        return error_response(e)

@app.route('/login', methods=['POST'])
def login():
    """
    Login a guest using email and password.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        description: Guest login credentials
        required: true
        schema:
          type: object
          required:
            - guest_email
            - password
          properties:
            guest_email:
              type: string
              example: john.doe@example.com
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful, returns guest_id.
      400:
        description: Missing required fields or invalid credentials.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()
        required_fields = ["guest_email", "password"]
        if not validate_fields(data, required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        guest_email = data["guest_email"]
        password = data["password"]

        # Query the guest table for a matching guest_email and password.
        response = supabase.table("guest") \
            .select("*") \
            .eq("guest_email", guest_email) \
            .eq("password", password) \
            .execute()

        if not response.data:
            return jsonify({"error": "Invalid credentials"}), 400

        guest = response.data[0]
        return jsonify({"guest_id": guest.get("guest_id")}), 200

    except Exception as e:
        return error_response(e)

# =========================
# OTP Endpoints
# =========================

@guest_blueprint.route('/validate/<int:otp>', methods=['GET'])
def validate_otp(otp):
    """
    Validate OTP for a guest
    ---
    tags:
      - OTP
    parameters:
      - name: otp
        in: path
        type: integer
        required: true
        description: OTP to validate
    responses:
      200:
        description: OTP validated successfully
      404:
        description: No guest found or OTP expired
      500:
        description: Internal server error
    """
    try:
        response = supabase.table("guest").select("*").eq("otp", otp).execute()
        if not response.data:
            return jsonify({"message": "No guest found"}), 404

        guest = response.data[0]
        otp_valid_datetime = guest.get("otp_valid_datetime")
        if not otp_valid_datetime:
            sg_tz = pytz.timezone('Asia/Singapore')
            today = datetime.now(sg_tz).date()
            end_of_day = sg_tz.localize(datetime(today.year, today.month, today.day, 23, 59, 59, 999999))
            time_iso = end_of_day.isoformat()
            supabase.table("guest").update({"otp_valid_datetime": time_iso}).eq("guest_id", guest["guest_id"]).execute()
            return jsonify({"message": "OTP validated, OTP will be available till end of today."}), 200

        if datetime.fromisoformat(otp_valid_datetime) < datetime.now(pytz.utc):
            return jsonify({"message": "OTP has expired"}), 404
        return jsonify({"guest": guest}), 200
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/isotpunique/<int:otp>', methods=['GET'])
def is_otp_unique(otp):
    """
    Check if an OTP is unique
    ---
    tags:
      - OTP
    parameters:
      - name: otp
        in: path
        type: integer
        required: true
        description: OTP to check for uniqueness
    responses:
      200:
        description: OTP is unique
      404:
        description: OTP already exists
      500:
        description: Internal server error
    """
    try:
        response = supabase.table("guest").select("*").eq("otp", otp).execute()
        if not response.data:
            return jsonify({"message": "OTP is unique"}), 200
        return jsonify({"guest": response.data}), 404
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/update_chat_id_by_otp', methods=['PUT'])
def update_chat_id_by_otp():
    """
    Update a guest's chat ID by OTP
    ---
    tags:
      - OTP
    parameters:
      - in: body
        name: body
        description: JSON object with OTP and new chat ID
        required: true
        schema:
          type: object
          required:
            - otp
            - chat_id
          properties:
            otp:
              type: string
              example: "123456"
            chat_id:
              type: integer
              example: 987654321
    responses:
      200:
        description: Chat ID updated successfully
      400:
        description: Missing required fields or update failed
      404:
        description: Guest not found with provided OTP
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if "otp" not in data or "chat_id" not in data:
            return jsonify({"error": "Missing required fields: otp or chat_id"}), 400

        otp = data["otp"]
        chat_id = data["chat_id"]

        response = supabase.table("guest").select("*").eq("otp", otp).execute()
        if not response.data:
            return jsonify({"error": "Guest not found with the provided OTP"}), 404

        guest = response.data[0]
        guest_id = guest["guest_id"]

        supabase.table("guest").update({"chat_id": None}).eq("chat_id", chat_id).neq("guest_id", guest_id).execute()

        update_response = supabase.table("guest").update({"chat_id": chat_id}).eq("guest_id", guest_id).execute()
        if update_response.data:
            return jsonify({"message": "Chat ID updated successfully"}), 200
        return jsonify({"error": "Failed to update Chat ID"}), 400
    except Exception as e:
        return error_response(e)


# =========================
# Ticket Purchase Endpoints
# =========================

@guest_blueprint.route('/buyticketbyloyalty/<int:id>', methods=['PUT'])
def buy_ticket_by_loyalty(id):
    """
    Buy a ticket using loyalty points
    ---
    tags:
      - Ticket Purchase
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the guest purchasing the ticket
      - in: body
        name: body
        description: JSON object with points to subtract and new OTP
        required: true
        schema:
          type: object
          required:
            - points
            - otp
          properties:
            points:
              type: integer
              example: 50
            otp:
              type: string
              example: "654321"
    responses:
      200:
        description: Ticket bought successfully using loyalty points
      400:
        description: Insufficient loyalty points or missing fields
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if "points" not in data or "otp" not in data:
            return jsonify({"error": "Missing required fields: points or otp"}), 400

        points_to_subtract = data['points']
        new_otp = data['otp']

        response = supabase.table("guest").select("guest_id", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        guest_data = response.data[0]
        current_loyalty_points = guest_data.get('loyalty_points')
        if current_loyalty_points < points_to_subtract:
            return jsonify({"error": "Insufficient loyalty points"}), 400

        new_loyalty_points = current_loyalty_points - points_to_subtract
        update_response = supabase.table("guest").update({
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,
            "otp_valid_datetime": None
        }).eq("guest_id", id).execute()

        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully using loyalty points",
                "new_loyalty_points": new_loyalty_points,
                "updated_otp": new_otp
            }), 200
        return jsonify({"error": "Failed to update guest"}), 500
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/buyticket/<int:id>', methods=['PUT'])
def buy_ticket(id):
    """
    Buy a ticket and update loyalty points after a Stripe purchase
    ---
    tags:
      - Ticket Purchase
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the guest purchasing the ticket
      - in: body
        name: body
        description: JSON object with the amount spent and new OTP
        required: true
        schema:
          type: object
          required:
            - amount
            - otp
          properties:
            amount:
              type: number
              example: 150.75
            otp:
              type: string
              example: "654321"
    responses:
      200:
        description: Ticket bought successfully, loyalty points added.
      400:
        description: Missing required fields
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if "amount" not in data or "otp" not in data:
            return jsonify({"error": "Missing required fields: amount or otp"}), 400

        amount = data['amount']
        new_otp = data['otp']
        points_to_add = math.ceil(amount * 0.10)

        response = supabase.table("guest").select("guest_id", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        guest_data = response.data[0]
        current_loyalty_points = guest_data.get('loyalty_points')
        new_loyalty_points = current_loyalty_points + points_to_add

        update_response = supabase.table("guest").update({
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,
            "otp_valid_datetime": None
        }).eq("guest_id", id).execute()

        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully, loyalty points added.",
                "points_added": points_to_add,
                "updated_otp": new_otp
            }), 200
        return jsonify({"error": "Failed to update guest"}), 500
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/buyticketfromwallet/<int:id>', methods=['PUT'])
def buy_ticket_from_wallet(id):
    """
    Buy a ticket from wallet funds and update loyalty points
    ---
    tags:
      - Ticket Purchase
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the guest purchasing the ticket
      - in: body
        name: body
        description: JSON object with amount and new OTP
        required: true
        schema:
          type: object
          required:
            - amount
            - otp
          properties:
            amount:
              type: number
              example: 10
            otp:
              type: string
              example: "654321"
    responses:
      200:
        description: Ticket bought successfully, wallet updated, loyalty points added.
      400:
        description: Insufficient funds or missing fields
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if "amount" not in data or "otp" not in data:
            return jsonify({"error": "Missing required fields: amount or otp"}), 400

        amount = data['amount']
        new_otp = data['otp']
        points_to_add = math.ceil(amount * 0.10)

        response = supabase.table("guest").select("guest_id", "wallet", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        guest_data = response.data[0]
        current_wallet = guest_data.get('wallet')
        current_loyalty_points = guest_data.get('loyalty_points')
        if current_wallet < amount:
            return jsonify({"error": "Insufficient wallet funds"}), 400

        new_wallet_balance = current_wallet - amount
        new_loyalty_points = current_loyalty_points + points_to_add

        update_response = supabase.table("guest").update({
            "wallet": new_wallet_balance,
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,
            "otp_valid_datetime": None
        }).eq("guest_id", id).execute()

        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully, wallet updated, loyalty points added.",
                "amount_subtracted": amount,
                "loyalty_points_added": points_to_add,
                "updated_otp": new_otp
            }), 200
        return jsonify({"error": "Failed to update guest"}), 500
    except Exception as e:
        return error_response(e)


# =========================
# Wallet Endpoints
# =========================

@guest_blueprint.route('/updatewallet/<int:guest_id>', methods=['PUT'])
def update_wallet(guest_id):
    """
    Update wallet balance (addition or subtraction)
    ---
    tags:
      - Wallet
    parameters:
      - name: guest_id
        in: path
        type: integer
        required: true
        description: ID of the guest whose wallet is updated
      - in: body
        name: body
        description: JSON object with wallet amount (positive or negative)
        required: true
        schema:
          type: object
          required:
            - wallet
          properties:
            wallet:
              type: number
              example: -100
    responses:
      200:
        description: Wallet updated successfully
      400:
        description: Wallet amount cannot be zero or insufficient funds
      404:
        description: Guest not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if "wallet" not in data:
            return jsonify({"error": "Missing wallet field"}), 400

        wallet_amount = data['wallet']
        if wallet_amount == 0:
            return jsonify({"error": "Wallet amount cannot be zero"}), 400

        response = supabase.table("guest").select("wallet").eq("guest_id", guest_id).execute()
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        current_wallet = response.data[0].get('wallet')
        if wallet_amount < 0 and current_wallet < abs(wallet_amount):
            return jsonify({"error": "Insufficient funds"}), 400

        new_wallet = current_wallet + wallet_amount
        update_response = supabase.table("guest").update({"wallet": new_wallet}).eq("guest_id", guest_id).execute()

        if update_response.data:
            return jsonify({"message": "Wallet updated successfully", "wallet": new_wallet}), 200
        return jsonify({"error": "Failed to update wallet"}), 500
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/wallet/<int:chat_id>', methods=['GET'])
def get_wallet_by_chat_id(chat_id):
    """
    Retrieve wallet balance by chat ID
    ---
    tags:
      - Wallet
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: Chat ID of the guest
    responses:
      200:
        description: Wallet balance retrieved successfully
      400:
        description: Missing chat_id field
      404:
        description: No guest found with provided chat_id or wallet not found
      500:
        description: Internal server error
    """
    try:
        if not chat_id:
            return jsonify({"error": "chat_id is required"}), 400

        response = supabase.table("guest").select("*").eq("chat_id", chat_id).execute()
        if not response.data:
            return jsonify({"error": "No guest found with the provided chat_id"}), 404

        guest = response.data[0]
        wallet = guest.get("wallet")
        if wallet is not None:
            return jsonify({"wallet": wallet}), 200
        return jsonify({"error": "Wallet not found for this guest"}), 404
    except Exception as e:
        return error_response(e)


@guest_blueprint.route('/valid_chat_ids', methods=['GET'])
def get_valid_chat_ids():
    """
    Retrieve valid chat IDs for guests with unexpired OTPs
    ---
    tags:
      - OTP
    responses:
      200:
        description: List of valid chat IDs
      404:
        description: No valid OTPs with chat_id found
      500:
        description: Internal server error
    """
    try:
        sg_tz = pytz.timezone('Asia/Singapore')
        current_time = datetime.now(sg_tz)
        response = supabase.table("guest").select("*").execute()

        valid_chat_ids = []
        for guest in response.data:
            otp_valid_datetime = guest.get("otp_valid_datetime")
            if otp_valid_datetime and datetime.fromisoformat(otp_valid_datetime) >= current_time:
                if guest.get("chat_id"):
                    valid_chat_ids.append(guest["chat_id"])

        if valid_chat_ids:
            return jsonify({"chat_ids": valid_chat_ids}), 200
        return jsonify({"message": "No valid OTPs with chat_id found"}), 404
    except Exception as e:
        return error_response(e)


# Register the guest Blueprint with the app
app.register_blueprint(guest_blueprint, url_prefix="/guest")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
