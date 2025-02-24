import requests
import os
import logging
import RPi.GPIO as GPIO
import time
from flask import Flask, request


TOKEN = "7795590650:AAG2r2Chj7qMDVUJADTiWlTA6TUlZzHHaDI"
WEBHOOK_URL = "https://c32f-121-7-1-21.ngrok-free.app"

app = Flask(__name__)

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})
    return response.json()

@app.route("/", methods=["POST"])
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
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    print(set_webhook())
    app.run(host="0.0.0.0", port=8080)


#for the lock

relay_pin = 18

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file_path = os.path.join(os.path.dirname(__file__), "logs/lock.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.IN)

@app.route("/open", methods=["GET"])
def open_lock():
    GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.output(relay_pin, False)
    # print("lock opening")
    logger.info("lock opening")

@app.route("/close", methods=["GET"])
def close_lock():
    GPIO.setup(relay_pin, GPIO.IN)
    GPIO.input(relay_pin)
    # print("lock closeing")
    logger.info("lock closeing")
