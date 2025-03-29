import logging
from flask import Blueprint, Flask, jsonify
from flask_cors import CORS

# --------------------------
# Flask App Setup
# --------------------------
app = Flask(__name__)
CORS(app)

# --------------------------
# Blueprint Setup
# --------------------------
testlock_blueprint = Blueprint("testlock", __name__)

# --------------------------
# Routes
# --------------------------
@testlock_blueprint.route("/open", methods=["GET"])
def open_lock():
    try:
        print("🔓 Lock Opened")
        return jsonify({"message": "Lock opened"}), 200
    except Exception as e:
        logging.exception("Error opening lock")
        return jsonify({"error": str(e)}), 500

@testlock_blueprint.route("/close", methods=["GET"])
def close_lock():
    try:
        print("🔒 Lock Closed")
        return jsonify({"message": "Lock closed"}), 200
    except Exception as e:
        logging.exception("Error closing lock")
        return jsonify({"error": str(e)}), 500

# --------------------------
# Register Blueprint
# --------------------------
app.register_blueprint(testlock_blueprint, url_prefix="/testlock")

# --------------------------
# Run the App
# --------------------------
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8077, debug=True)
    except Exception as e:
        logging.exception("Flask app failed to start")
