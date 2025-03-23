import os
import pika
import json
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables for Supabase credentials
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# RabbitMQ connection settings
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "park_topic"
exchange_type = "topic"

# Pre-existing queues
queues = {
    "Error": "*.error",
    "Access": "*.access"
}

# Define API URLs for logging
log_URL = "http://127.0.0.1:8084/accesslogs"
error_URL = "http://127.0.0.1:8078/error"

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
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))
    channel = connection.channel()

    # Declare the exchange (ensure it exists)
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

    # Bind the existing queues to the routing keys
    for queue, routing_key in queues.items():
        channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_key)
        print(f"Listening for messages in queue '{queue}' with routing key: {routing_key}")

    # Start consuming messages from both queues
    for queue in queues.keys():
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print("Waiting for messages...")
    channel.start_consuming()

# Main execution
if __name__ == '__main__':
    try:
        start_rabbitmq_consumer()
    except Exception as e:
        print(f"Error: {e}")