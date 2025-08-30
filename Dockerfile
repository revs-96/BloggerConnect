# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies for python-magic and psycopg2
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=BloggerConnect/main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose Flask port
EXPOSE 5000

# Run the Flask application with gunicorn for production
# Add the current directory to Python path to resolve import issues
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--pythonpath", ".", "BloggerConnect.main:app"]
