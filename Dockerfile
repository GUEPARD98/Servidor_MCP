# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DICE_ROLLER_LOG_LEVEL=INFO

# Set the working directory in the container
WORKDIR /app

# Create a non-root user for security
RUN groupadd -r dice && useradd -r -g dice dice

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY server.py .

# Change ownership of the app directory to the dice user
RUN chown -R dice:dice /app

# Switch to non-root user
USER dice

# Create volume for persistent history
VOLUME ["/app/data"]

# Set environment variable for history file location
ENV HISTORY_FILE=/app/data/dice_history.json

# Expose the port (though MCP uses stdio, this is for documentation)
EXPOSE 8000

# Define the command to run the application
CMD ["python", "server.py"]
