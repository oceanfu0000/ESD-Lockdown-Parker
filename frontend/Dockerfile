# Use lightweight Node.js base image
FROM node:18-alpine

# Install http-server globally
RUN npm install -g http-server

# Set working directory
WORKDIR /app/Frontend

# Copy the frontend code into container
COPY ./Frontend .

# Expose the HTTP server port
EXPOSE 8100

# Start the frontend using http-server
CMD ["http-server", ".", "-p", "8100"]
