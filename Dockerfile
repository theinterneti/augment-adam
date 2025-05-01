FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create cache directory
RUN mkdir -p /cache && chmod 777 /cache

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Install the package in development mode
RUN pip install -e .

# Expose port for API
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV AUGMENT_CACHE_DIR=/cache

# Run the application
CMD ["python", "-m", "augment_adam.server"]
