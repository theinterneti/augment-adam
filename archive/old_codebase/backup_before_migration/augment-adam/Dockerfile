# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set environment variables for pip cache
ENV PIP_CACHE_DIR=/root/.cache/pip
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Builder stage: install dependencies in a venv
FROM base AS builder

# Install system dependencies (if needed for common Python packages)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better cache usage
COPY --link requirements.txt ./

# Create venv and install dependencies
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    python -m venv $VIRTUAL_ENV && \
    . $VIRTUAL_ENV/bin/activate && \
    pip install --upgrade pip && \
    pip install --requirement requirements.txt

# Copy the rest of the application code
COPY --link augment_adam ./augment_adam
COPY --link augment-adam ./augment-adam
COPY --link setup.py ./
COPY --link setup.cfg ./

# Install the package in editable mode (if needed for dev, otherwise regular install)
RUN . $VIRTUAL_ENV/bin/activate && \
    pip install --no-deps --editable .

# Final stage: minimal runtime image
FROM base AS final

# Create a non-root user
RUN useradd -m augmentadam
USER augmentadam

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy only the necessary source code and config
COPY --from=builder /app/augment_adam ./augment_adam
COPY --from=builder /app/augment-adam ./augment-adam
COPY --from=builder /app/setup.py ./
COPY --from=builder /app/setup.cfg ./

# Optionally copy global/user settings if needed at runtime (not secrets)
COPY --from=builder /app/augment-adam/global_settings.json ./augment-adam/global_settings.json
COPY --from=builder /app/augment-adam/user_settings.json ./augment-adam/user_settings.json

# Expose FastAPI default port
EXPOSE 8000

# Entrypoint: run the FastAPI server
CMD ["python", "-m", "augment_adam.server"]
