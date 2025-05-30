from flask import Flask, Blueprint, jsonify
from flasgger import Swagger
import RPi.GPIO as GPIO

# -------------------------------
# Flask App Setup
# -------------------------------

app = Flask(__name__)
Swagger(app)  # Initialize Flasgger Swagger documentation
lock_blueprint = Blueprint("lock", __name__)

# -------------------------------
# GPIO Setup
# -------------------------------

relay_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.IN)

app_lock_open = False  # Track lock state internally

# -------------------------------
# Lock Control Functions
# -------------------------------

def open_lock():
    global app_lock_open
    try:
        if not app_lock_open:
            GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.output(relay_pin, False)  # Set pin LOW to activate relay
            app_lock_open = True
            print("🔓 Lock opened")
        else:
            print("🔓 Lock already open")
    except Exception as e:
        print(f"❌ Error opening lock: {e}")
        raise

def close_lock():
    global app_lock_open
    try:
        if app_lock_open:
            GPIO.setup(relay_pin, GPIO.IN)  # Set back to input mode
            app_lock_open = False
            print("🔒 Lock closed")
        else:
            print("🔒 Lock already closed")
    except Exception as e:
        print(f"❌ Error closing lock: {e}")
        raise

# -------------------------------
# API Routes
# -------------------------------

@lock_blueprint.route("/open", methods=["GET"])
def open_lock_api():
    """
    Open the lock.
    ---
    tags:
      - Lock Control
    responses:
      200:
        description: Lock opened successfully or already open.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Lock opened!"
      500:
        description: Failed to open lock.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to open lock: <error message>"
    """
    try:
        if not app_lock_open:
            open_lock()
            return jsonify({"message": "Lock opened!"}), 200
        return jsonify({"message": "Lock is already open!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to open lock: {e}"}), 500

@lock_blueprint.route("/close", methods=["GET"])
def close_lock_api():
    """
    Close the lock.
    ---
    tags:
      - Lock Control
    responses:
      200:
        description: Lock closed successfully or already closed.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Lock closed!"
      500:
        description: Failed to close lock.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to close lock: <error message>"
    """
    try:
        if app_lock_open:
            close_lock()
            return jsonify({"message": "Lock closed!"}), 200
        return jsonify({"message": "Lock is already closed!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to close lock: {e}"}), 500

@lock_blueprint.route("/get_state", methods=["GET"])
def get_lock_state():
    """
    Get the current state of the lock.
    ---
    tags:
      - Lock Control
    responses:
      200:
        description: Current lock state.
        schema:
          type: object
          properties:
            lock_state:
              type: boolean
              example: true
      500:
        description: Failed to get lock state.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to get lock state: <error message>"
    """
    try:
        return jsonify({"lock_state": app_lock_open}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get lock state: {e}"}), 500

# -------------------------------
# Register Blueprint and Run App
# -------------------------------

app.register_blueprint(lock_blueprint, url_prefix="/lock")

if __name__ == '__main__':
    try:
        print("🚀 Starting Lock Control API on port 8079")
        app.run(host='0.0.0.0', port=8079)
    except Exception as e:
        print(f"❌ Flask app encountered an error: {e}")
    finally:
        GPIO.cleanup()
        print("🧼 GPIO cleanup completed")
