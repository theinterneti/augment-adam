#!/bin/bash
# Run the background test service
# This script starts the background test service that monitors code changes,
# generates tests, runs tests, and reports results in real-time.

set -e  # Exit on error

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== BACKGROUND TEST SERVICE ==========${NC}"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Check if the required scripts exist
if [ ! -f "scripts/background_test_service.py" ]; then
    echo -e "${RED}Error: Background test service script not found${NC}"
    exit 1
fi

# Create directories
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p logs
mkdir -p reports/tests
mkdir -p templates/dashboard

# Create dashboard templates if they don't exist
if [ ! -f "templates/dashboard/index.html" ]; then
    echo -e "${GREEN}Creating dashboard templates...${NC}"
    python scripts/test_dashboard.py --create-templates
fi

# Start the dashboard server
echo -e "${GREEN}Starting dashboard server...${NC}"
python scripts/test_dashboard.py --host localhost --port 8080 &
DASHBOARD_PID=$!

# Wait for the dashboard server to start
echo -e "${GREEN}Waiting for dashboard server to start...${NC}"
sleep 2

# Start the background test service
echo -e "${GREEN}Starting background test service...${NC}"
python scripts/background_test_service.py --source-dir src/augment_adam --test-dir tests --model-name Qwen/Qwen2-7B-Instruct --verbose

# Clean up
echo -e "${GREEN}Cleaning up...${NC}"
kill $DASHBOARD_PID

echo -e "${BLUE}========== BACKGROUND TEST SERVICE STOPPED ==========${NC}"
echo ""
