import json
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import pika
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from RabbitMQClient import RabbitMQClient
from invokes import invoke_http

# RabbitMQ Configuration
exchange_name = "payment_topic"
exchange_type = "topic"

rabbit_client = RabbitMQClient(
    hostname="localhost",
    port=5672,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

# Flask App Setup
app = Flask(__name__)
CORS(app)

# Blueprint for Payment Routes
payment_blueprint = Blueprint("payment", __name__)

# Service URLs
staff_URL = "http://127.0.0.1:8083/staff"  # Staff service endpoint
guest_URL = "http://127.0.0.1:8082/guest"  # Guest service endpoint
log_URL = "http://127.0.0.1:8084/logs"  # Logging service endpoint
stripe_URL = "http://127.0.0.1:8086/stripeservice"  # Stripe payment service endpoint
error_URL = "http://127.0.0.1:8078/error"  # Error logging endpoint
otp_URL = os.getenv("OTP_URL")  # OTP service endpoint


# Function to log errors by sending a request to the error logging service
def log_error(service, endpoint, error):
    requests.post(
        error_URL, json={"service": service, "endpoint": endpoint, "error": str(error)}
    )


# Endpoint to handle ticket purchase
@payment_blueprint.route("/buyticket", methods=["POST"])
def buyticket():
    try:
        # Process payment through Stripe
        response = invoke_http(
            f"{stripe_URL}/charges", method="POST", json=request.json["charge"]
        )
        if response.get("code", 200) == 200:
            try:
                # Validate OTP uniqueness
                while True:
                    otp_response = invoke_http(
                        f"{otp_URL}/isotpunique/{request.json['otp']}", method="GET"
                    )
                    otp_response = invoke_http(
                        f"{guest_URL}/isotpunique/{otp_response}", method="GET"
                    )
                    if otp_response.get("code", 200) == 200:
                        break

                # Associate OTP with the guest and complete ticket purchase
                invoke_http(
                    f"{guest_URL}/buyticket/{request.json['guest_id']}",
                    method="PUT",
                    json={"otp": otp_response},
                )

                # Notify other services via RabbitMQ
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="payment.notification",
                    body=json.dumps(
                        request.json["guest_id"]
                    ),  # json.dumps(message) might need this
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                return (
                    jsonify({"message": "Payment successful! Ticket purchased."}),
                    200,
                )
            except Exception as e:
                log_error("Payment Service", "/buyticket", e)
                return (
                    jsonify({"error": "Guest service unavailable. Try again later."}),
                    503,
                )
    except Exception as e:
        log_error("Payment Service", "/buyticket", e)
        return jsonify({"error": "Payment processing failed."}), 400


# Endpoint to handle ticket purchase using loyalty points
@payment_blueprint.route("/buyticketbyloyalty", methods=["POST"])
def buyticketbyloyalty():
    try:
        response = invoke_http(
            f"{stripe_URL}/charges", method="POST", json=request.json["charge"]
        )
        if response.get("code", 200) == 200:
            try:
                # Validate OTP uniqueness
                while True:
                    otp_response = invoke_http(
                        f"{otp_URL}/isotpunique/{request.json['otp']}", method="GET"
                    )
                    otp_response = invoke_http(
                        f"{guest_URL}/isotpunique/{otp_response}", method="GET"
                    )
                    if otp_response.get("code", 200) == 200:
                        break
                invoke_http(
                    f"{guest_URL}/buyticketbyloyalty/{request.json['guest_id']}",
                    method="PUT",
                    json={"otp": otp_response, "points": request.json["amount"]},
                )
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="payment.notification",
                    body=request.json["guest_id"],
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                return (
                    jsonify({"message": "Payment successful! Ticket purchased."}),
                    200,
                )
            except Exception as e:
                log_error("Payment Service", "/buyticketbyloyalty", e)
                return (
                    jsonify({"error": "Guest service unavailable. Try again later."}),
                    503,
                )
    except Exception as e:
        log_error("Payment Service", "/buyticketbyloyalty", e)
        return jsonify({"error": "Payment processing failed."}), 400


# Endpoint to handle ticket purchase using wallet
@payment_blueprint.route("/buyticketbywallet", methods=["POST"])
def buyticketbywallet():
    try:
        response = invoke_http(
            f"{stripe_URL}/charges", method="POST", json=request.json["charge"]
        )
        if response.get("code", 200) == 200:
            try:
                # Validate OTP uniqueness
                while True:
                    otp_response = invoke_http(
                        f"{otp_URL}/isotpunique/{request.json['otp']}", method="GET"
                    )
                    otp_response = invoke_http(
                        f"{guest_URL}/isotpunique/{otp_response}", method="GET"
                    )
                    if otp_response.get("code", 200) == 200:
                        break
                invoke_http(
                    f"{guest_URL}/buyticketfromwallet/{request.json['guest_id']}",
                    method="PUT",
                    json={"otp": otp_response, "amount": request.json["amount"]},
                )
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="payment.notification",
                    body=request.json["guest_id"],
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                return (
                    jsonify({"message": "Payment successful! Ticket purchased."}),
                    200,
                )
            except Exception as e:
                log_error("Payment Service", "/buyticketbywallet", e)
                return (
                    jsonify({"error": "Guest service unavailable. Try again later."}),
                    503,
                )
    except Exception as e:
        log_error("Payment Service", "/buyticketbywallet", e)
        return jsonify({"error": "Payment processing failed."}), 400


# Endpoint to handle wallet top-up
@payment_blueprint.route("/topupwallet", methods=["POST"])
def topupwallet():
    try:
        # Process payment through Stripe
        response = invoke_http(
            f"{stripe_URL}/charges", method="POST", json=request.json["charge"]
        )
        if response.get("code", 200) == 200:
            try:
                # Update guest wallet balance
                invoke_http(
                    f"{guest_URL}/updatewallet/{request.json['guest_id']}",
                    method="PUT",
                    json={"wallet": request.json["charge"]["amount"]},
                )

                return jsonify({"message": "Payment successful! Wallet Top-up."}), 200
            except Exception as e:
                log_error("Payment Service", "/topupwallet", e)
                return (
                    jsonify({"error": "Guest service unavailable. Try again later."}),
                    503,
                )
    except Exception as e:
        log_error("Payment Service", "/topupwallet", e)
        return jsonify({"error": "Payment processing failed."}), 400


# Register the payment blueprint with Flask app
app.register_blueprint(payment_blueprint, url_prefix="/makepayment")

# Start Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8087, debug=True)
