from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Setup Flask app
app = Flask(__name__)
CORS(app)
accesslogs_blueprint = Blueprint("accesslogs", __name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Routes
# ---------------------------

@accesslogs_blueprint.route("/", methods=["POST"])
def create_log():
    try:
        data = request.get_json()
        required_fields = {"staff_id", "type", "message"}

        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields: staff_id, type, message"}), 400

        log_entry = {
            "staff_id": data["staff_id"],
            "type": data["type"],
            "message": data["message"],
            "date_time": datetime.now().isoformat()
        }

        response = supabase.table("accesslogs").insert(log_entry).execute()

        if response.data:
            return jsonify({"message": "Access log created successfully"}), 201
        else:
            return jsonify({"error": "Failed to create access log"}), 400

    except Exception as e:
        logging.exception("Exception occurred while creating access log")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@accesslogs_blueprint.route("/", methods=["GET"])
def read_all_accesslogs():
    try:
        response = supabase.table("accesslogs").select("*").execute()

        if not response.data:
            return jsonify({"error": "No access logs found"}), 404

        return jsonify(response.data), 200

    except Exception as e:
        logging.exception("Exception occurred while fetching all access logs")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@accesslogs_blueprint.route("/<int:staff_id>", methods=["GET"])
def get_accesslogs_by_staff(staff_id):
    try:
        response = supabase.table("accesslogs").select("*").eq("staff_id", staff_id).execute()

        if not response.data:
            return jsonify({"error": f"No access logs found for staff_id {staff_id}"}), 404

        return jsonify({"accesslogs": response.data}), 200

    except Exception as e:
        logging.exception(f"Exception occurred while fetching logs for staff_id {staff_id}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ---------------------------
# Register Blueprint & Start App
# ---------------------------

app.register_blueprint(accesslogs_blueprint, url_prefix="/accesslogs")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)
