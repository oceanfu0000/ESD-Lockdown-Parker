from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SK")

# Flask app setup
app = Flask(__name__)
CORS(app)

# Blueprint for Stripe service routes
payment_blueprint = Blueprint("stripeservice", __name__)

@payment_blueprint.route("/charges", methods=["POST"])
def charge():
    try:
        data = request.get_json()
        # data = requestJson["charge"]

        required_fields = {"amount", "currency", "description", "source"}
        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing required fields"}), 400

        # Create the charge using Stripe API
        charge = stripe.Charge.create(
            amount=data["amount"],
            currency=data["currency"],
            description=data["description"],
            source=data["source"]
        )

        print("✅ Charge created:", charge["id"])
        return jsonify({"message": "Charge successful", "charge": charge}), 200

    except stripe.error.CardError as e:
        return jsonify({"error": f"Card error: {e.user_message}"}), 402

    except stripe.error.RateLimitError as e:
        return jsonify({"error": "Too many requests to Stripe API"}), 429

    except stripe.error.InvalidRequestError as e:
        return jsonify({"error": f"Invalid request: {e.user_message}"}), 400

    except stripe.error.AuthenticationError as e:
        return jsonify({"error": "Authentication with Stripe API failed"}), 401

    except stripe.error.APIConnectionError as e:
        return jsonify({"error": "Network communication with Stripe failed"}), 503

    except stripe.error.StripeError as e:
        return jsonify({"error": "Something went wrong with Stripe"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Register blueprint
app.register_blueprint(payment_blueprint, url_prefix="/stripeservice")

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
