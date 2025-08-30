# syntax=docker/dockerfile:1.4

# Use slim Python image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies
# - libmagic1: for python-magic
# - libpq-dev & gcc: for psycopg2
# - postgresql-client: so wait-for-db.sh can use pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq-dev \
    gcc \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure wait-for-db.sh is executable
RUN chmod +x wait-for-db.sh

# Environment variables for Flask
ENV FLASK_APP=BloggerConnect/main.py \
    FLASK_RUN_HOST=0.0.0.0

# Expose Flask port
EXPOSE 5000

# Start app with wait-for-db to ensure DB is ready
CMD ["./wait-for-db.sh", "db", "gunicorn", "--bind", "0.0.0.0:5000", "--pythonpath", ".", "BloggerConnect.app:app"]
