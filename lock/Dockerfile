# RIP cannot create Image for now
# Dahai will work his magic

# Set the base image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the global requirements.txt from the root into the container
COPY ../requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY ./lock /app/lock

# Expose the port the app runs on
EXPOSE 8079

# Run the application
CMD ["python", "./lock/lock.py"]