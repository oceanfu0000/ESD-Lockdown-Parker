# Set the base image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the global requirements.txt from the root into the container
COPY ../requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the contents of the staff folder into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8089

# Run the application
CMD ["python", "./sendnotification/send_notification.py"]