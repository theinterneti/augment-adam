FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements-mcp.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Copy application code
COPY mcp_context_engine /app/mcp_context_engine

# Command to run the application
CMD ["python", "-m", "mcp_context_engine.app"]
