from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
from flasgger import Swagger, swag_from

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
Swagger(app)
CORS(app)
error_blueprint = Blueprint("error", __name__)
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Routes
# -----------------------------

@error_blueprint.route("", methods=["POST"])
@swag_from({
    'tags': ['Error'],
    'summary': 'Log an error into the system',
    'description': 'This endpoint allows you to log an error event, including the service name, endpoint, and error message.',
    'parameters': [
        {
            'name': 'service',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Name of the service where the error occurred'
        },
        {
            'name': 'endpoint',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'The endpoint where the error happened'
        },
        {
            'name': 'error',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Detailed error message or description'
        }
    ],
    'responses': {
        201: {
            'description': 'Error logged successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Error logged successfully'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields: service, endpoint, error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Missing required fields: service, endpoint, error"
                    }
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Server error: <error message>"
                    }
                }
            }
        }
    }
})
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

@error_blueprint.route("", methods=["GET"])
@swag_from({
    'tags': ['Error'],
    'summary': 'Retrieve all error logs',
    'description': 'This endpoint retrieves all error logs stored in the system.',
    'responses': {
        200: {
            'description': 'List of error logs retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'service': {'type': 'string'},
                        'endpoint': {'type': 'string'},
                        'error': {'type': 'string'},
                        'date_time': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        404: {
            'description': 'No error logs found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': "No error logs found"}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Server error: <error message>"
                    }
                }
            }
        }
    }
})
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
    app.run(host='0.0.0.0', port=8078)
