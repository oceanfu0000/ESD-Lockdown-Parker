#!/usr/bin/env python3
"""
A standalone script to create exchanges and queues on RabbitMQ.

This script connects to a RabbitMQ broker, declares an exchange, and creates queues
with specified routing keys, binding them to the declared exchange.
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
    """
    Connect to RabbitMQ and declare an exchange.

    This function establishes a connection to a RabbitMQ broker using the provided
    hostname and port. It then declares an exchange with the specified name and type.

    Args:
        hostname (str): The hostname of the RabbitMQ broker.
        port (int): The port number on which the RabbitMQ broker is listening.
        exchange_name (str): The name of the exchange to declare.
        exchange_type (str): The type of the exchange (e.g., 'topic').

    Returns:
        pika.adapters.blocking_connection.BlockingChannel: A channel to interact with RabbitMQ.

    Raises:
        Exception: If connection fails or the exchange cannot be declared.
    """
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
    """
    Declare a queue and bind it to an exchange with a specific routing key.

    This function declares a durable queue and binds it to a given exchange using the
    provided routing key.

    Args:
        channel (pika.adapters.blocking_connection.BlockingChannel): The channel connected to RabbitMQ.
        exchange_name (str): The name of the exchange to bind the queue to.
        queue_name (str): The name of the queue to declare.
        routing_key (str): The routing key used for binding the queue.

    Raises:
        Exception: If the queue declaration or binding fails.
    """
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
    """
    Main execution block.

    This block connects to the RabbitMQ broker, declares the exchange, and creates/binds the queues.
    It catches exceptions that may occur during the setup process.
    """
    try:
        channel = create_exchange(AMQP_HOST, AMQP_PORT, EXCHANGE_NAME, EXCHANGE_TYPE)

        for q in QUEUES:
            create_queue(channel, EXCHANGE_NAME, q["name"], q["routing_key"])

        print("✅ RabbitMQ setup completed successfully.")

    except Exception as final_error:
        print(f"🔥 Setup failed: {final_error}")
