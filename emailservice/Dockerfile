# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app

# Copy the credentials.json and token.json into the container
COPY ./emailservice /app/emailservice
COPY ../requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app runs on
EXPOSE 8088

# Run the Flask app
CMD ["python", "./emailservice/emailservice.py"]