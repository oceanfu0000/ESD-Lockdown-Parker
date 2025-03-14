import os
from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests


#region Create a Flask app
app = Flask(__name__)

CORS(app)

# Create a Blueprint for Telegram routes
telegramservice_blueprint = Blueprint("telegram", __name__)

# Register the Telegram Blueprint
app.register_blueprint(telegramservice_blueprint, url_prefix="/telegramservice")

#endregion


# Environment variables for Telegram Bot Token and Webhook URL
TOKEN = os.getenv('TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@telegramservice_blueprint.route("/", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "chat" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"].lower()

        # Custom responses based on user message
        if user_message == "hi":
            reply = "Hello! How can I help you?"
        elif user_message == "bye":
            reply = "Goodbye! Have a great day!"
        else:
            reply = "Sorry, I don't understand."

        send_message(chat_id, reply)

    return "OK", 200

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


#region Setting up Flask app
app = Flask(__name__)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
#endregion