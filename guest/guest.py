from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv

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

guest_blueprint = Blueprint("guest", __name__)
#endregion

# Create new guest
@guest_blueprint.route('/',methods=["POST"])
def create_guest():
        try:
            data = request.json
            if "guest_name" in data and "guest_email" in data and "guest_tele" in data and "otp" in data:
                # Insert new staff into the "staff" table in Supabase
                response = supabase.table("guest").insert({
                    "guest_name": data["guest_name"],
                    "guest_email": data["guest_email"],
                    "guest_tele": data["guest_tele"],
                    "otp": data["otp"]
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

# Read a specific staff member by ID
# If no fields specified, return all
# If field specified (e.g./guest/1?field=loyalty_points), return loyalty_point only
@guest_blueprint.route('/<int:id>', methods=['GET'])
def get_guest(id):
    try:
        # Fetch guest data from Supabase
        response = supabase.table("guest").select("*").eq("guest_id", id).execute()

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

# Update a staff member by ID
@guest_blueprint.route('/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    try:
        # Fetch the staff member by staff_id from the "staff" table in Supabase
        response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()

        if response.data:
            data = request.json

            # Prepare the update data
            update_data = {}
            if "guest_name" in data:
                update_data["guest_name"] = data["guest_name"]
            if "otp" in data:
                update_data["otp"] = data["otp"]
            if "wallet" in data:
                update_data["wallet"] = data["wallet"]

            # Update the staff member in Supabase
            update_response = supabase.table("guest").update(update_data).eq("guest_id", guest_id).execute()

            if update_response.data:
                return jsonify({"message": "Guest member updated successfully"}), 200
            else:
                return jsonify({"error": "Failed to update staff member"}), 400
        else:
            return jsonify({"error": "Guest member not found"}), 404
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
# If exists, return Guest Id
# If not, return No Guest Found
@guest_blueprint.route('/validate/<int:otp>', methods=['GET'])
def validate(otp):
    try:
        response = supabase.table("guest").select("*").eq("otp",otp).execute()

        if not response.data:
            return jsonify({"message": "No Guest Found"}), 404
        
        return jsonify({"guest": response.data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Loyalty Points to Guest
# Get Information from Request Body (guest_id, points, operation (add, subtract))
@guest_blueprint.route('/updateloyalty', methods = ['PUT'])
def update_loyalty():
    try:
        # Get the request JSON data
        data = request.get_json()

        guest_id = data['guest_id']
        points = data['points']
        operation = data['operation']

        # Query the guest table to get current loyalty points
        response = supabase.table("guest").select("guest_id", "loyalty_points").eq("guest_id", guest_id).execute()
        
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current loyalty points
        current_loyalty_points = response.data[0].get('loyalty_points')

        if current_loyalty_points <= 0 and operation == "subtract":
            return jsonify({"error": "No money bro"}), 404

        # Calculate the new loyalty points based on the operation
        if operation == 'add':
            new_loyalty_points = current_loyalty_points + points
        elif operation == 'subtract':
            new_loyalty_points = current_loyalty_points - points

        # Update the guest's loyalty points in the database
        update_response = supabase.table("guest").update({"loyalty_points": new_loyalty_points}).eq("guest_id", guest_id).execute()

        # Check if the update was successful
        if update_response:
            return jsonify({"message": "Loyalty points updated successfully", "new_loyalty_points": new_loyalty_points}), 200
        else:
            return jsonify({"error": "Failed to update loyalty points"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Loyalty Points to Guest
# Get Information from Request Body (guest_id, points, operation (add, subtract))
@guest_blueprint.route('/updatewallet', methods = ['PUT'])
def update_wallet():
    try:
        # Get the request JSON data
        data = request.get_json()

        guest_id = data['guest_id']
        wallet = data['wallet']
        operation = data['operation']

        # Query the guest table to get current loyalty points
        response = supabase.table("guest").select("guest_id", "wallet").eq("guest_id", guest_id).execute()
        
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current loyalty points
        current_wallet = response.data[0].get('wallet')

        if current_wallet <= 0 and operation == "subtract":
            return jsonify({"error": "No money bro"}), 404

        # Calculate the new loyalty points based on the operation
        if operation == 'add':
            new_wallet = current_wallet + wallet
        elif operation == 'subtract':
            new_wallet = current_wallet - wallet

        # Update the guest's loyalty points in the database
        update_response = supabase.table("guest").update({"wallet": new_wallet}).eq("guest_id", guest_id).execute()

        # Check if the update was successful
        if update_response:
            return jsonify({"message": "Wallet updated successfully", "wallet": new_wallet}), 200
        else:
            return jsonify({"error": "Failed to update loyalty points"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register the guest Blueprint
app.register_blueprint(guest_blueprint, url_prefix="/guest")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
#endregion