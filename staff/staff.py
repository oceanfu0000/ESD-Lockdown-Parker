from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from flasgger import Swagger, swag_from

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
Swagger(app)
CORS(app)
staff_blueprint = Blueprint("staff", __name__)

# ------------------------------
# Routes
# ------------------------------

@staff_blueprint.route("", methods=["POST"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Create a new staff member',
    'description': 'This endpoint allows you to create a new staff member by providing the staff name, password, and phone number.',
    'parameters': [
        {
            'name': 'staff_name',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Name of the staff member'
        },
        {
            'name': 'password',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Password for the staff member'
        },
        {
            'name': 'staff_tele',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Phone number of the staff member'
        }
    ],
    'responses': {
        201: {
            'description': 'Staff member created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Staff member created successfully'}
                }
            }
        },
        400: {
            'description': 'Missing required fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required fields'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
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


@staff_blueprint.route("", methods=["GET"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Retrieve all staff members',
    'description': 'This endpoint retrieves all staff members from the system.',
    'responses': {
        200: {
            'description': 'List of all staff members',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'staff_name': {'type': 'string'},
                        'staff_tele': {'type': 'string'}
                    }
                }
            }
        },
        404: {
            'description': 'No staff members found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'No staff members found'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
def read_all_staff():
    try:
        response = supabase.table("staff").select("*").execute()
        return jsonify(response.data), 200 if response.data else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/<int:staff_id>", methods=["GET"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Retrieve a single staff member',
    'description': 'This endpoint retrieves a specific staff member by their ID.',
    'parameters': [
        {
            'name': 'staff_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the staff member'
        }
    ],
    'responses': {
        200: {
            'description': 'Staff member found',
            'schema': {
                'type': 'object',
                'properties': {
                    'staff_name': {'type': 'string'},
                    'staff_tele': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Staff member not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Staff member not found'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
def read_staff(staff_id):
    try:
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()
        if response.data:
            return jsonify(response.data[0]), 200
        return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/<int:staff_id>", methods=["PUT"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Update a staff member',
    'description': 'This endpoint allows you to update staff details such as their name, password, and phone number.',
    'parameters': [
        {
            'name': 'staff_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the staff member'
        },
        {
            'name': 'staff_name',
            'in': 'body',
            'type': 'string',
            'required': False,
            'description': 'New staff name'
        },
        {
            'name': 'password',
            'in': 'body',
            'type': 'string',
            'required': False,
            'description': 'New staff password'
        },
        {
            'name': 'staff_tele',
            'in': 'body',
            'type': 'string',
            'required': False,
            'description': 'New staff phone number'
        }
    ],
    'responses': {
        200: {
            'description': 'Staff member updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Staff member updated successfully'}
                }
            }
        },
        400: {
            'description': 'No valid fields provided for update',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'No valid fields provided for update'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Staff'],
    'summary': 'Delete a staff member',
    'description': 'This endpoint allows you to delete a staff member by their ID.',
    'parameters': [
        {
            'name': 'staff_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the staff member'
        }
    ],
    'responses': {
        200: {
            'description': 'Staff member deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Staff member deleted successfully'}
                }
            }
        },
        404: {
            'description': 'Staff member not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Staff member not found'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
def delete_staff(staff_id):
    try:
        response = supabase.table("staff").delete().eq("staff_id", staff_id).execute()
        if response.data:
            return jsonify({"message": "Staff member deleted successfully"}), 200
        return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@staff_blueprint.route("/validate", methods=["POST"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Validate staff login credentials',
    'description': 'This endpoint validates a staff member\'s credentials by checking their username and password.',
    'parameters': [
        {
            'name': 'staff_name',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'The staff member\'s name'
        },
        {
            'name': 'password',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'The staff member\'s password'
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Login successful'},
                    'Staff': {'type': 'object', 'properties': {'staff_name': {'type': 'string'}}}
                }
            }
        },
        401: {
            'description': 'Invalid password',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Invalid password'}
                }
            }
        },
        403: {
            'description': 'Account locked',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Account locked'},
                    'Staff': {'type': 'object', 'properties': {'staff_name': {'type': 'string'}}}
                }
            }
        },
        404: {
            'description': 'Staff not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Staff not found'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Staff'],
    'summary': 'Update staff chat ID by phone number and password',
    'description': 'This endpoint allows you to update a staff member\'s chat ID by providing their phone number and password.',
    'parameters': [
        {
            'name': 'staff_tele',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Staff member\'s phone number'
        },
        {
            'name': 'password',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Staff member\'s password'
        },
        {
            'name': 'chat_id',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'The new chat ID for the staff member'
        }
    ],
    'responses': {
        200: {
            'description': 'Chat ID updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Chat ID updated successfully'}
                }
            }
        },
        400: {
            'description': 'Missing staff_tele, password, or chat_id',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing staff_tele, password, or chat_id'}
                }
            }
        },
        404: {
            'description': 'Staff not found with provided credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Staff not found with provided credentials'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Staff'],
    'summary': 'Validate staff chat ID',
    'description': 'This endpoint checks if a staff member exists with the provided chat ID.',
    'parameters': [
        {
            'name': 'chat_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Staff member\'s chat ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Valid chat_id found',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Valid chat_id found'}
                }
            }
        },
        404: {
            'description': 'Chat ID not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Chat ID not found'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: <error message>'}
                }
            }
        }
    }
})
def validate_chat_id(chat_id):
    try:
        response = supabase.table("staff").select("*").eq("chat_id", chat_id).execute()
        if response.data:
            return jsonify({"staff": response.data}), 200
        return jsonify({"error": "Chat ID not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route("/reset", methods=["PUT"])
@swag_from({
    'tags': ['Staff'],
    'summary': 'Reset the failed login attempts for a staff member',
    'description': 'This route allows an admin to reset the failed login attempts for a specific staff member identified by their staff_id.',
    'parameters': [
        {
            'name': 'staff_id',
            'in': 'body',
            'required': True,
            'description': 'The unique identifier for the staff member whose failed attempts need to be reset',
            'schema': {
                'type': 'object',
                'properties': {
                    'staff_id': {'type': 'string', 'example': '67890'}
                },
                'required': ['staff_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully reset the failed login attempts for the specified staff member',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': "John Doe's attempts reset to 0"}
                }
            }
        },
        400: {
            'description': 'Bad request, either the staff_id was missing or there was an error in updating the failed attempts',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to update Chat ID'}
                }
            }
        },
        404: {
            'description': 'Staff member with the provided staff_id was not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Staff not found with provided credentials'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Server error: Error details'}
                }
            }
        }
    }
})
def reset_staff_attempt():
    try:
        data = request.json
        staff_id = data.get("staff_id")

        if not staff_id:
            return jsonify({"error": "staff_id is required"}), 400
        
        response = supabase.table("staff").select("*").eq("staff_id", staff_id).execute()
        staff_name = response.data[0]["staff_name"]

        if not response.data:
            return jsonify({"error": "Staff not found with provided credentials"}), 404

        # Attempt to update staff attempts
        update_response = supabase.table("staff").update({"failed_attempts": 0}).eq("staff_id", staff_id).execute()

        if update_response.data:
            return jsonify({"message": f"{staff_name}'s attempts reset to 0"}), 200
        return jsonify({"error": "Failed to update Chat ID"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ------------------------------
# Register Blueprint & Run App
# ------------------------------

app.register_blueprint(staff_blueprint, url_prefix="/staff")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)