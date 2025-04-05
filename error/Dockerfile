# Set the base image
FROM python:3.13-slim

# Install tzdata to configure timezone
RUN apt-get update && apt-get install -y tzdata

# Set the timezone to Singapore
RUN ln -fs /usr/share/zoneinfo/Asia/Singapore /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Set the working directory
WORKDIR /app

# Copy the global requirements.txt from the root into the container
COPY ../requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY ./error /app/error

# Expose the port the app runs on
EXPOSE 8078

# Run the application
CMD ["python", "./error/error.py"]