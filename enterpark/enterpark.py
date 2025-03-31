from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import requests
import time
import pika
import sys
import os
import json
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

# Setup for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RabbitMQClient import RabbitMQClient

# -----------------------------
# RabbitMQ Configuration
# -----------------------------
exchange_name = "park_topic"
exchange_type = "topic"

rabbit_client = RabbitMQClient(
    hostname="rabbitmq",
    port=5672,
    exchange_name=exchange_name,
    exchange_type=exchange_type
)

def log_error(service, endpoint, error):
    message = {
        "service": service,
        "endpoint": endpoint,
        "error": str(error)
    }
    rabbit_client.channel.basic_publish(
        exchange=exchange_name,
        routing_key=f"{service}.error",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)
Swagger(app)
enterpark_blueprint = Blueprint("enterpark", __name__)
load_dotenv()

staff_URL = os.getenv('STAFF_URL')
guest_URL = os.getenv('GUEST_URL')
lock_URL = os.getenv('LOCK_URL')  # or use LOCK_URL if Pi connected

# -----------------------------
# Helper: Door Open
# -----------------------------
def open_door():
    try:
        requests.get(lock_URL + "/open")
        time.sleep(3)
        requests.get(lock_URL + "/close")
    except Exception as e:
        log_error("enterpark", "/open_door", e)

# -----------------------------
# Guest Entry Route
# -----------------------------
@enterpark_blueprint.route("/guest/<int:otp>", methods=["GET"])
@swag_from({
    'tags': ['Guest'],
    'parameters': [
        {
            'name': 'otp',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'One-Time Password (OTP) to validate guest entry'
        }
    ],
    'responses': {
        200: {'description': 'Access granted'},
        404: {'description': 'No valid ticket found'},
        503: {'description': 'Guest service unavailable'}
    }
})
def guest_enterpark(otp):
    try:
        response = requests.get(f"{guest_URL}/validate/{otp}")
        if response.status_code == 200:
            open_door()
            return jsonify({"message": "Access granted! Door opening."}), 200
        else:
            return jsonify({
                "message": "No valid ticket found. Please purchase a ticket.",
                "redirect_url": f"{guest_URL}/buy_ticket"
            }), 404
    except requests.exceptions.RequestException as e:
        log_error("enterpark", f"/guest/{otp} (GET)", e)
        return jsonify({"error": "Guest service unavailable. Try again later."}), 503
    except Exception as e:
        log_error("enterpark", f"/guest/{otp} (GET)", e)
        return jsonify({"error": "Unexpected error"}), 500

# -----------------------------
# Staff Entry Route
# -----------------------------
@enterpark_blueprint.route("/staff", methods=["POST"])
@swag_from({
    'tags': ['Staff'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'staff_tele': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['staff_tele', 'password']
            }
        }
    ],
    'responses': {
        200: {'description': 'Access granted'},
        401: {'description': 'Invalid password'},
        403: {'description': 'Account locked'},
        400: {'description': 'Missing request body'},
        503: {'description': 'Staff service unavailable'},
        500: {'description': 'Unexpected error'}
    }
})
def staff_enterpark():
    if not request.json:
        return jsonify({"error": "Missing request body"}), 400

    try:
        response = requests.post(f"{staff_URL}/validate", json=request.json)
        status = response.status_code
        response_data = response.json()

        if status == 200:
            open_door()
            try:
                data = {
                    "staff_id": response_data["Staff"]["staff_id"],
                    "type": "Success",
                    "message": f"Staff member {response_data['Staff']['staff_name']} entered the Park!"
                }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.access",
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
            except Exception as e:
                log_error("enterpark", "/staff (POST) - publish success", e)
                return jsonify({"error": "Staff notification failed"}), 503

        elif status == 401:
            return jsonify({"error": "Invalid password"}), 401

        elif status == 403:
            try:
                data = {
                    "staff_id": response_data["Staff"]["staff_id"],
                    "type": "Failed",
                    "message": f"Staff member {response_data['Staff']['staff_name']} attempted to access the park but failed."
                }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.access",
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
            except Exception as e:
                log_error("enterpark", "/staff (POST) - publish failure", e)

            return jsonify({"error": "Account locked due to failed attempts"}), 403

        else:
            log_error("enterpark", "/staff (POST)", f"Unexpected status code: {status}")
            return jsonify({"error": "Unexpected response from staff service"}), status

        return jsonify(response_data), status

    except requests.exceptions.RequestException as e:
        log_error("enterpark", "/staff (POST)", e)
        return jsonify({"error": "Staff service unavailable"}), 503
    except Exception as e:
        log_error("enterpark", "/staff (POST)", e)
        return jsonify({"error": "Unexpected error"}), 500

# -----------------------------
# Register Blueprint and Run App
# -----------------------------
app.register_blueprint(enterpark_blueprint, url_prefix="/enterpark")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085)
