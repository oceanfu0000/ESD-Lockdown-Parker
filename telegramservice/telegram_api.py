import os
from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

#region Create a Flask app
app = Flask(__name__)
CORS(app)

# Create a Blueprint for Telegram routes
telegramservice_blueprint = Blueprint("telegramservice", __name__)


#endregion

# Environment variables for Telegram Bot Token and Webhook URL
TOKEN = os.getenv('TOKEN')
PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = "telegram.esdlockdownparker.org/telegramservice/"
DIALOGFLOW_PROJECT_ID = PROJECT_ID
DIALOGFLOW_LANGUAGE_CODE = "en"
GOOGLE_APPLICATION_CREDENTIALS = "telegramservice/esdlocking.json"

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})
    return response.json()

@telegramservice_blueprint.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        if "message" in data and "chat" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_message = data["message"].get("text", "").lower()
            print(f"Received message from chat ID {chat_id}: {user_message}")

            # Forward message to Dialogflow
            dialogflow_response = detect_intent_from_dialogflow(chat_id, user_message)
            print(dialogflow_response)
            reply = dialogflow_response.get("queryResult", {}).get("fulfillmentText", "I didn't understand that.")
            
            send_message(chat_id, reply)
        
        return "OK", 200
    except Exception as e:
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500


def detect_intent_from_dialogflow(session_id, text):
    url = f"https://dialogflow.googleapis.com/v2/projects/{DIALOGFLOW_PROJECT_ID}/agent/sessions/{session_id}:detectIntent"
    headers = {
        "Authorization": f"Bearer {get_google_access_token()}",
        "Content-Type": "application/json"
    }
    payload = {
        "query_input": {
            "text": {
                "text": text,
                "language_code": DIALOGFLOW_LANGUAGE_CODE
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_google_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(Request())  # This will refresh the token if it's expired
    return credentials.token

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

#region Setting up Flask app
# Register the Telegram Blueprint
app.register_blueprint(telegramservice_blueprint, url_prefix="/telegramservice")

def test_detect_intent():
    # Ensure your credentials are valid and the API call works
    session_id = "test-session"
    text = "Hello"
    response = detect_intent_from_dialogflow(session_id, text)
    print(response)
    
if __name__ == "__main__":
    print(set_webhook())
    test_detect_intent();
    app.run(host="0.0.0.0", port=8081, debug=True)
#endregion

