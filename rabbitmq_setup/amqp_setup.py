#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika

# Configuration
AMQP_HOST = "localhost"
AMQP_PORT = 5672
EXCHANGE_NAME = "park_topic"
EXCHANGE_TYPE = "topic"

# Queues to bind
QUEUES = [
    {"name": "Error", "routing_key": "error.*"},
    {"name": "Access", "routing_key": "access.*"},
]


def create_exchange(hostname, port, exchange_name, exchange_type):
    try:
        print(f"🔌 Connecting to RabbitMQ broker {hostname}:{port}...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=hostname,
                port=port,
                heartbeat=300,
                blocked_connection_timeout=300,
            )
        )
        print("✅ Connected")

        channel = connection.channel()

        print(f"📦 Declaring exchange: {exchange_name}")
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        return channel

    except Exception as e:
        print(f"❌ Failed to connect or declare exchange: {e}")
        raise


def create_queue(channel, exchange_name, queue_name, routing_key):
    try:
        print(f"📬 Declaring queue: {queue_name}")
        channel.queue_declare(queue=queue_name, durable=True)

        print(f"🔗 Binding queue '{queue_name}' to exchange '{exchange_name}' with routing key '{routing_key}'")
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
    except Exception as e:
        print(f"❌ Failed to create or bind queue '{queue_name}': {e}")
        raise


if __name__ == "__main__":
    try:
        channel = create_exchange(AMQP_HOST, AMQP_PORT, EXCHANGE_NAME, EXCHANGE_TYPE)

        for q in QUEUES:
            create_queue(channel, EXCHANGE_NAME, q["name"], q["routing_key"])

        print("✅ RabbitMQ setup completed successfully.")

    except Exception as final_error:
        print(f"🔥 Setup failed: {final_error}")
