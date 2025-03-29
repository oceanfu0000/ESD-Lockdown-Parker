#!/usr/bin/env python3

import time
import pika
import os
import json
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# -------------------------------
# Environment & Supabase Setup
# -------------------------------

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# RabbitMQ Configuration
# -------------------------------

AMQP_HOST = "rabbitmq"
AMQP_PORT = 5672
EXCHANGE_NAME = "park_topic"
EXCHANGE_TYPE = "topic"

QUEUES = {
    "Error": "*.error",
    "Access": "*.access",
    "Notification": "payment.notification"
}

# -------------------------------
# External Service URLs
# -------------------------------

LOG_URL = os.getenv("ACCESS_LOGS_URL")
ERROR_URL = os.getenv("ERROR_URL")
EMAIL_URL = os.getenv("EMAIL_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -------------------------------
# Utility: Send Telegram Message
# -------------------------------

def send_message(chat_id, text):
    try:
        response = requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": text})
        response.raise_for_status()
        print("✅ Telegram message sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

# -------------------------------
# RabbitMQ Setup
# -------------------------------

def connect_to_rabbitmq():
    for i in range(5):
        try:
            print(f"Attempt {i+1}: Connecting to RabbitMQ at {AMQP_HOST}:{AMQP_PORT}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=AMQP_HOST,
                    port=AMQP_PORT,
                    heartbeat=300,
                    blocked_connection_timeout=300
                )
            )
            print("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("⏳ RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("❌ Failed to connect to RabbitMQ after multiple attempts")

def setup_rabbitmq():
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()

        print(f"📦 Declaring exchange: {EXCHANGE_NAME}")
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)

        for queue, routing_key in QUEUES.items():
            print(f"📬 Declaring queue: {queue}")
            channel.queue_declare(queue=queue, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue, routing_key=routing_key)

        print("✅ RabbitMQ setup complete")
        return channel, connection
    except Exception as e:
        print(f"❌ Failed to set up RabbitMQ: {e}")
        raise

# -------------------------------
# Callback for Received Messages
# -------------------------------

def callback(channel, method, properties, body):
    try:
        message = json.loads(body)
        routing_key = method.routing_key
        print(f"📨 Received from {routing_key}: {message}")

        if routing_key.endswith(".error"):
            log_url = ERROR_URL
            log_type = "Error"

        elif routing_key.endswith(".access"):
            log_url = LOG_URL
            log_type = "Access"

        elif routing_key == "payment.notification":
            guest_id = message.get("guest_id")
            if not guest_id:
                print("⚠️ guest_id missing in message")
                return

            try:
                response = supabase.table("guest").select("*").eq("guest_id", guest_id).execute()
                guest = response.data[0] if response.data else None

                if not guest:
                    print(f"⚠️ Guest not found for ID {guest_id}")
                    return

                chat_id = guest.get("chat_id")
                otp = guest.get("otp")
                email = guest.get("guest_email")

                if chat_id:
                    send_message(chat_id, f"🎫 Your OTP is {otp}! Thanks for purchasing a ticket.")

                if email:
                    try:
                        email_response = requests.post(EMAIL_URL, json={
                            "to": email,
                            "subject": "Ticket Purchase Confirmation",
                            "message": f"Your OTP is {otp}!"
                        })
                        email_response.raise_for_status()
                        print("📧 Email sent successfully.")
                    except Exception as e:
                        print(f"❌ Failed to send email: {e}")

            except Exception as e:
                print(f"❌ Failed to fetch guest from Supabase: {e}")

            return  # No logging for notifications

        else:
            print(f"⚠️ Unknown routing key: {routing_key}")
            return

        # POST log to API
        try:
            api_response = requests.post(log_url, json=message)
            if api_response.status_code == 201:
                print(f"✅ {log_type} log saved.")
            else:
                print(f"❌ Failed to log {log_type}: {api_response.text}")
        except Exception as e:
            print(f"❌ Logging error to {log_url} failed: {e}")

    except Exception as e:
        print(f"🔥 Error processing message: {e}")
        print(f"⚠️ Raw message: {body}")

# -------------------------------
# Start RabbitMQ Consumer
# -------------------------------

def start_rabbitmq_consumer():
    try:
        channel, connection = setup_rabbitmq()

        for queue in QUEUES:
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            print(f"🔎 Listening on queue: {queue} ({QUEUES[queue]})")

        print("🚀 Waiting for messages. Press Ctrl+C to stop.")
        channel.start_consuming()

    except KeyboardInterrupt:
        print("🛑 Consumer interrupted. Shutting down.")
    except Exception as e:
        print(f"❌ Consumer error: {e}")
    finally:
        try:
            connection.close()
            print("🔌 Connection closed.")
        except Exception:
            pass

# -------------------------------
# Entrypoint
# -------------------------------

if __name__ == "__main__":
    try:
        start_rabbitmq_consumer()
    except Exception as e:
        print(f"❌ Failed to start consumer: {e}")
