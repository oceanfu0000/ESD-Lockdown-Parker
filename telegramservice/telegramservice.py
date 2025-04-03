import os
import sys
import requests
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext,
    ConversationHandler, filters
)
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import pika
import json

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from invokes import invoke_http
from RabbitMQClient import RabbitMQClient

# ------------------------------
# Setup
# ------------------------------
load_dotenv()

TOKEN = os.getenv("TOKEN")
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = "esdlocking.json"

staff_URL = os.getenv("STAFF_URL")
guest_URL = os.getenv("GUEST_URL")

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

AWAITING_OTP, AWAITING_STAFFPASSWORD, AWAITING_BROADCASTMSG = range(3)

# -----------------------------
# RabbitMQ Configuration
# -----------------------------
exchange_name = "park_topic"
exchange_type = "topic"

rabbit_client = RabbitMQClient(
    hostname="rabbitmq",
    port=5672,
    exchange_name=exchange_name,
    exchange_type=exchange_type
)

# ------------------------------
# Command Handlers
# ------------------------------

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to the ESD Lockdown Parker Bot! Type /help to see available commands."
    )

async def help(update: Update, context: CallbackContext):
    help_text = (
        "Here are the commands you can use:\n\n"
        "/start - Welcome message\n"
        "/login - Login to your account\n"
        "/stafflogin - Login to your staff account\n"
        "/checkBalance - Check your balance\n"
        "/broadcast - Broadcast a message\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def login(update: Update, context: CallbackContext):
    await update.message.reply_text("Enter your OTP to login.")
    return AWAITING_OTP

async def staff_login(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter your password.")
    return AWAITING_STAFFPASSWORD

async def broadcast(update: Update, context: CallbackContext):
    await update.message.reply_text("Please broadcast your message.")
    return AWAITING_BROADCASTMSG

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Action cancelled. Please try again.")
    return ConversationHandler.END

# ------------------------------
# Action Handlers
# ------------------------------

async def check_balance(update: Update, context: CallbackContext):
    try:
        chat_id = update.message.chat_id
        response = invoke_http(f"{guest_URL}/wallet/{chat_id}", method="GET")
        if response.get("code", 200) == 200:
            await update.message.reply_text(f"Your balance is: {response['wallet']}")
        else:
            await update.message.reply_text("Unable to retrieve balance. Please login first.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    return ConversationHandler.END

async def otp_received(update: Update, context: CallbackContext):
    try:
        otp = update.message.text.strip()
        chat_id = update.message.chat_id

        response = invoke_http(f"{guest_URL}/validate/{otp}", method="GET")
        if response.get("code", 200) == 200:
            update_response = invoke_http(
                f"{guest_URL}/update_chat_id_by_otp", method="PUT",
                json={"otp": otp, "chat_id": chat_id}
            )
            if update_response.get("code", 200) == 200:
                await update.message.reply_text("Login successful!")
            else:
                await update.message.reply_text("Invalid OTP. Please try again.")
        else:
            await update.message.reply_text("Invalid OTP. Please try again.")
    except Exception as e:
        await update.message.reply_text(f"Error processing OTP: {e}")
    return ConversationHandler.END

async def password_received(update: Update, context: CallbackContext):
    try:
        password = update.message.text.strip()
        tele_handler = update.message.chat.username
        chat_id = update.message.chat_id

        response = invoke_http(
            f"{staff_URL}/update_chat_id_by_tele_password", method="PUT",
            json={"password": password, "staff_tele": tele_handler, "chat_id": chat_id}
        )
        if response.get("code", 200) == 200:
            await update.message.reply_text("Login successful!")
        else:
            await update.message.reply_text("Invalid credentials. Please try again.")
    except Exception as e:
        await update.message.reply_text(f"Login error: {e}")
    return ConversationHandler.END

async def broadcast_msg_received(update: Update, context: CallbackContext):
    try:
        msg = update.message.text.strip()
        chat_id = update.message.chat_id
        staff_check = invoke_http(f"{staff_URL}/validate_chat_id/{chat_id}", method="GET")
        if staff_check.get("code", 200) == 200:
            guest_response = invoke_http(f"{guest_URL}/valid_chat_ids", method="GET")
            if guest_response.get("code", 200) == 200:
                staff_info = staff_check["staff"][0]
                data = {
                    "user_id": staff_info["staff_id"],
                    "user_type": "staff",
                    "action": "Broadcast",
                    "type": "Success",
                    "message": f"Staff member {staff_info['staff_name']} broadcasted {msg}!" 
                }
                rabbit_client.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key="enterpark.access",
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2),
                    )
                for cid in guest_response["chat_ids"]:
                    try:
                        await bot.send_message(chat_id=cid, text=msg)
                    except Exception:
                        continue
                await update.message.reply_text("Broadcast sent.")
            else:
                await update.message.reply_text("Unable to retrieve guest list.")
        else:
            await update.message.reply_text("You are not authorized to broadcast.")
    except Exception as e:
        await update.message.reply_text(f"Broadcast error: {e}")
    return ConversationHandler.END

# ------------------------------
# Dialogflow Integration
# ------------------------------

def get_google_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

def detect_intent_from_dialogflow(session_id, text):
    try:
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/{session_id}:detectIntent"
        headers = {
            "Authorization": f"Bearer {get_google_access_token()}",
            "Content-Type": "application/json",
        }
        payload = {
            "query_input": {
                "text": {
                    "text": text,
                    "language_code": "en"
                }
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Dialogflow error: {e}")
        return {}

async def handle_message(update: Update, context: CallbackContext):
    try:
        user_message = update.message.text
        chat_id = update.message.chat_id

        response = detect_intent_from_dialogflow(chat_id, user_message)
        fulfillment_text = response.get("queryResult", {}).get("fulfillmentText")

        if fulfillment_text:
            await update.message.reply_text(fulfillment_text)
        else:
            await update.message.reply_text("I’m not sure how to respond to that.")
    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}")

# ------------------------------
# Handlers
# ------------------------------

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("checkBalance", check_balance))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("login", login)],
    states={AWAITING_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, otp_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("stafflogin", staff_login)],
    states={AWAITING_STAFFPASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("broadcast", broadcast)],
    states={AWAITING_BROADCASTMSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_msg_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ------------------------------
# Main Entry Point
# ------------------------------

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot...")
    application.run_polling()
