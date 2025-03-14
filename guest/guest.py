from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)

#region Create a Blueprint for guest routes
app = Flask(__name__)

CORS(app)

guest_blueprint = Blueprint("guest", __name__)

#endregion

# Check OTP in DB
# If exists, return Guest Details
# If not, return No Guest Found
@guest_blueprint.route('/validate/<int:otp>', methods=['GET'])
def validate(otp):
    try:
        response = supabase.table("guest").select("*").eq("otp",otp).execute()

        if not response.data:
            return jsonify({"error": "no guest found"}),500
        
        return jsonify({"guest": response.data}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Check Guest Details using guest_id
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
        
# Register the guest Blueprint
app.register_blueprint(guest_blueprint, url_prefix="/guest")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
#endregion