#!/usr/bin/env python3

import time
import pika
import os
import json
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables for Supabase credentials
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# RabbitMQ connection details
amqp_host = "rabbitmq"  # This should match your service name in docker-compose
amqp_port = 5672
exchange_name = "park_topic"
exchange_type = "topic"

queues = {
    "Error": "*.error",
    "Access": "*.access"
}

# API URLs for logging
log_URL = os.getenv('ACCESS_LOGS_URL')
error_URL = os.getenv('ERROR_URL')

# Connect to RabbitMQ
def connect_to_rabbitmq():
    for i in range(5):  # Retry up to 5 times
        try:
            print(f"Attempt {i+1}: Connecting to RabbitMQ at {amqp_host}:{amqp_port}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=amqp_host, port=amqp_port, heartbeat=300, blocked_connection_timeout=300)
            )
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Failed to connect to RabbitMQ after multiple attempts")

# Declare exchange and queues
def setup_rabbitmq():
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Declare Exchange
    print(f"Declaring exchange: {exchange_name}")
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

    # Declare and bind Queues
    for queue, routing_key in queues.items():
        print(f"Declaring queue: {queue}")
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_key)
    
    print("RabbitMQ setup complete!")
    return channel, connection

# Callback function to process messages
def callback(channel, method, properties, body):
    try:
        message = json.loads(body)
        routing_key = method.routing_key  # Get actual routing key
        print(f"Received message: {message} from {routing_key}")

        # Determine log destination
        if routing_key.endswith(".error"):
            url = error_URL
            log_type = "Error"
        elif routing_key.endswith(".access"):
            url = log_URL
            log_type = "Access"
        else:
            print(f"Unknown routing key: {routing_key}")
            return

        # Send log to API
        response = requests.post(url, json=message)
        if response.status_code == 201:
            print(f"{log_type} log added successfully.")
        else:
            print(f"Failed to log {log_type}: {response.text}")

    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Message content: {body}")

# Function to start the RabbitMQ consumer
def start_rabbitmq_consumer():
    channel, connection = setup_rabbitmq()

    # Start consuming messages from both queues
    for queue in queues.keys():
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        print(f"Listening for messages in queue '{queue}' with routing key: {queues[queue]}")

    print("Waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted, closing connection.")
    finally:
        connection.close()

if __name__ == "__main__":
    setup_rabbitmq()  # Set up RabbitMQ
    start_rabbitmq_consumer()  # Start consuming messages