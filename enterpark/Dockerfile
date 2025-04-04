# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's caching
COPY ../requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the RabbitMQClient module
COPY ../RabbitMQClient.py /app/RabbitMQClient.py

# Copy the rest of the application code
COPY ./enterpark /app/enterpark

# Expose the port that the app runs on
EXPOSE 8085

# Run the application
CMD ["python", "./enterpark/enterpark.py"]