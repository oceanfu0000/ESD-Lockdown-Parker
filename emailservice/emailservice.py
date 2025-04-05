from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
import base64
import logging
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flasgger import Swagger, swag_from

# ------------------------------
# Configuration
# ------------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")
# TOKEN_PATH = "emailservice/token.json"
# CREDS_PATH = "emailservice/credentials.json"
CREDS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
SENDER_EMAIL = "serviceatpark@gmail.com"  # Change if needed

# ------------------------------
# Flask App Setup
# ------------------------------

app = Flask(__name__)
Swagger(app)
CORS(app)
email_blueprint = Blueprint("email", __name__)
logging.basicConfig(level=logging.INFO)

# ------------------------------
# Gmail Authentication
# ------------------------------

def authenticate():
    """Authenticate with Gmail and handle token refresh or regeneration."""
    creds = None

    try:
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            print(creds)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logging.info("✅ Token refreshed successfully.")
                except Exception as e:
                    logging.warning(f"⚠️ Token refresh failed: {e}")
                    creds = None  # fallback to full auth flow

            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_PATH, "w") as token_file:
                    token_file.write(creds.to_json())
                logging.info("✅ token.json generated successfully")

        return build("gmail", "v1", credentials=creds)

    except Exception as e:
        logging.exception("❌ Failed to authenticate with Gmail")
        raise RuntimeError(f"Gmail authentication failed: {str(e)}")

# ------------------------------
# Send Email
# ------------------------------

def send_email(service, sender, to, subject, message_text):
    """Compose and send an email via Gmail API."""
    try:
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

        logging.info(f"📨 Email sent successfully. Message ID: {result['id']}")
        return {"message_id": result["id"], "status": "Email sent successfully"}

    except HttpError as error:
        logging.error(f"❌ Gmail API error: {error}")
        raise RuntimeError(f"Gmail API error: {error}")

# ------------------------------
# Route
# ------------------------------

@email_blueprint.route("", methods=["POST"])
@swag_from({
    'tags': ['Email'],
    'summary': 'Send an email via Gmail API',
    'description': 'This endpoint allows you to send an email using the Gmail API. Provide recipient, subject, and message text in the request.',
    'parameters': [
        {
            'name': 'to',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Recipient email address'
        },
        {
            'name': 'subject',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Subject of the email'
        },
        {
            'name': 'message',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Text content of the email message'
        }
    ],
    'responses': {
        200: {
            'description': 'Email sent successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message_id': {
                        'type': 'string',
                        'description': 'The unique ID of the sent message'
                    },
                    'status': {
                        'type': 'string',
                        'description': 'The status of the email sending operation'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields ("to", "subject", or "message")',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Missing 'to', 'subject', or 'message' in request."
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Internal server error"
                    }
                }
            }
        }
    }
})
def sending_email():
    try:
        data = request.get_json()

        recipient_email = data.get("to")
        subject = data.get("subject")
        message_text = data.get("message")

        if not all([recipient_email, subject, message_text]):
            return jsonify({"error": "Missing 'to', 'subject', or 'message' in request."}), 400

        service = authenticate()
        response = send_email(service, SENDER_EMAIL, recipient_email, subject, message_text)
        return jsonify(response), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logging.exception("❌ Unexpected error occurred")
        return jsonify({"error": "Internal server error"}), 500

# ------------------------------
# App Registration & Entry Point
# ------------------------------

app.register_blueprint(email_blueprint, url_prefix="/email")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)
