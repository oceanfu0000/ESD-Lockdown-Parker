# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's caching
COPY ../requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./emailservice /app/emailservice

# Expose the port that the Flask app runs on
EXPOSE 8088

# Run the Flask app
CMD ["python", "./emailservice/emailservice.py"]