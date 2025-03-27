from flask import Flask, Blueprint, jsonify
import RPi.GPIO as GPIO

# Flask app setup
app = Flask(__name__)

# Create a Blueprint for lock control
lock_blueprint = Blueprint("lock", __name__)

# GPIO setup
relay_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.IN)

app_lock_open = False

def open_lock():
    global app_lock_open
    try:
        if not app_lock_open:  # Only open if it's currently closed
            GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.output(relay_pin, False)
            app_lock_open = True
            print("Lock opened")
        else:
            print("Lock is already open")
    except Exception as e:
        print(f"Error opening lock: {e}")

def close_lock():
    global app_lock_open
    try:
        if app_lock_open:  # Only close if it's currently open
            GPIO.setup(relay_pin, GPIO.IN)
            GPIO.input(relay_pin)
            app_lock_open = False
            print("Lock closed")
        else:
            print("Lock is already closed")
    except Exception as e:
        print(f"Error closing lock: {e}")

@lock_blueprint.route('/open', methods=['GET'])
def open_lock_api():
    try:
        if not app_lock_open:
            open_lock()
            return jsonify({"message": "Lock opened!"}), 200
        else:
            return jsonify({"message": "Lock is already open!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to open lock: {e}"}), 500

@lock_blueprint.route('/close', methods=['GET'])
def close_lock_api():
    try:
        if app_lock_open:
            close_lock()
            return jsonify({"message": "Lock closed!"}), 200
        else:
            return jsonify({"message": "Lock is already closed!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to close lock: {e}"}), 500

@lock_blueprint.route('/get_state', methods=['GET'])
def get_lock_state():
    try:
        return jsonify({"lock_state": app_lock_open}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get lock state: {e}"}), 500

# Register the Blueprint with the Flask app
app.register_blueprint(lock_blueprint, url_prefix="/lock")

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8079)
    except Exception as e:
        print(f"Flask app encountered an error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")
