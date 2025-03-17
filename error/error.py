from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime


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

#region Create a Blueprint for error routes
app = Flask(__name__)

CORS(app)

error_blueprint = Blueprint("error", __name__)
#endregion

@error_blueprint.route("/", methods=["POST"])
def log_error():
    try:
        data = request.json
        response = supabase.table("errorlogs").insert({
            "service": data["service"],
            "endpoint": data["endpoint"],
            "error": data["error"],
            "date_time": datetime.now().isoformat()
        }).execute()

        if response.data:
            return jsonify({"message": "Error logged successfully"}),201
        else:
            return jsonify({"error": "Failed to log error"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@error_blueprint.route("/", methods=["GET"])
def get_all_errors():
    try:
        response = supabase.table("errorlogs").select("*").execute()

        if response.data:
            return jsonify(response.data),200
        else:
            return jsonify({"error": "No error log found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register the error Blueprint
app.register_blueprint(error_blueprint, url_prefix="/error")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8079, debug=True)
#endregion