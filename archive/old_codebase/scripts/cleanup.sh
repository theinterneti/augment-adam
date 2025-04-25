#!/bin/bash
# Clean up the Dukat environment

echo "Cleaning up Dukat environment..."

# Stop and remove containers
docker-compose down
docker-compose -f docker-compose.test-gen.yml down

echo "Cleanup complete!"
