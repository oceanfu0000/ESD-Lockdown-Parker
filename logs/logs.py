from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import logging
from flasgger import Swagger, swag_from

# Load environment variables
load_dotenv()

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Setup Flask app
app = Flask(__name__)
Swagger(app)
CORS(app)
logs_blueprint = Blueprint("log", __name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Routes
# ---------------------------

@logs_blueprint.route("", methods=["POST"])
def create_log():
    try:
        data = request.get_json()
        required_fields = {"user_id", "user_type", "action", "type", "message"}

        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields: staff_id, type, message"}), 400

        log_entry = {
            "user_id": data["user_id"],
            "user_type": data["user_type"],
            "action": data["action"],
            "type": data["type"],
            "message": data["message"],
            "date_time": datetime.now().isoformat()
        }

        response = supabase.table("logs").insert(log_entry).execute()

        if response.data:
            return jsonify({"message": "Activity log created successfully"}), 201
        else:
            return jsonify({"error": "Failed to create activity log"}), 400

    except Exception as e:
        logging.exception("Exception occurred while creating activity log")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@logs_blueprint.route("", methods=["GET"])
def read_all_logs():
    try:
        response = supabase.table("logs").select("*").execute()

        if not response.data:
            return jsonify({"error": "No activity logs found"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        logging.exception("Exception occurred while fetching all activity logs")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@logs_blueprint.route("/guest", methods=["GET"])
def read_all_guest():
    try:
        response = supabase.table("logs").select("*").eq("user_type","guest").execute()

        if not response.data:
            return jsonify({"error": "No guest logs found"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@logs_blueprint.route("/staff", methods=["GET"])
def read_all_staff():
    try:
        response = supabase.table("logs").select("*").eq("user_type","staff").execute()

        if not response.data:
            return jsonify({"error": "No staff logs found"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@logs_blueprint.route("/guest/<guest_id>", methods=["GET"])
def read_guest_logs(guest_id):
    try:
        response = supabase.table("logs").select("*").eq("user_type", "guest").eq("user_id", guest_id).execute()

        if not response.data:
            return jsonify({"error": f"No logs found for guest_id {guest_id}"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@logs_blueprint.route("/staff/<staff_id>", methods=["GET"])
def read_staff_logs(staff_id):
    try:
        response = supabase.table("logs").select("*").eq("user_type", "staff").eq("user_id", staff_id).execute()

        if not response.data:
            return jsonify({"error": f"No logs found for staff_id {staff_id}"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ---------------------------
# Register Blueprint & Start App
# ---------------------------

app.register_blueprint(logs_blueprint, url_prefix="/log")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084)
