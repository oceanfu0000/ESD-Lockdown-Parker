from datetime import datetime
import math
from flask import Blueprint, Flask, jsonify, request
import pytz
import requests
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flasgger import Swagger

#region Supabase Set Up
# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)
#endregion

#region Create a Blueprint for guest routes
app = Flask(__name__)

CORS(app)

Swagger(app)

guest_blueprint = Blueprint("guest", __name__)
#endregion

# Create new guest
@guest_blueprint.route('/',methods=["POST"])
def create_guest():
        """
    Create a new staff member
    ---
    parameters:
      - name: staff_name
        in: body
        type: string
        required: true
      - name: password
        in: body
        type: string
        required: true
      - name: staff_tele
        in: body
        type: string
        required: true
    responses:
      201:
        description: Staff member created successfully
      400:
        description: Missing required fields or creation failed
    """
        try:
            data = request.json
            if "guest_name" in data and "guest_email" in data and "guest_tele" in data:
                # Insert new staff into the "staff" table in Supabase
                response = supabase.table("guest").insert({
                    "guest_name": data["guest_name"],
                    "guest_email": data["guest_email"],
                    "guest_tele": data["guest_tele"]
                }).execute()

                if response.data:
                    return jsonify({"message": "Guest created successfully"}), 201
                else:
                    return jsonify({"error": "Failed to create guest member"}), 400
            else:
                return jsonify({"error": "Missing required fields"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Read all guests
@guest_blueprint.route('/', methods=["GET"])
def get_all_guests():
    try:
        # Fetch all staff members from the "staff" table in Supabase
        response = supabase.table("guest").select("*").execute()
        
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "No guest found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Read a specific guest member by ID
# If no fields specified, return all
# If field specified (e.g./guest/1?field=loyalty_points), return loyalty_point only
@guest_blueprint.route('/<int:guest_id>', methods=['GET'])
def get_guest(guest_id):
    try:
        # Fetch guest data from Supabase
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()

        # If no data is found, return a 404 error
        if not response.data:
            return jsonify({"error": "No guest found"}), 404
        
        guest = response.data[0]  # Get the first guest

        # Check if the query parameter 'field' is provided to get a specific value
        field = request.args.get('field')

        if field and field in guest:
            # Return the specific field
            return jsonify({field: guest[field]}), 200
        else:
            # Return all guest details
            return jsonify({"guest": guest}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a guest member by ID
# {
#     "guest_name": "John Doe",
#     "guest_email": "john.doe@example.com",
#     "guest_tele": "+123456789",
#     "wallet": "100", 
#     "otp": "123456",
#     "loyalty_points": 100,
#     "otp_valid_datetime": "2025-03-19T10:00:00+00:00"
#     "chat_id": 12345678
# }

@guest_blueprint.route('/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    try:
        data = request.json
        required_fields = {"guest_name", "guest_email", "guest_tele", "wallet", "otp", "loyalty_points", "otp_valid_datetime","chat_id"}
        
        if required_fields.issubset(data):
            # Parse the otp_valid_datetime to datetime object with timezone
            otp_valid_datetime = datetime.strptime(data["otp_valid_datetime"], "%Y-%m-%dT%H:%M:%S%z")
            
            # Update the guest in the "guest" table in Supabase
            response = supabase.table("guest").update({
                "guest_name": data["guest_name"],
                "guest_email": data["guest_email"],
                "guest_tele": data["guest_tele"],
                "wallet": data["wallet"],
                "otp": data["otp"],
                "loyalty_points": data["loyalty_points"],
                "otp_valid_datetime": otp_valid_datetime.isoformat(),
                "chat_id": data["chat_id"]
            }).eq("guest_id", guest_id).execute()

            if response.data:
                return jsonify({"message": "Guest updated successfully"}), 200
            else:
                return jsonify({"error": "Failed to update guest"}), 400
        else:
            return jsonify({"error": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a staff member by ID
@guest_blueprint.route("/<int:guest_id>", methods=["DELETE"])
def delete_staff(guest_id):
    try:
        # Fetch the staff member by staff_id from the "staff" table in Supabase
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()

        if response.data:
            # Delete the staff member in Supabase
            delete_response = supabase.table("guest").delete().eq("guest_id", guest_id).execute()

            if delete_response.data:
                return jsonify({"message": "Guest deleted successfully"}), 200
            else:
                return jsonify({"error": "Failed to delete guest member"}), 400
        else:
            return jsonify({"error": "Guest not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Check OTP in DB
@guest_blueprint.route('/validate/<int:otp>', methods=['GET'])
def validate(otp):
    try:
        response = supabase.table("guest").select("*").eq("otp",otp).execute()
        if not response.data:
            return jsonify({"message": "No Guest Found"}), 404
        
        # guest_data = response.data[0]

        # Check if otp_valid_datetime is still valid if is null is also valid
        otp_valid_datetime = response.data[0].get("otp_valid_datetime")
        if not otp_valid_datetime:
            # Get today's date in Singapore timezone (SGT)
            sg_tz = pytz.timezone('Asia/Singapore')
            today = datetime.now(sg_tz).date()  # Get current date in Singapore Time (SGT)
            
            # Manually create a naive datetime for 23:59:59.999999
            otp_valid_datetime_naive = datetime(
                today.year, today.month, today.day, 23, 59, 59, 999999
            )
            # Localize the naive datetime to the Singapore timezone
            otp_valid_datetime_naive = sg_tz.localize(otp_valid_datetime_naive)
            timeData = otp_valid_datetime_naive.isoformat()
            response = supabase.table("guest").update({"otp_valid_datetime": timeData}).eq("guest_id", response.data[0]["guest_id"]).execute()

            return jsonify({"message": "OTP Validated, OTP will be available till end of today."}), 200

        if datetime.fromisoformat(otp_valid_datetime) < datetime.now(pytz.utc):
            return jsonify({"message": "OTP has expired"}) , 404
        
        return jsonify({"guest": response.data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@guest_blueprint.route('/isotpunique/<int:otp>', methods=['GET'])
def isOtpUnique(otp):
    try:
        response = supabase.table("guest").select("*").eq("otp",otp).execute()

        if not response.data:
            return jsonify({"message": "OTP is Unique"}), 200
        
        return jsonify({"guest": response.data}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# {
#   "points": 100,
#   "otp": "123456"
# }
# Buy Ticket with Loyalty Points
# Get Information from Request Body (points, otp)
@guest_blueprint.route('/buyticketbyloyalty/<int:id>', methods=['PUT'])
def buyticketbyloyalty(id):
    try:
        # Get the request JSON data
        data = request.get_json()

        points_to_subtract = data['points']  # Points to subtract
        new_otp = data['otp']  # OTP to update

        # Query the guest table to get current loyalty points and OTP
        response = supabase.table("guest").select("guest_id", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()
        
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current loyalty points, OTP, and otp_valid_datetime
        guest_data = response.data[0]
        current_loyalty_points = guest_data.get('loyalty_points')

        # Check if there are enough points to subtract
        if current_loyalty_points < points_to_subtract:
            return jsonify({"error": "Insufficient loyalty points"}), 400

        # Calculate the new loyalty points after subtraction
        new_loyalty_points = current_loyalty_points - points_to_subtract

        # Update the guest's loyalty points, OTP, and set otp_valid_datetime to null
        update_response = supabase.table("guest").update({
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,  # Update OTP with the new value
            "otp_valid_datetime": None  # Set otp_valid_datetime to null
        }).eq("guest_id", id).execute()

        # Check if the update was successful
        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully using loyalty points",
                "new_loyalty_points": new_loyalty_points,
                "updated_otp": new_otp
            }), 200
        else:
            return jsonify({"error": "Failed to update loyalty points, OTP, and otp_valid_datetime"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# {
#   "amount": 150.75,
#   "otp": "123456"
# }
#  Update Loyalty Point + OTP after Purchase with Stripe
@guest_blueprint.route('/buyticket/<int:id>', methods=['PUT'])
def buyticket(id):
    try:
        # Get the request JSON data
        data = request.get_json()

        amount = data['amount']  # The amount spent
        points_to_add = math.ceil(amount * 0.10)  # Calculate 10% and round up if necessary
        new_otp = data['otp']  # New OTP to update

        # Query the guest table to get current loyalty points and OTP
        response = supabase.table("guest").select("guest_id", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()

        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current loyalty points
        guest_data = response.data[0]
        current_loyalty_points = guest_data.get('loyalty_points')

        # Calculate the new loyalty points after addition
        new_loyalty_points = current_loyalty_points + points_to_add

        # Update the guest's loyalty points and OTP in the database
        update_response = supabase.table("guest").update({
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,
            "otp_valid_datetime": None  # Set the OTP valid datetime to None
        }).eq("guest_id", id).execute()

        # Check if the update was successful
        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully, loyalty points added.",
                "points_added": points_to_add,
                "updated_otp": new_otp,
            }), 200
        else:
            return jsonify({"error": "Failed to update loyalty points, OTP, or otp_valid_datetime"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# {
#     "amount": 10,
#     "otp": "123456"
# }
#  Update Wallet Balance, Loyalty Point + OTP after Purchase using Wallet
@guest_blueprint.route('/buyticketfromwallet/<int:id>', methods=['PUT'])
def buyticketfromwallet(id):
    try:
        # Get the request JSON data
        data = request.get_json()

        amount = data['amount']  # The amount spent
        new_otp = data['otp']  # New OTP to update

        # Calculate loyalty points to add (e.g., 10% of the amount)
        points_to_add = math.ceil(amount * 0.10)  # Calculate 10% and round up if necessary

        # Query the guest table to get current wallet balance, loyalty points, and OTP
        response = supabase.table("guest").select("guest_id", "wallet", "loyalty_points", "otp", "otp_valid_datetime").eq("guest_id", id).execute()

        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current wallet balance and loyalty points
        guest_data = response.data[0]
        current_wallet = guest_data.get('wallet')
        current_loyalty_points = guest_data.get('loyalty_points')

        # Ensure that there are enough funds in the wallet
        if current_wallet < amount:
            return jsonify({"error": "Insufficient wallet funds"}), 400

        # Subtract the amount from the wallet
        new_wallet_balance = current_wallet - amount

        # Calculate the new loyalty points after addition
        new_loyalty_points = current_loyalty_points + points_to_add

        # Update the guest's wallet, loyalty points, and OTP in the database
        update_response = supabase.table("guest").update({
            "wallet": new_wallet_balance,
            "loyalty_points": new_loyalty_points,
            "otp": new_otp,
            "otp_valid_datetime": None  # Set the OTP valid datetime to None
        }).eq("guest_id", id).execute()

        # Check if the update was successful
        if update_response.data:
            return jsonify({
                "message": "Ticket bought successfully, wallet updated, loyalty points added.",
                "amount_subtracted": amount,
                "loyalty_points_added": points_to_add,
                "updated_otp": new_otp,
            }), 200
        else:
            return jsonify({"error": "Failed to update wallet, loyalty points, OTP, or otp_valid_datetime"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# {
#     "wallet": -100
# }
# Update Wallet Balance (add or minus)
@guest_blueprint.route('/updatewallet/<int:guest_id>', methods = ['PUT'])
def update_wallet(guest_id):
    try:
        # Get the request JSON data
        data = request.get_json()

        wallet_amount = data['wallet']  # The wallet amount to be added or subtracted

        # Ensure wallet_amount is not zero
        if wallet_amount == 0:
            return jsonify({"error": "Wallet amount cannot be zero"}), 400

        # Query the guest table to get the current wallet balance
        response = supabase.table("guest").select("wallet").eq("guest_id", guest_id).execute()

        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current wallet balance
        current_wallet = response.data[0].get('wallet')

        # Ensure that we don't allow subtraction that makes the wallet negative
        if wallet_amount < 0 and current_wallet < abs(wallet_amount):
            return jsonify({"error": "Insufficient funds"}), 400

        new_wallet = current_wallet + wallet_amount  # Subtracting by adding a negative value or adding it

        # Update the guest's wallet in the database
        update_response = supabase.table("guest").update({"wallet": new_wallet}).eq("guest_id", guest_id).execute()

        # Check if the update was successful
        if update_response.data:
            return jsonify({"message": "Wallet updated successfully", "wallet": new_wallet}), 200
        else:
            return jsonify({"error": "Failed to update wallet"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register the guest Blueprint
app.register_blueprint(guest_blueprint, url_prefix="/guest")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
#endregion