import os
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackContext,
    Application,
    ConversationHandler,
    filters
)
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from invokes import invoke_http

# Define states for conversation
AWAITING_OTP, AWAITING_STAFFPASSWORD, AWAITING_BROADCASTMSG = range(3)

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TOKEN")
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
WEBHOOK_URL = "https://telegram.esdlockdownparker.org/telegramservice/"
GOOGLE_APPLICATION_CREDENTIALS = "telegramservice/esdlocking.json"

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

staff_URL = "http://127.0.0.1:8083/staff"
guest_URL = "http://127.0.0.1:8082/guest"

# Command Handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to the ESD Lockdown Parker Bot! If you need help with the commands, type /help."
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

async def check_balance(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    response = invoke_http(f"{guest_URL}/wallet/{chat_id}", method="GET")
    if response.get("code", 200) == 200:
        balance = response["wallet"]
        await update.message.reply_text(f"Your balance is: {balance}")
    else:
        await update.message.reply_text("Unable to retrieve balance. Please try again later. Make sure you logined.")
    return ConversationHandler.END

async def otp_received(update: Update, context: CallbackContext):
    # print("OTP received")
    otp = update.message.text.strip()
    response = invoke_http(f"{guest_URL}/validate/{otp}", method="GET")
    if response.get("code", 200) == 200:
        chat_id = update.message.chat_id
        response = invoke_http(
            f"{guest_URL}/update_chat_id_by_otp", method="PUT", json={"otp": otp, "chat_id": chat_id}
        )
        if response.get("code", 200) == 200:
            await update.message.reply_text("Login successful!")
        else:
            await update.message.reply_text("Invalid OTP. Please try again.")
    return ConversationHandler.END

async def password_received(update: Update, context: CallbackContext):
    password = update.message.text.strip()
    teleHandler = update.message.chat.username
    chat_id = update.message.chat_id
    response = invoke_http(
        f"{staff_URL}/update_chat_id_by_tele_password", method="PUT",
        json={"password": password, "staff_tele": teleHandler, "chat_id": chat_id}
    )
    if response.get("code", 200) == 200:
        await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text("Invalid OTP. Please try again.")
    return ConversationHandler.END

async def broadcast_msg_received(update: Update, context: CallbackContext):
    msg = update.message.text.strip()
    chat_id = update.message.chat_id
    response = invoke_http(f"{staff_URL}/validate_chat_id/{chat_id}", method="GET")
    if response.get("code", 200) == 200:
        response = invoke_http(f"{guest_URL}/valid_chat_ids", method="GET")
        if response.get("code", 200) == 200:
            for chat_ids in response["chat_ids"]:
                bot.send_message(chat_id=chat_ids, text=msg)
            await update.message.reply_text("Broadcast message sent successfully!")
        else:
            await update.message.reply_text("Unable to retrieve guests. Please try again later.")
    else:
        await update.message.reply_text("Invalid staff login. Please try again.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("No Response. Please try again.")
    return ConversationHandler.END

def detect_intent_from_dialogflow(session_id, text):
    url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/{session_id}:detectIntent"
    headers = {
        "Authorization": f"Bearer {get_google_access_token()}",
        "Content-Type": "application/json",
    }
    payload = {"query_input": {"text": {"text": text, "language_code": "en"}}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_google_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.message.chat_id

    response = detect_intent_from_dialogflow(chat_id, user_message)
    # print(response)
    if response:
        fulfillment_text = response["queryResult"].get("fulfillmentText")
        if fulfillment_text:
            await update.message.reply_text(fulfillment_text)
        else:
            await update.message.reply_text("I'm not sure how to respond to that.")
    else:
        await update.message.reply_text("Error processing your request. Please try again later.")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("checkBalance", check_balance))
application.add_handler(CommandHandler("help", help))

login_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("login", login)],
    states={
        AWAITING_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, otp_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

stafflogin_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("stafflogin", staff_login)],
    states={
        AWAITING_STAFFPASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

broadcast_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("broadcast", broadcast)],
    states={
        AWAITING_BROADCASTMSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_msg_received)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(login_conv_handler)
application.add_handler(stafflogin_conv_handler)
application.add_handler(broadcast_conv_handler)

# Add general handler last so it doesn't override conversation handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Starting Telegram Bot...")
    application.run_polling()