FROM python:3.13-slim

WORKDIR /app

COPY init-rabbitmq.sh /app/init-rabbitmq.sh
# Ensure the Python script is copied
COPY amqp_setup.py /app/amqp_setup.py
# Copy the global requirements.txt from the root into the container
COPY ./requirements.txt /app/requirements.txt
# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "-c", "/app/init-rabbitmq.sh"]