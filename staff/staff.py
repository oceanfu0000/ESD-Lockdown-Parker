from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# ------------------------------
# Supabase Setup
# ------------------------------

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ------------------------------
# Flask Setup
# ------------------------------

app = Flask(__name__)
CORS(app)
staff_blueprint = Blueprint("staff", __name__)

# ------------------------------
# Routes
# ------------------------------

@staff_blueprint.route("/", methods=["POST"])
def create_staff():
    try:
        data = request.json
        required = {"staff_name", "password", "staff_tele"}
        if not data or not required.issubset(data):
            return jsonify({"error": "Missing required fields"}), 400

        response = supabase.table("staff").insert({
            "staff_name": data["staff_name"],
            "password": data["password"],
            "staff_tele": data["staff_tele"]
        }).execute()

        if response.data:
            return jsonify({"message": "Staff member created successfully"}), 201
        return jsonify({"error": "Failed to create staff member"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/", methods=["GET"])
def read_all_staff():
    try:
        response = supabase.table("staff").select("*").execute()
        return jsonify(response.data), 200 if response.data else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/<int:staff_id>", methods=["GET"])
def read_staff(staff_id):
    try:
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()
        if response.data:
            return jsonify(response.data[0]), 200
        return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    try:
        data = request.json
        update_data = {k: v for k, v in data.items() if k in ["staff_name", "password", "staff_tele"]}

        if not update_data:
            return jsonify({"error": "No valid fields provided for update"}), 400

        response = supabase.table("staff").update(update_data).eq("staff_id", staff_id).execute()
        if response.data:
            return jsonify({"message": "Staff member updated successfully"}), 200
        return jsonify({"error": "Failed to update staff member"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    try:
        response = supabase.table("staff").delete().eq("staff_id", staff_id).execute()
        if response.data:
            return jsonify({"message": "Staff member deleted successfully"}), 200
        return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/validate", methods=["POST"])
def validate():
    try:
        data = request.json
        if not data or "staff_name" not in data or "password" not in data:
            return jsonify({"error": "Missing staff_name or password"}), 400

        response = supabase.table("staff").select("*").eq("staff_name", data["staff_name"]).execute()
        if not response.data:
            return jsonify({"message": "Staff not found"}), 404

        staff = response.data[0]

        if staff.get("failed_attempts", 0) >= 3:
            return jsonify({"message": "Account locked", "Staff": staff}), 403

        if staff["password"] == data["password"]:
            supabase.table("staff").update({"failed_attempts": 0}).eq("staff_name", data["staff_name"]).execute()
            return jsonify({"message": "Login successful", "Staff": staff}), 200
        else:
            supabase.table("staff").update({
                "failed_attempts": staff["failed_attempts"] + 1
            }).eq("staff_name", data["staff_name"]).execute()
            return jsonify({"message": "Invalid password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/update_chat_id_by_tele_password", methods=["PUT"])
def update_staff_chat_id_by_tele_password():
    try:
        data = request.json
        if not all(k in data for k in ("staff_tele", "password", "chat_id")):
            return jsonify({"error": "Missing staff_tele, password, or chat_id"}), 400

        response = supabase.table("staff").select("*").eq("staff_tele", data["staff_tele"]).eq("password", data["password"]).execute()
        if not response.data:
            return jsonify({"error": "Staff not found with provided credentials"}), 404

        staff_id = response.data[0]["staff_id"]
        update_response = supabase.table("staff").update({"chat_id": data["chat_id"]}).eq("staff_id", staff_id).execute()

        if update_response.data:
            return jsonify({"message": "Chat ID updated successfully"}), 200
        return jsonify({"error": "Failed to update Chat ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/validate_chat_id/<int:chat_id>", methods=["GET"])
def validate_chat_id(chat_id):
    try:
        response = supabase.table("staff").select("*").eq("chat_id", chat_id).execute()
        if response.data:
            return jsonify({"message": "Valid chat_id found"}), 200
        return jsonify({"error": "Chat ID not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------
# Register Blueprint & Run App
# ------------------------------

app.register_blueprint(staff_blueprint, url_prefix="/staff")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)