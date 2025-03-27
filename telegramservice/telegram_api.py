import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    Dispatcher,
    ConversationHandler,
)
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from invokes import invoke_http

# Define states for conversation
AWAITING_OTP, AWAITING_STAFFPASSWORD, AWAITING_BROADCASTMSG = range(3)

# region Create a Flask app
app = Flask(__name__)
CORS(app)

TOKEN = os.getenv("TOKEN")
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
WEBHOOK_URL = "https://telegram.esdlockdownparker.org/telegramservice/"
# GOOGLE_APPLICATION_CREDENTIALS = "/app/esdlocking.json"
GOOGLE_APPLICATION_CREDENTIALS = "./esdlocking.json"

bot = Bot(token=TOKEN)

staff_URL = "http://127.0.0.1:8083/staff"  # Staff service endpoint
guest_URL = "http://127.0.0.1:8082/guest"  # Guest service endpoint

# guest_URL = os.getenv("GUEST_URL")


# Set up Telegram Webhook
def set_webhook():
    return bot.set_webhook(url=WEBHOOK_URL)


@app.route("/health", methods=["GET"])
def health_check():
    return "Healthy", 200


@app.route("/", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        dispatcher.process_update(update)
        return "OK", 200
    except Exception as e:
        return "Internal Server Error", 500


# Command Handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the ESD Lockdown Parker Bot! How can I assist you today?"
    )


def login(update: Update, context: CallbackContext):
    update.message.reply_text("Please login to your account.")


def otp_received(update: Update, context: CallbackContext):
    otp = update.message.text.strip()
    response = invoke_http(
                        f"{guest_URL}/validate/{otp}", method="GET"
                    )
    if response.get("code", 200) == 200:
        #update chat_id in database
        chat_id = update.message.chat_id
        response = invoke_http(
                        f"{guest_URL}/update_chat_id_by_otp", method="PUT", json={"otp": otp, "chat_id": chat_id}
                    )
        if response.get("code", 200) == 200:
            update.message.reply_text("Login successful!")
        else:
            update.message.reply_text("Invalid OTP. Please try again.")

    return ConversationHandler.END  # End the conversation

def password_received(update: Update, context: CallbackContext):
    password = update.message.text.strip()
    teleHandler = update.message.chat.username
    chat_id = update.message.chat_id
    response = invoke_http(
                        f"{guest_URL}/update_chat_id_by_tele_password", method="PUT", json={"password": password, "teleHandler": teleHandler, "chat_id": chat_id}
                    )
    if response.get("code", 200) == 200:
        update.message.reply_text("Login successful!")
    else:
        update.message.reply_text("Invalid OTP. Please try again.")

    return ConversationHandler.END  # End the conversation

def broadcast_msg_received(update: Update, context: CallbackContext):
    msg = update.message.text.strip()

    #check if chat id exists in database for staff if it is then get all guest in park and send it out
    chat_id = update.message.chat_id
    response = invoke_http(
                        f"{staff_URL}/validate_chat_id/{chat_id}", method="GET"
                    )
    if response.get("code", 200) == 200:
        # Get all guest in park and send the message to them
        response = invoke_http(
                        f"{guest_URL}/valid_chat_ids", method="GET"
                    )
        if response.get("code", 200) == 200:
            for chat_ids in response["chat_ids"]:
                # Send the message to each chat_id
                bot.send_message(chat_id=chat_ids, text=msg)
            update.message.reply_text("Broadcast message sent successfully!")
        else:
            update.message.reply_text("Unable to retrieve guests. Please try again later.")

    return ConversationHandler.END  # End the conversation

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("No Response. Please try again.")
    return ConversationHandler.END


def staff_login(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your password.")


def check_balance(update: Update, context: CallbackContext):
    #get balance if chat id exists in database
    chat_id = update.message.chat_id
    # Here, you can check the balance (replace this with actual balance checking logic)
    response = invoke_http(
                        f"{guest_URL}/wallet/{chat_id}", method="GET"
                    )
    if response.get("code", 200) == 200:
        balance = response["wallet"]
        update.message.reply_text(f"Your balance is: {balance}")
    else:
        update.message.reply_text("Unable to retrieve balance. Please try again later.")

def broadcast(update: Update, context: CallbackContext):
    update.message.reply_text("Please broadcast your message.")


def detect_intent_from_dialogflow(session_id, text):
    url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/{session_id}:detectIntent"
    headers = {
        "Authorization": f"Bearer {get_google_access_token()}",
        "Content-Type": "application/json",
    }
    payload = {"query_input": {"text": {"text": text, "language_code": "en"}}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def help(update: Update, context: CallbackContext):
    help_text = (
        "Here are the commands you can use:\n\n"
        "/start - Welcome message\n"
        "/login - Login to your account\n"
        "/stafflogin - Login to your staff account\n"
        "/checkBalance - Check your balance\n"
        "/broadcast - Broadcast a message\n"
        "/help - Show this help message"
    )
    update.message.reply_text(help_text)


def get_google_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token


@app.route("/sendMsg", methods=["POST"])
def send_message_to_telegram():
    data = request.json
    chat_id = data.get("chat_id")
    text = data.get("text")

    if not chat_id or not text:
        return jsonify({"error": "Missing chat_id or text"}), 400

    bot.send_message(chat_id=chat_id, text=text)
    return jsonify({"status": "Message sent"}), 200


# Initialize Dispatcher for Handling Commands
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("checkBalance", check_balance))
dispatcher.add_handler(CommandHandler("help", help))

login_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("login", login)],
    states={
        AWAITING_OTP: [MessageHandler(Filters.text & ~Filters.command, otp_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
stafflogin_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("stafflogin", staff_login)],
    states={
        AWAITING_STAFFPASSWORD: [MessageHandler(Filters.text & ~Filters.command, password_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
broadcast_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("broadcast", broadcast)],
    states={
        AWAITING_STAFFPASSWORD: [MessageHandler(Filters.text & ~Filters.command, broadcast_msg_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

dispatcher.add_handler(login_conv_handler)
dispatcher.add_handler(stafflogin_conv_handler)
dispatcher.add_handler(broadcast_conv_handler)
if __name__ == "__main__":
    print(set_webhook())
    app.run(host="0.0.0.0", port=8081, debug=True)
