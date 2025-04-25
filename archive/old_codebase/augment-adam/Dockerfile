# syntax=docker/dockerfile:1

FROM python:3.10-slim AS base

# Set up pip cache directory for all stages
ENV PIP_CACHE_DIR=/root/.cache/pip

# Create a non-root user for security
RUN addgroup --system augmentadam && adduser --system --ingroup augmentadam augmentadam

# Builder stage: install dependencies and build the virtual environment
FROM base AS builder
WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better cache utilization
COPY --link requirements.txt ./

# Create virtual environment and install dependencies using pip cache
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    python -m venv .venv && \
    .venv/bin/pip install -r requirements.txt

# Copy the rest of the application code
COPY --link . .

# Install the package in editable mode (development mode)
RUN .venv/bin/pip install -e .

# Final stage: minimal runtime image
FROM base AS final
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
# Copy application code from builder
COPY --from=builder /app /app

# Create cache directory and set permissions
RUN mkdir -p /cache && chmod 777 /cache

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV AUGMENT_CACHE_DIR=/cache

# Use non-root user
USER augmentadam

# Expose FastAPI port
EXPOSE 8000

# Entrypoint: run the FastAPI server
CMD ["python", "-m", "augment_adam.server"]
