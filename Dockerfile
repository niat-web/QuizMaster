
# Use Python 3.14 as the base image
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Display Python logs immediately
ENV PYTHONUNBUFFERED=1

# Copy dependency list first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Flask application port
EXPOSE 5000

# Start Flask, accessible outside the container
CMD ["flask", "--app", "run", "run", "--host=0.0.0.0", "--port=5000"]
