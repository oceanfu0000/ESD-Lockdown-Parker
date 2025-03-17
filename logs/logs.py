from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone
import requests

# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)

#region Create a Blueprint for logs routes
app = Flask(__name__)

CORS(app)

logs_blueprint = Blueprint("logs", __name__)
#endregion

#region Error Endpoint
ERROR_MICROSERVICE_URL = "http://127.0.0.1:8079/error"

def log_error(service, endpoint, error):
    error_data = {
        "service": service,
        "endpoint": endpoint,
        "error": error
    }
    try:
        requests.post(ERROR_MICROSERVICE_URL, json=error_data)
    except Exception as e:
        print(f"Failed to log error: {e}")
#endregion

@logs_blueprint.route("/", methods=["POST"])
def create_log():
    try:
        data = request.json
        if "type" in data and "message" in data and "staff_id" in data:
            response = supabase.table("accesslogs").insert({
                "staff_id": data["staff_id"],
                "type": data["type"],
                "message": data["message"],
                "date_time": datetime.now().isoformat()
                }).execute()
            
            if response.data:
                return jsonify({"message": "Record logged!"}), 201
            else:
                return jsonify({"error": "Failed to log!"}), 400
        else:
            return jsonify({"error": "Missing required fields"}), 400
    except Exception as e:
        log_error("logs","/ (POST)", str(e))
        return jsonify({"error": str(e)}), 500

@logs_blueprint.route("/", methods=["GET"])
def read_all_logs():
        try:
            response = supabase.table("accesslogs").select("*").execute()
        
            if response.data:
                return jsonify(response.data), 200
            else:
                return jsonify({"error": "No logs found"}), 404
        except Exception as e:
            log_error("logs","/ (GET)", str(e))
            return jsonify({"error": str(e)}), 500

@logs_blueprint.route("/<int:staff_id>", methods=["GET"])
def get_logs(staff_id):
    try:
        response = supabase.table("accesslogs").select("*").eq("staff_id",staff_id).execute()

        if not response.data:
            return jsonify({"error": "No records found"}),404
        
        return jsonify({"logs": response.data})
    except Exception as e:
        log_error("logs",f"/{staff_id} (GET)", str(e))
        return jsonify({"error": str(e)}),500

# Register the logs Blueprint
app.register_blueprint(logs_blueprint, url_prefix="/logs")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)
#endregion
