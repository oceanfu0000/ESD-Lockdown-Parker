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
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Attempt {attempt}: Connecting to RabbitMQ at {self.hostname}:{self.port}...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.hostname,
                        port=self.port,
                        heartbeat=300,
                        blocked_connection_timeout=300,
                    )
                )
                self.channel = self.connection.channel()

                # Verify exchange exists
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type=self.exchange_type,
                    passive=True  # Only check if exchange exists, do not create
                )

                print("✅ Connected to RabbitMQ.")
                return

            except pika.exceptions.ChannelClosedByBroker as e:
                raise Exception(f"❌ Exchange '{self.exchange_name}' of type '{self.exchange_type}' does not exist.") from e

            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ Connection failed: {e}. Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

        raise Exception(f"❌ Failed to connect after {self.max_retries} retries.")

    def close(self):
        """Closes the RabbitMQ connection gracefully."""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            print("🔌 Connection to RabbitMQ closed.")
        except Exception as e:
            print(f"⚠️ Error closing RabbitMQ connection: {e}")

    def is_connection_open(self):
        """Checks if the connection is alive."""
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

                print(f"📥 Listening on queue: {queue_name}")
                self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=callback,
                    auto_ack=True
                )
                self.channel.start_consuming()

            except pika.exceptions.ChannelClosedByBroker as e:
                raise Exception(f"❌ Queue '{queue_name}' not found.") from e

            except pika.exceptions.ConnectionClosedByBroker:
                print("⚠️ Connection closed by broker. Reconnecting...")
                time.sleep(self.retry_interval)
                continue

            except pika.exceptions.AMQPConnectionError:
                print("⚠️ AMQP connection error. Reconnecting...")
                time.sleep(self.retry_interval)
                continue

            except KeyboardInterrupt:
                print("🛑 Interrupted by user.")
                self.close()
                break

            except Exception as e:
                print(f"❌ Unexpected error during consuming: {e}")
                self.close()
                break
