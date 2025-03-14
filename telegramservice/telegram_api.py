import os
import requests
from flask import Blueprint, request

# Create a Blueprint for Telegram routes
telegram_blueprint = Blueprint("telegram", __name__)

# Environment variables for Telegram Bot Token and Webhook URL
TOKEN = os.getenv('TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@telegram_blueprint.route("/", methods=["POST"])
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
