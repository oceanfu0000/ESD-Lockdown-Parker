import logging
import os
from flask import Blueprint, Flask
from flask_cors import CORS
from os import environ

#region Create a Blueprint for testlock routes
app = Flask(__name__)

CORS(app)

testlock_blueprint = Blueprint("testlock", __name__)

#endregion

@testlock_blueprint.route("/open", methods=["GET"])
def open_lock():
    print("Lock Opened")
    return "open"

@testlock_blueprint.route("/close", methods=["GET"])
def close_lock():
    print("Lock Closed")
    return "close"

app.register_blueprint(testlock_blueprint, url_prefix="/testlock")

#region Setting up Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083, debug=True)
#endregion