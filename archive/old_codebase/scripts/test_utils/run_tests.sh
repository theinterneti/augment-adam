#!/bin/bash
# Run tests using the test generator

set -e  # Exit on error

echo "Running tests..."

# Run tests using the test generator
docker-compose -f docker-compose.test-gen.yml run dukat-test-generator \
  python -m scripts.auto_test_generator \
  --project-path /project \
  --config /app/config/project_config.yml \
  --project dukat \
  --output-dir /app/test_results

echo "Tests complete!"
