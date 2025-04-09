#!/usr/bin/env python3
"""
A standalone script to consume RabbitMQ messages

This module sets up a RabbitMQ consumer that listens on multiple queues defined by routing keys.
Depending on the message type, it performs various actions such as logging errors, handling access
attempts, and sending notifications via Telegram or email. Environment variables for external services
are loaded using dotenv.

Modules:
    time, pika, os, json, requests: Standard libraries and external dependencies.
    dotenv: To load environment variables.
"""

import time
import pika
import os
import json
import requests
from dotenv import load_dotenv

# -------------------------------
# Environment
# -------------------------------

load_dotenv()

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

LOG_URL = os.getenv("LOGS_URL")
ERROR_URL = os.getenv("ERROR_URL")
EMAIL_URL = os.getenv("EMAIL_URL")
STAFF_URL = os.getenv("STAFF_URL")
GUEST_URL = os.getenv("GUEST_URL")
TELEGRAM_TOKEN = os.getenv("TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -------------------------------
# Utility: Send Telegram Message
# -------------------------------

def send_message(chat_id, text):
    """
    Send a Telegram message using the bot API.

    Args:
        chat_id (str/int): The Telegram chat ID to which the message should be sent.
        text (str): The text message to send.

    Returns:
        None

    Side Effects:
        Prints the status of the Telegram message delivery.
    """
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
    """
    Attempt to connect to the RabbitMQ broker with retries.

    Tries to establish a connection up to 5 times. If RabbitMQ is not ready, it waits 10 seconds
    between attempts.

    Returns:
        pika.BlockingConnection: An active connection to RabbitMQ.

    Raises:
        Exception: If unable to connect after multiple attempts.
    """
    for i in range(5):
        try:
            print(f"Attempt {i+1}: Connecting to RabbitMQ at {AMQP_HOST}:{AMQP_PORT}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=AMQP_HOST,
                    port=AMQP_PORT,
                    heartbeat=0,
                    blocked_connection_timeout=None
                )
            )
            print("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("⏳ RabbitMQ not ready. Retrying in 10 seconds...")
            time.sleep(10)
    raise Exception("❌ Failed to connect to RabbitMQ after multiple attempts")

def setup_rabbitmq():
    """
    Set up RabbitMQ exchange and queues.

    Connects to RabbitMQ, declares the exchange and queues, and binds each queue to the exchange
    using its corresponding routing key.

    Returns:
        tuple: A tuple containing:
            - channel (pika.adapters.blocking_connection.BlockingChannel): The channel for communication.
            - connection (pika.BlockingConnection): The established connection to RabbitMQ.

    Raises:
        Exception: If there is an error during the setup process.
    """
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
    """
    Process incoming messages from RabbitMQ.

    Decodes the JSON message and determines the action based on the routing key:
      - For error messages, it sets the log endpoint to ERROR_URL.
      - For access messages, it may fetch staff details and send Telegram alerts.
      - For payment notifications, it fetches guest information and sends notifications via Telegram
        and email.
      - Logs the message to an external API if applicable.

    Args:
        channel: The RabbitMQ channel.
        method: Delivery method containing routing key details.
        properties: Message properties.
        body (bytes): The raw message body (JSON encoded).

    Returns:
        None

    Side Effects:
        May send Telegram messages, emails, and log data via API.
    """
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
            msg_type = message.get("type")
            user_type = message.get("user_type")
            if user_type == "staff" and msg_type == "Failed":
                staff_id = message.get("user_id")
                try:
                    # Fetch staff name from staff 
                    response = requests.get(f"{STAFF_URL}/{staff_id}")
                    staff = response.json()
                    if response.status_code != 200:
                        print(f"⚠️ Staff not found for ID {staff_id}")
                        return

                    staff_name = staff.get("staff_name")

                    response = requests.get(STAFF_URL)
                    staff_members = response.json()
                    if response.status_code != 200:
                        print("⚠️ Failed to fetch staff members.")
                        return
                    # print(staff_members)
                    for staff_member in staff_members:
                        chat_id = staff_member.get("chat_id")
                        if chat_id:
                            send_message(chat_id, f"❌ {staff_name} has made multiple unsuccessful attempts to access Door 1.")
                        else:
                            print(f"⚠️ No chat_id found for staff member {staff_member}")
        
                except Exception as e:
                    print(f"❌ Failed to fetch staff: {e}")

        elif routing_key == "payment.notification":
            guest_id = message.get("guest_id")

            if not guest_id:
                print("⚠️ guest_id missing in message")
                return

            try:
                response = requests.get(f"{GUEST_URL}/{guest_id}")
                guest = response.json()
                guest = guest.get("guest")

                if response.status_code != 200:
                    print(f"⚠️ Guest not found for ID {guest_id}")
                    return

                chat_id = guest.get("chat_id")
                otp = guest.get("otp")
                email = guest.get("guest_email")
                print(f"📧 Sending OTP {otp} to {email}")

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
                print(f"❌ Failed to fetch guest: {e}")

            return  # No further logging for notifications

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
    """
    Initialize and start the RabbitMQ consumer.

    This function sets up the RabbitMQ exchange and queues, registers the callback for each queue,
    and begins consuming messages. It handles keyboard interrupts and ensures the connection is closed
    upon termination.

    Returns:
        None

    Side Effects:
        Listens indefinitely for incoming messages until interrupted.
    """
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
    """
    Entry point of the script.

    This block starts the RabbitMQ consumer and handles any exceptions that may occur during startup.
    """
    try:
        start_rabbitmq_consumer()
    except Exception as e:
        print(f"❌ Failed to start consumer: {e}")
