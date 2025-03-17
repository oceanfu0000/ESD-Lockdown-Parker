from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import requests
import stripe
import os

# region Create a Flask app

app = Flask(__name__)
CORS(app)

# endregion

# region Create a Blueprint for payment routes
# Create a Blueprint for Payment routes
payment_blueprint = Blueprint("payment", __name__)
# endregion

staff_URL = "http://127.0.0.1:8083/staff"
guest_URL = "http://127.0.0.1:8082/guest"
log_URL = "http://127.0.0.1:8084/logs"
stripe_URL = "http://127.0.0.1:8086/stripeservice"

@payment_blueprint.route("/buyticket", methods=["POST"])
def buyticket():
    try:
        r = requests.post(f"{stripe_URL}/charges",{request.json['charge']})
        if r.status_code == 200:

            return jsonify({"message": "Payment successful! Ticket purchased."}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with stripe service: {e}")
        return jsonify({"error": "Stripe service unavailable. Try again later."}), 503
    
       
        return jsonify(charge), 200  # Return the charge details
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=str(e)), 400
    
@payment_blueprint.route("/topupwallet", methods=["POST"])
def topupwallet():
    try:
        r = requests.post(f"{stripe_URL}/charges",{request.json['charge']})
        if r.status_code == 200:
            try:
                guestWallet = requests.put(f"{guest_URL}/{request.json['guest_id']}",{"wallet":request.json['charge']['amount']})
                #put get otp
                otp = 1234
                
            except requests.exceptions.RequestException as e:
                print(f"Error communicating with guest service: {e}")
                return jsonify({"error": "Guest service unavailable. Try again later."}), 503
            except Exception as e:
                return jsonify(error=str(e)), 400

            return jsonify({"message": "Payment successful! Wallet Top-up"}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with stripe service: {e}")
        return jsonify({"error": "Stripe service unavailable. Try again later."}), 503
    
       
        return jsonify(charge), 200  # Return the charge details
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=str(e)), 400

#pay loyalty points

app.register_blueprint(payment_blueprint, url_prefix="/stripeservice")
# region Setting up Flask app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8087, debug=True)
# endregion
