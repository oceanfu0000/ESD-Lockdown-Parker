import json
import os
import sys
import pika
import requests
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
from flasgger import Swagger, swag_from
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from RabbitMQClient import RabbitMQClient
from invokes import invoke_http

# Load env
load_dotenv()

# Flask App Setup
app = Flask(__name__)
CORS(app)
Swagger(app)

payment_blueprint = Blueprint("makepayment", __name__)

# RabbitMQ Configuration
exchange_name = "park_topic"
exchange_type = "topic"
rabbit_client = RabbitMQClient(
    hostname="rabbitmq",
    port=5672,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

# Service URLs from env
staff_URL = os.getenv("STAFF_URL")
guest_URL = os.getenv("GUEST_URL")
error_URL = os.getenv("ERROR_URL")
stripe_URL = os.getenv("STRIPE_URL")
otp_URL = os.getenv("OTP_URL")


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


def validate_otp(otp):
    try:
        otp_response = invoke_http(f"{guest_URL}/isotpunique/{otp}", method="GET")
        return otp_response.get("code", 200) == 200
    except Exception:
        return False


# -----------------------------
# Buy Ticket (Stripe)
# -----------------------------
@payment_blueprint.route("/buyticket", methods=["POST"])
@swag_from({
    'tags': ['Payment'],
    'summary': 'Buy ticket using Stripe',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'charge': {'type': 'object'},
                'guest_id': {'type': 'integer'}
            },
            'required': ['charge', 'guest_id']
        }
    }],
    'responses': {
        200: {'description': 'Ticket purchased successfully'},
        400: {'description': 'Payment processing failed'},
        503: {'description': 'Guest service unavailable'}
    }
})
def buyticket():
    try:
        data = request.get_json()
        charge = data["charge"]
        # otp = data["otp"]
        guest_id = data["guest_id"]
        response = invoke_http(f"{stripe_URL}/charges", method="POST", json=charge)
        if response.get("code", 200) == 200:
            otp = None
            while True:
                otp = invoke_http(f"{otp_URL}", method="GET")
                if validate_otp(otp):
                    break

            invoke_http(f"{guest_URL}/buyticket/{guest_id}", method="PUT", json={"otp": otp,"amount": charge["amount"]})

            rabbit_client.channel.basic_publish(
                exchange=exchange_name,
                routing_key="payment.notification",
                body=json.dumps({"guest_id": guest_id}),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            return jsonify({"message": "Payment successful! Ticket purchased."}), 200

        return jsonify({"error": "Stripe payment failed"}), 400

    except Exception as e:
        log_error("payment_service", "/buyticket", e)
        return jsonify({"error": "Payment processing failed."}), 400


# -----------------------------
# Buy Ticket (Loyalty)
# -----------------------------
@payment_blueprint.route("/buyticketbyloyalty", methods=["POST"])
@swag_from({
    'tags': ['Payment'],
    'summary': 'Buy ticket using loyalty points',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'charge': {'type': 'object'},
                'guest_id': {'type': 'integer'}
            },
            'required': ['charge', 'guest_id']
        }
    }],
    'responses': {
        200: {'description': 'Ticket purchased successfully'},
        400: {'description': 'Payment processing failed'},
        503: {'description': 'Guest service unavailable'}
    }
})
def buyticketbyloyalty():
    try:
        data = request.get_json()
        charge = data["charge"]
        # otp = data["otp"]
        points = data["charge"]["amount"]
        guest_id = data["guest_id"]

        response = invoke_http(f"{stripe_URL}/charges", method="POST", json=charge)
        if response.get("code", 200) == 200:
            otp = None
            while True:
                otp = invoke_http(f"{otp_URL}", method="GET")
                if validate_otp(otp):
                    break

            invoke_http(
                f"{guest_URL}/buyticketbyloyalty/{guest_id}",
                method="PUT",
                json={"otp": otp, "points": points}
            )

            rabbit_client.channel.basic_publish(
                exchange=exchange_name,
                routing_key="payment.notification",
                body=json.dumps({"guest_id": guest_id}),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            return jsonify({"message": "Payment successful! Ticket purchased."}), 200

        return jsonify({"error": "Stripe payment failed"}), 400

    except Exception as e:
        log_error("payment_service", "/buyticketbyloyalty", e)
        return jsonify({"error": "Payment processing failed."}), 400


# -----------------------------
# Buy Ticket (Wallet)
# -----------------------------
@payment_blueprint.route("/buyticketbywallet", methods=["POST"])
@swag_from({
    'tags': ['Payment'],
    'summary': 'Buy ticket using wallet balance',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'charge': {'type': 'object'},
                'guest_id': {'type': 'integer'}
            },
            'required': ['charge', 'guest_id']
        }
    }],
    'responses': {
        200: {'description': 'Ticket purchased successfully'},
        400: {'description': 'Payment processing failed'},
        503: {'description': 'Guest service unavailable'}
    }
})
def buyticketbywallet():
    try:
        data = request.get_json()
        charge = data["charge"]
        # otp = data["otp"]
        amount = data["charge"]["amount"]
        guest_id = data["guest_id"]

        response = invoke_http(f"{stripe_URL}/charges", method="POST", json=charge)
        if response.get("code", 200) == 200:
            otp = None
            while True:
                otp = invoke_http(f"{otp_URL}", method="GET")
                if validate_otp(otp):
                    break

            invoke_http(
                f"{guest_URL}/buyticketfromwallet/{guest_id}",
                method="PUT",
                json={"otp": otp, "amount": amount}
            )

            rabbit_client.channel.basic_publish(
                exchange=exchange_name,
                routing_key="payment.notification",
                body=json.dumps({"guest_id": guest_id}),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            return jsonify({"message": "Payment successful! Ticket purchased."}), 200

        return jsonify({"error": "Stripe payment failed"}), 400

    except Exception as e:
        log_error("payment_service", "/buyticketbywallet", e)
        return jsonify({"error": "Payment processing failed."}), 400


# -----------------------------
# Wallet Top-up
# -----------------------------
@payment_blueprint.route("/topupwallet", methods=["POST"])
@swag_from({
    'tags': ['Payment'],
    'summary': 'Top up wallet via Stripe',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'charge': {'type': 'object'},
                'guest_id': {'type': 'integer'}
            },
            'required': ['charge', 'guest_id']
        }
    }],
    'responses': {
        200: {'description': 'Top-up successful'},
        400: {'description': 'Payment processing failed'},
        503: {'description': 'Guest service unavailable'}
    }
})
def topupwallet():
    try:
        data = request.get_json()
        charge = data["charge"]
        guest_id = data["guest_id"]
        amount = charge["amount"]

        response = invoke_http(f"{stripe_URL}/charges", method="POST", json=charge)
        if response.get("code", 200) == 200:
            invoke_http(
                f"{guest_URL}/updatewallet/{guest_id}",
                method="PUT",
                json={"wallet": amount}
            )
            return jsonify({"message": "Payment successful! Wallet Top-up."}), 200

        return jsonify({"error": "Stripe payment failed"}), 400

    except Exception as e:
        log_error("payment_service", "/topupwallet", e)
        return jsonify({"error": "Payment processing failed."}), 400


# Register Blueprint
app.register_blueprint(payment_blueprint, url_prefix="/makepayment")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8087)
