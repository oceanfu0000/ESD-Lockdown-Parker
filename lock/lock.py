from flask import Flask, Blueprint, jsonify
import RPi.GPIO as GPIO

# -------------------------------
# Flask App Setup
# -------------------------------

app = Flask(__name__)
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
    try:
        if not app_lock_open:
            open_lock()
            return jsonify({"message": "Lock opened!"}), 200
        return jsonify({"message": "Lock is already open!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to open lock: {e}"}), 500

@lock_blueprint.route("/close", methods=["GET"])
def close_lock_api():
    try:
        if app_lock_open:
            close_lock()
            return jsonify({"message": "Lock closed!"}), 200
        return jsonify({"message": "Lock is already closed!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to close lock: {e}"}), 500

@lock_blueprint.route("/get_state", methods=["GET"])
def get_lock_state():
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
