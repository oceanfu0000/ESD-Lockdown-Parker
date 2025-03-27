#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika

amqp_host = "localhost"
amqp_port = 5672
exchange_name1 = "park_topic"
exchange_name2 = "payment_topic"
exchange_type = "topic"

def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Open channel")
    channel = connection.channel()

    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )

    return channel

def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Declare queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)

    print(f"Bind queue '{queue_name}' to exchange '{exchange_name}' with routing key '{routing_key}'")
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

# Create both exchanges
channel1 = create_exchange(amqp_host, amqp_port, exchange_name1, exchange_type)
channel2 = create_exchange(amqp_host, amqp_port, exchange_name2, exchange_type)

# Bind queues to the first exchange (park_topic)
create_queue(channel1, exchange_name1, "Error", "error.*")
create_queue(channel1, exchange_name1, "Access", "access.*")

# Bind queues to the second exchange (payment_topic)
create_queue(channel2, exchange_name2, "PaymentSuccess", "payment.success")
create_queue(channel2, exchange_name2, "PaymentFailure", "payment.failure")

print("Setup completed successfully.")
