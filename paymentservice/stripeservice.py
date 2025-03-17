from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SK")
# region Create a Flask app

app = Flask(__name__)
CORS(app)

# endregion

# region Create a Blueprint for payment routes
# Create a Blueprint for Payment routes
payment_blueprint = Blueprint("stripeservice", __name__)
# endregion

@payment_blueprint.route("/charge", methods=["POST"])
def charge():
    try:
        data = request.json
        amount = data.get("amount")
        currency = data.get("currency")
        description = data.get("description")
        source = data.get("source")  # Token generated on frontend (e.g., via Stripe Elements)

        # Create the charge
        charge = stripe.Charge.create(
            amount=amount,  # The amount is in cents, so 1000 = $10.00
            currency=currency,
            description=description,
            source=source  # The token received from frontend (e.g., 'tok_visa')
        )

        return jsonify(charge), 200  # Return the charge details
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=str(e)), 400


app.register_blueprint(payment_blueprint, url_prefix="/stripeservice")
# region Setting up Flask app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086, debug=True)
# endregion
