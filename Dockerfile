# Start with the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /code/app
COPY ./alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations

# The command to run the application will be specified in docker-compose.yml
# This allows for flexibility (e.g., running tests or the server)