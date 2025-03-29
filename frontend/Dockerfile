# Use Node.js base image
FROM node:18-alpine

# Install http-server globally
RUN npm install -g http-server

# Set working directory
WORKDIR /app

# Correct path to frontend code
COPY ./frontend ./frontend

# Expose port
EXPOSE 8100

# Start the server
CMD [ "http-server", "./frontend", "-p", "8100"]
