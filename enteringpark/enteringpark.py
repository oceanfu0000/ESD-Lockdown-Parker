from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS

from datetime import datetime

import requests

import time

#region Create a Blueprint for enter_park routes
app = Flask(__name__)

CORS(app)

enter_park_blueprint = Blueprint("enter_park", __name__)

#endregion

#region Error Endpoint
ERROR_MICROSERVICE_URL = "http://127.0.0.1:8079/error"

def log_error(service, endpoint, error):
    error_data = {
        "service": service,
        "endpoint": endpoint,
        "error": error
    }
    try:
        requests.post(ERROR_MICROSERVICE_URL, json=error_data)
    except Exception as e:
        print(f"Failed to log error: {e}")
#endregion

staff_URL = "http://127.0.0.1:8083/staff"
guest_URL = "http://127.0.0.1:8082/guest"
log_URL = "http://127.0.0.1:8084/logs"
# Use this when Pi is connected
door_URL = "https://lock.esdlockdownparker.org/"
# Use this when Pi isn't connected
lock_URL = "http://127.0.0.1:8083/testlock"


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
        log_error("enter_park",f"/guest/{otp} (GET)", str(e))
        return jsonify({"error": "Guest service unavailable. Try again later."}), 503

    # TODO: Change the guest_URL to the right one
    # No Guest Found! Redirect them to buy tickets
    return jsonify({
        "message": "No valid ticket found. Please purchase a ticket.",
        "redirect_url": f"{guest_URL}/buy_ticket"
    }), 404

# NOTE: WIP
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
                    "message": f"Staff member {r.json()['Staff']['staff_name']} entered the Park!",
                    "date_time": datetime.now().isoformat()
                    }
                r = requests.post(log_URL,json=data)

            except Exception as e:
                log_error("enter_park","/staff (POST)", str(e))
                print(f"Error logging entry: {e}")

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
                    "message": f"Staff member {r.json()['Staff']['staff_name']} attempted to access the park but failed.",
                    "date_time": datetime.now().isoformat()
                }
                r = requests.post(log_URL,json=data)

                if r.status_code != 201:
                    print(f"Failed to log entry: {r.status_code} - {r.text}")
            except Exception as e:
                log_error("enter_park","/staff (POST)", str(e))
                print(f"Error logging entry: {e}")
        
        else:
            print(f"Unexpected status code: {r.status_code}")

        return r.json(), r.status_code
    
    except Exception as e:
        log_error("enter_park","/staff (POST)", str(e))
        return jsonify({"error": "Service unavailable"}), 503
    
#region Door Opening/Closing
def open_door():
    # For Testing Purposes
    requests.get(lock_URL + "/open")
    time.sleep(3)
    requests.get(lock_URL + "/close")

    # Actual Demo
    requests.get(door_URL + "/open")
    time.sleep(3)
    requests.get(door_URL + "/close")
#endregion

# Register the enter_park Blueprint
app.register_blueprint(enter_park_blueprint, url_prefix="/enter_park")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)
#endregion