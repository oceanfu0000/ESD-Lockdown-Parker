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
accesslogs_blueprint = Blueprint("accesslogs", __name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Routes
# ---------------------------

@accesslogs_blueprint.route("", methods=["POST"])
@swag_from({
    'tags': ['Logs'],
    'summary': 'Create an access log entry',
    'description': 'This endpoint creates a new access log entry with staff_id, type, and message.',
    'parameters': [
        {
            'name': 'log_entry',
            'in': 'body',
            'required': True,
            'description': 'The log entry to be created',
            'schema': {
                'type': 'object',
                'required': ['staff_id', 'type', 'message'],
                'properties': {
                    'staff_id': {
                        'type': 'string',
                        'description': 'ID of the staff member who entered'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'Type of the log entry (e.g., info, error)'
                    },
                    'message': {
                        'type': 'string',
                        'description': 'Message of the log entry'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Access log created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Access log created successfully'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields or failed to create log',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Missing required fields: staff_id, type, message'
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
                        'example': 'Server error: <error message>'
                    }
                }
            }
        }
    }
})
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

@accesslogs_blueprint.route("", methods=["GET"])
@swag_from({
    'tags': ['Logs'],
    'summary': 'Fetch all access log entries',
    'description': 'This endpoint fetches all access log entries from the database.',
    'responses': {
        200: {
            'description': 'Successfully retrieved all access logs',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'staff_id': {
                            'type': 'string',
                            'description': 'ID of the staff member who entered'
                        },
                        'type': {
                            'type': 'string',
                            'description': 'Type of log entry (e.g., Success, Failure)'
                        },
                        'message': {
                            'type': 'string',
                            'description': 'Message of the log entry'
                        },
                        'date_time': {
                            'type': 'string',
                            'description': 'Date and time when the log entry was created',
                            'example': '2025-03-31T12:00:00'
                        }
                    }
                }
            }
        },
        404: {
            'description': 'No access logs found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'No access logs found'
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
                        'example': 'Server error: <error message>'
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Logs'],
    'summary': 'Fetch access logs for a specific staff member',
    'description': 'This endpoint fetches all access log entries for a given staff member based on their staff_id.',
    'parameters': [
        {
            'name': 'staff_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the staff member to fetch access logs for'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully retrieved access logs for the specified staff member',
            'schema': {
                'type': 'object',
                'properties': {
                    'accesslogs': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'staff_id': {
                                    'type': 'string',
                                    'description': 'ID of the staff member who created the log entry'
                                },
                                'type': {
                                    'type': 'string',
                                    'description': 'Type of log entry (e.g., info, error)'
                                },
                                'message': {
                                    'type': 'string',
                                    'description': 'Message of the log entry'
                                },
                                'date_time': {
                                    'type': 'string',
                                    'description': 'Date and time when the log entry was created',
                                    'example': '2025-03-31T12:00:00'
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'No access logs found for the given staff_id',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'No access logs found for staff_id 123'
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
                        'example': 'Server error: <error message>'
                    }
                }
            }
        }
    }
})
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
    app.run(host='0.0.0.0', port=8084)
