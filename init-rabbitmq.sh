#!/bin/bash
echo "Waiting for RabbitMQ to be ready..."
sleep 5  # Ensures RabbitMQ is up before running setup

echo "Initializing RabbitMQ exchanges and queues..."
python3 amqp_setup.py  # Runs the Python script to configure RabbitMQ

echo "RabbitMQ setup complete!"