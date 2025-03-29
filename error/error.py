from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import os
import logging

# -----------------------------
# Environment Setup
# -----------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)
error_blueprint = Blueprint("error", __name__)
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Routes
# -----------------------------

@error_blueprint.route("/", methods=["POST"])
def log_error():
    try:
        data = request.get_json()

        required_fields = {"service", "endpoint", "error"}
        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields: service, endpoint, error"}), 400

        error_entry = {
            "service": data["service"],
            "endpoint": data["endpoint"],
            "error": data["error"],
            "date_time": datetime.now().isoformat()
        }

        response = supabase.table("errorlogs").insert(error_entry).execute()

        if response.data:
            return jsonify({"message": "Error logged successfully"}), 201
        else:
            logging.warning("Failed to insert error into Supabase")
            return jsonify({"error": "Failed to log error"}), 400

    except Exception as e:
        logging.exception("Unexpected error during error logging")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@error_blueprint.route("/", methods=["GET"])
def get_all_errors():
    try:
        response = supabase.table("errorlogs").select("*").execute()

        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "No error logs found"}), 404

    except Exception as e:
        logging.exception("Unexpected error while retrieving error logs")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# -----------------------------
# Register Blueprint and Start App
# -----------------------------

app.register_blueprint(error_blueprint, url_prefix="/error")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8078, debug=True)
