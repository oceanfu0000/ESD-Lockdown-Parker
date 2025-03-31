from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import stripe
import os
from dotenv import load_dotenv
from flasgger import Swagger, swag_from


# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SK")

# Flask app setup
app = Flask(__name__)
Swagger(app)
CORS(app)

# Blueprint for Stripe service routes
payment_blueprint = Blueprint("stripeservice", __name__)

@payment_blueprint.route("/charges", methods=["POST"])
@swag_from({
    'tags': ['Payment'],
    'summary': 'Create a charge',
    'description': 'This endpoint processes a payment by creating a charge using Stripe API.',
    'parameters': [
        {
            'name': 'amount',
            'in': 'body',
            'type': 'integer',
            'required': True,
            'description': 'Amount to charge in the smallest unit (e.g., cents)',
        },
        {
            'name': 'currency',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Currency code (e.g., USD)',
        },
        {
            'name': 'description',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Description of the charge',
        },
        {
            'name': 'source',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Source of the payment, such as a token or card ID',
        }
    ],
    'responses': {
        200: {
            'description': 'Charge successfully created',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Charge successful'},
                    'charge': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'ch_1FzUVy2eZvKYlo2CEXa32z6V'},
                            'amount': {'type': 'integer', 'example': 1000},
                            'currency': {'type': 'string', 'example': 'usd'},
                            'description': {'type': 'string', 'example': 'Payment for XYZ service'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required fields'}
                }
            }
        },
        402: {
            'description': 'Card error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Card error: Your card has insufficient funds'}
                }
            }
        },
        401: {
            'description': 'Authentication error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Authentication with Stripe API failed'}
                }
            }
        },
        429: {
            'description': 'Rate limit exceeded',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Too many requests to Stripe API'}
                }
            }
        },
        503: {
            'description': 'Network error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Network communication with Stripe failed'}
                }
            }
        },
        500: {
            'description': 'Stripe API error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Something went wrong with Stripe'}
                }
            }
        }
    }
})
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
