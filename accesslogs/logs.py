from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)

#region Create a Blueprint for accesslogs routes
app = Flask(__name__)

CORS(app)

accesslogs_blueprint = Blueprint("accesslogs", __name__)
#endregion

@accesslogs_blueprint.route("/", methods=["POST"])
def create_accesslog():
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
                return jsonify({"message": "Record accesslogged!"}), 201
            else:
                return jsonify({"error": "Failed to accesslog!"}), 400
        else:
            return jsonify({"error": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@accesslogs_blueprint.route("/", methods=["GET"])
def read_all_accesslogs():
        try:
            response = supabase.table("accesslogs").select("*").execute()
        
            if response.data:
                return jsonify(response.data), 200
            else:
                return jsonify({"error": "No accesslogs found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@accesslogs_blueprint.route("/<int:staff_id>", methods=["GET"])
def get_accesslogs(staff_id):
    try:
        response = supabase.table("accesslogs").select("*").eq("staff_id",staff_id).execute()

        if not response.data:
            return jsonify({"error": "No records found"}),404
        
        return jsonify({"accesslogs": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}),500

# Register the accesslogs Blueprint
app.register_blueprint(accesslogs_blueprint, url_prefix="/accesslogs")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)
#endregion
