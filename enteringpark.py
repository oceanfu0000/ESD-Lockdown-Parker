from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS

import sys
import os

from supabase import create_client, Client
from dotenv import load_dotenv

import requests
from invokes import invoke_http

#region Create a Blueprint for enter_park routes
app = Flask(__name__)

CORS(app)

enter_park_blueprint = Blueprint("enter_park", __name__)

#endregion

staff_URL = "http://127.0.0.1:8083/staff"
guest_URL = "http://127.0.0.1:8082/guest"
# Not Done Yet
# door_URL = 
log_URL = "http://127.0.0.1:8084/log"

@enter_park_blueprint.route("/guest/<int:otp>", methods=["GET"])
def user_enter_park(otp):

    print("Checking if in Guest DB")
    guest_details = invoke_http(f"{guest_URL}/validate/{otp}")
    code = guest_details.get("code")
    print(guest_details["code"])

    if(guest_details["code"] == 200):
        print("Guest in DB! Opening Door Now")
    
    elif(guest_details["code"] == 404):
        print("walahee")

    return guest_details

@enter_park_blueprint.route("/staff", methods=["GET"])
def guest_enter_park():

    print("Checking if in Staff DB")
    staff_details = invoke_http(f"{staff_URL}/validate",method="POST",json=request.json)
    code = staff_details.get("code")
    print(staff_details["code"])

    if(staff_details["code"] == 200):
        print("Staff in DB! Opening Door Now")
    
    else:
        print("walahee")

    return staff_details  

# Register the enter_park Blueprint
app.register_blueprint(enter_park_blueprint, url_prefix="/enter_park")

#region Setting up Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)
#endregion