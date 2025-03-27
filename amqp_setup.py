#!/usr/bin/env python3

import time
import pika

# RabbitMQ connection details
amqp_host = "rabbitmq"  # This should match your service name in docker-compose
amqp_port = 5672
exchange_name = "park_topic"
exchange_type = "topic"

queues = [
    {"name": "Error", "routing_key": "error.*"},
    {"name": "Access", "routing_key": "access.*"}
]

def connect_to_rabbitmq():
    for i in range(5):  # Retry up to 5 times
        try:
            print(f"Attempt {i+1}: Connecting to RabbitMQ at {amqp_host}:{amqp_port}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=amqp_host, port=amqp_port, heartbeat=300,blocked_connection_timeout=300)
            )
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Failed to connect to RabbitMQ after multiple attempts")

def setup_rabbitmq():
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Declare Exchange
    print(f"Declaring exchange: {exchange_name}")
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

    # Declare and bind Queues
    for queue in queues:
        print(f"Declaring queue: {queue['name']}")
        channel.queue_declare(queue=queue["name"], durable=True)
        channel.queue_bind(exchange=exchange_name, queue=queue["name"], routing_key=queue["routing_key"])
    
    print("RabbitMQ setup complete!")
    connection.close()

if __name__ == "__main__":
    setup_rabbitmq()