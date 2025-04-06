import logging
from flask import Blueprint, Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from

# --------------------------
# Flask App Setup
# --------------------------
app = Flask(__name__)
CORS(app)
Swagger(app)  # Initialize Flasgger for Swagger documentation

# --------------------------
# Blueprint Setup
# --------------------------
testlock_blueprint = Blueprint("testlock", __name__)

# --------------------------
# Routes
# --------------------------
@testlock_blueprint.route("/open", methods=["GET"])
@swag_from({
    'tags': ['Test Lock'],
    'summary': 'Open the test lock',
    'description': 'This endpoint simulates opening the test lock.',
    'responses': {
        200: {
            'description': 'Lock opened successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Lock opened'
                    }
                }
            }
        },
        500: {
            'description': 'Error opening lock',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error opening lock'
                    }
                }
            }
        }
    }
})
def open_lock():
    try:
        print("🔓 Lock Opened")
        return jsonify({"message": "Lock opened"}), 200
    except Exception as e:
        logging.exception("Error opening lock")
        return jsonify({"error": str(e)}), 500

@testlock_blueprint.route("/close", methods=["GET"])
@swag_from({
    'tags': ['Test Lock'],
    'summary': 'Close the test lock',
    'description': 'This endpoint simulates closing the test lock.',
    'responses': {
        200: {
            'description': 'Lock closed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Lock closed'
                    }
                }
            }
        },
        500: {
            'description': 'Error closing lock',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error closing lock'
                    }
                }
            }
        }
    }
})
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
        app.run(host="0.0.0.0", port=8077)
    except Exception as e:
        logging.exception("Flask app failed to start")
