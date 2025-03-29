from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS

import requests

import time

import pika
import sys
import os
import json
from dotenv import load_dotenv
# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import RabbitMQClient
from RabbitMQClient import RabbitMQClient  # Import the class from the module

#region RabbitMQ Configuration
exchange_name = "park_topic"
exchange_type = "topic"

rabbit_client = RabbitMQClient(
    hostname="rabbitmq",
    port=5672,
    exchange_name=exchange_name,
    exchange_type=exchange_type
)
#endregion

# Flask App Setup
app = Flask(__name__)

CORS(app)

# Blueprint for Enter Park Routes
enter_park_blueprint = Blueprint("enter_park", __name__)

load_dotenv()

error_URL = os.getenv('ERROR_URL')
staff_URL = os.getenv('STAFF_URL')
guest_URL = os.getenv('GUEST_URL')
lock_URL = os.getenv('TESTLOCK_URL')
# Use this when Pi is connected
# lock_URL = os.getenv('LOCK_URL')
# Use this when Pi isn't connected

@enter_park_blueprint.route("/guest/<int:otp>", methods=["GET"])
def guest_enter_park(otp):

    try:
        # Check if in Guest DB
        r = requests.get(f"{guest_URL}/validate/{otp}")
        
        # Guest Found!
        if r.status_code == 200:
            open_door()
            return jsonify({"message": "Access granted! Door opening."}), 200

    except requests.exceptions.RequestException as e:

        # log_error("enter_park",f"/guest/{otp} (GET)", str(e))
        message = {
            "service":"enter_park",
            "endpoint": f"/guest/{otp} (GET)",
            "error": str(e)
            }
        rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.error",
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
        return jsonify({"error": "Guest service unavailable. Try again later."}), 503

    # TODO: Change the guest_URL to the right one
    # No Guest Found! Redirect them to buy tickets
    return jsonify({
        "message": "No valid ticket found. Please purchase a ticket.",
        "redirect_url": f"{guest_URL}/buy_ticket"
    }), 404

@enter_park_blueprint.route("/staff", methods=["POST"])
def staff_enter_park():
    
    # Check if Request Body was provided
    if not request.json:
        return jsonify({"error": "Missing request body"}), 400

    try:
        # Check if in Staff DB
        r = requests.post(f"{staff_URL}/validate",json=request.json)

        # Staff Found!
        if(r.status_code == 200):
            open_door()

            try:
                data = {
                    # Get Staff ID
                    "staff_id": r.json()['Staff']['staff_id'],
                    "type": "Success",
                    # Get Staff Name
                    "message": f"Staff member {r.json()['Staff']['staff_name']} entered the Park!"
                    }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.access",
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2),
                    )
            except Exception as e:
                message = {
                    "service":"enter_park",
                    "endpoint": "/staff (POST)",
                    "error": str(e)
                    }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.error",
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2),
                    )
                return jsonify({"error": "Staff service unavailable. Try again later."}), 503
            
        # Invalid Password
        elif(r.status_code == 401):
            print("Invalid Password, Please Try Again")
        
        elif(r.status_code == 403):
            # TODO: Telegram Notification
            print("Account Locked due to failed attempts")
            try:
                data = {
                    "staff_id": r.json()['Staff']['staff_id'],
                    "type": "Failed",
                    "message": f"Staff member {r.json()['Staff']['staff_name']} attempted to access the park but failed."
                }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.access",
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                
                if r.status_code != 201:
                    print(f"Failed to log entry: {r.status_code} - {r.text}")
            except Exception as e:
                message = {
                    "service":"enter_park",
                    "endpoint": "/staff (POST)",
                    "error": str(e)
                    }
                
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.error",
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2),
                    )
                # log_error("enter_park","/staff (POST)", str(e))
                print(f"Error logging entry: {e}")
        
        else:
            print(f"Unexpected status code: {r.status_code}")

        return r.json(), r.status_code
    
    except Exception as e:
        message = {
            "service":"enter_park",
            "endpoint": "/staff (POST)",
            "error": str(e)
            }
        rabbit_client.channel.basic_publish(
            exchange=exchange_name,
            routing_key="enterpark.error",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
            )
        # log_error("enter_park","/staff (POST)", str(e))
        return jsonify({"error": "Service unavailable"}), 503
    
def open_door():
    requests.get(lock_URL + "/open")
    time.sleep(3)
    requests.get(lock_URL + "/close")

# Register the enter_park Blueprint
app.register_blueprint(enter_park_blueprint, url_prefix="/enter_park")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)
#endregion