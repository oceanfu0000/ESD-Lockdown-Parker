import time
import pika

class RabbitMQClient:
    def __init__(self, hostname, port, exchange_name, exchange_type, max_retries=12, retry_interval=5):
        self.hostname = hostname
        self.port = port
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Establishes a connection to RabbitMQ with retry logic."""
        retries = 0
        while retries < self.max_retries:
            retries += 1
            try:
                print(f"Connecting to AMQP broker {self.hostname}:{self.port}...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.hostname,
                        port=self.port,
                        heartbeat=300,
                        blocked_connection_timeout=300,
                    )
                )
                self.channel = self.connection.channel()
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type=self.exchange_type,
                    passive=True,  # Ensures exchange exists
                )
                print("Connected to RabbitMQ.")
                return
            except pika.exceptions.ChannelClosedByBroker as exception:
                raise Exception(f"{self.exchange_type} exchange {self.exchange_name} not found.") from exception
            except pika.exceptions.AMQPConnectionError as exception:
                print(f"Failed to connect: {exception}. Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)
        raise Exception(f"Max {self.max_retries} retries exceeded.")

    def close(self):
        """Closes the RabbitMQ connection."""
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        print("Connection closed.")

    def is_connection_open(self):
        """Checks if the connection is open."""
        try:
            self.connection.process_data_events()
            return True
        except pika.exceptions.AMQPError:
            return False

    def start_consuming(self, queue_name, callback):
        """Starts consuming messages from a queue."""
        while True:
            try:
                if not self.is_connection_open():
                    self.connect()
                print(f"Consuming from queue: {queue_name}")
                self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
                self.channel.start_consuming()
            except pika.exceptions.ChannelClosedByBroker as exception:
                raise Exception(f"Queue {queue_name} not found.") from exception
            except pika.exceptions.ConnectionClosedByBroker:
                print("Connection lost. Reconnecting...")
                continue
            except KeyboardInterrupt:
                self.close()
                break