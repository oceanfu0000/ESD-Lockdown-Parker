from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests

# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)

#region Create a Blueprint for staff routes
app = Flask(__name__)

CORS(app)

staff_blueprint = Blueprint("staff", __name__)

#endregion

# Create a new staff member
@staff_blueprint.route("/", methods=["POST"])
def create_staff():
    try:
        data = request.json
        if "staff_name" in data and "password" in data and "staff_tele" in data:
            # Insert new staff into the "staff" table in Supabase
            response = supabase.table("staff").insert({
                "staff_name": data["staff_name"],
                "password": data["password"],
                "staff_tele": data["staff_tele"]
            }).execute()

            if response.data:
                return jsonify({"message": "Staff member created successfully"}), 201
            else:
                return jsonify({"error": "Failed to create staff member"}), 400
        else:
            return jsonify({"error": "Missing required fields"}), 400
    except Exception as e:
        log_error("staff","/ (POST)", str(e))
        return jsonify({"error": str(e)}), 500

# Read all staff members
@staff_blueprint.route("/", methods=["GET"])
def read_all_staff():
    try:
        # Fetch all staff members from the "staff" table in Supabase
        response = supabase.table("staff").select("*").execute()
        
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "No staff members found"}), 404
    except Exception as e:
        log_error("staff","/ (GET)", str(e))
        return jsonify({"error": str(e)}), 500

# Read a specific staff member by ID
@staff_blueprint.route("/<int:staff_id>", methods=["GET"])
def read_staff(staff_id):
    try:
        # Fetch the staff member by staff_id from the "staff" table in Supabase
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()
        
        if response.data:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        log_error("staff",f"/{staff_id} (GET)", str(e))
        return jsonify({"error": str(e)}), 500

# Update a staff member by ID
@staff_blueprint.route("/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    try:
        # Fetch the staff member by staff_id from the "staff" table in Supabase
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()

        if response.data:
            data = request.json

            # Prepare the update data
            update_data = {}
            if "staff_name" in data:
                update_data["staff_name"] = data["staff_name"]
            if "password" in data:
                update_data["password"] = data["password"]
            if "staff_tele" in data:
                update_data["staff_tele"] = data["staff_tele"]

            # Update the staff member in Supabase
            update_response = supabase.table("staff").update(update_data).eq("staff_id", staff_id).execute()

            if update_response.data:
                return jsonify({"message": "Staff member updated successfully"}), 200
            else:
                return jsonify({"error": "Failed to update staff member"}), 400
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        log_error("staff",f"/{staff_id} (PUT)", str(e))
        return jsonify({"error": str(e)}), 500

# Check OTP in DB
# If exists, return Guest Id
# If not, return No Guest Found
@staff_blueprint.route('/validate', methods=['POST'])
def validate():
    try:
        # Get the request data
        data = request.json
        staff_name = data["staff_name"]
        password = data["password"]

        # Query Supabase to get the staff by staff_name
        response = supabase.table("staff").select("*").eq("staff_name", staff_name).execute()

        # Check if the staff member exists
        if not response.data:
            return jsonify({"message": "Staff not found"}), 404

        # Get the staff data (assuming only one record is returned)
        staff = response.data[0]

        # Check if the user has exceeded failed attempts limit
        if staff["failed_attempts"] >= 3:
            return jsonify({"message": "Account locked due to too many failed login attempts" , "Staff": staff}), 403

        # Compare the provided password with the stored hashed password
        if staff["password"] == password:
            # Reset failed attempts on successful login
            supabase.table("staff").update({"failed_attempts": 0}).eq("staff_name", staff_name).execute()
            return jsonify({"message": "Login successful!", "Staff": staff}), 200
        else:
            # Increment failed attempts on unsuccessful login
            supabase.table("staff").update({"failed_attempts": staff["failed_attempts"] + 1}).eq("staff_name", staff_name).execute()
            return jsonify({"message": "Invalid password"}), 401

    except Exception as e:
        log_error("staff","/validate (POST)", str(e))
        return jsonify({"error": str(e)}), 500

# Delete a staff member by ID
@staff_blueprint.route("/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    try:
        # Fetch the staff member by staff_id from the "staff" table in Supabase
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()

        if response.data:
            # Delete the staff member in Supabase
            delete_response = supabase.table("staff").delete().eq("staff_id", staff_id).execute()

            if delete_response.data:
                return jsonify({"message": "Staff member deleted successfully"}), 200
            else:
                return jsonify({"error": "Failed to delete staff member"}), 400
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        log_error("staff",f"/{staff_id} (DELETE)", str(e))
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route("/update_chat_id_by_tele_password", methods=["PUT"])
def update_staff_chat_id_by_tele_password():
    try:
        data = request.json

        # Check for required fields: staff_tele, password, and chat_id
        if "staff_tele" not in data or "password" not in data or "chat_id" not in data:
            return jsonify({"error": "Missing required fields: staff_tele, password, or chat_id"}), 400

        staff_tele = data["staff_tele"]
        password = data["password"]
        chat_id = data["chat_id"]

        # Look up the staff member by staff_tele and password
        response = supabase.table("staff").select("*").eq("staff_tele", staff_tele).eq("password", password).execute()

        if response.data:
            # Assuming only one record matches the staff_tele and password
            staff = response.data[0]
            staff_id = staff["staff_id"]  # Get staff_id from the matched record

            # Update chat_id for the staff member with the matched staff_tele and password
            update_response = supabase.table("staff").update({"chat_id": chat_id}).eq("staff_id", staff_id).execute()

            if update_response.data:
                return jsonify({"message": "Staff chat_id updated successfully"}), 200
            else:
                return jsonify({"error": "Failed to update chat_id"}), 400
        else:
            return jsonify({"error": "Staff member not found with the provided staff_tele and password"}), 404

    except Exception as e:
        log_error("staff", "/update_chat_id_by_tele_password (PUT)", str(e))
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route("/validate_chat_id/<int:chat_id>", methods=["GET"])
def validate_chat_id(chat_id):
    try:
        # Look up the staff member by chat_id
        response = supabase.table("staff").select("*").eq("chat_id", chat_id).execute()

        if response.data:
            # If the chat_id exists, return a valid response
            return jsonify({"message": "Valid chat_id found"}), 200
        else:
            # If the chat_id does not exist in the database
            return jsonify({"error": "Chat ID not found"}), 404

    except Exception as e:
        log_error("staff", "/validate_chat_id (GET)", str(e))
        return jsonify({"error": str(e)}), 500


# Register the staff Blueprint
app.register_blueprint(staff_blueprint, url_prefix="/staff")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)
#endregion