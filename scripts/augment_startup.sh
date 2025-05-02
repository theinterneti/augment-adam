#!/bin/bash
# Augment Assistant Startup Script
# This script gathers useful information about the project environment
# to help the AI assistant provide better assistance

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== AUGMENT ASSISTANT STARTUP INFORMATION ==========${NC}"
echo ""

# Project structure information
echo -e "${GREEN}📁 PROJECT STRUCTURE${NC}"
echo "-------------------"
echo "Main directories:"
find /workspace -maxdepth 2 -type d | grep -v "__pycache__" | sort | sed 's/^/  /'
echo ""

# Git information
echo -e "${GREEN}🔄 GIT STATUS${NC}"
echo "------------"
cd /workspace
echo "Current branch:"
git branch --show-current
echo ""
echo "Git status:"
git status --short
echo ""
echo "Recent commits:"
git log --oneline -n 5
echo ""

# Environment information
echo -e "${GREEN}🐍 PYTHON ENVIRONMENT${NC}"
echo "-------------------"
echo "Python version:"
python --version
echo ""

if [ -f "/workspace/pyproject.toml" ]; then
  echo -e "${GREEN}📦 DEPENDENCIES (from pyproject.toml)${NC}"
  echo "-----------------------------------"
  grep -A 50 "\[tool.poetry.dependencies\]" /workspace/pyproject.toml | grep -v "\[tool.poetry" | grep -B 50 -m 1 "\[" | grep -v "\[" | sed 's/^/  /'
  echo ""
fi

# Testing information
echo -e "${GREEN}🧪 TESTING INFORMATION${NC}"
echo "--------------------"
echo "Test files count:"
find /workspace/tests -name "test_*.py" | wc -l
echo ""

# Check for test coverage if pytest-cov is installed
if python -c "import pytest_cov" 2>/dev/null; then
  echo -e "${YELLOW}Test Coverage:${NC}"
  cd /workspace && python -m pytest --cov=src --cov-report=term-missing:skip-covered --cov-report=json -xvs tests/unit/memory/vector/test_base.py 2>/dev/null | grep -E "TOTAL|^src" | head -n 10 || echo "  No coverage data available"
  echo ""
fi

# Check for failing tests
echo -e "${YELLOW}Recent Failing Tests:${NC}"
cd /workspace && python -m pytest tests/unit/memory/vector/test_base.py -v 2>&1 | grep -E "FAILED|ERROR" | head -n 5 || echo "  No recent test failures found"
echo ""

# Show Python path
echo -e "${YELLOW}Python Path:${NC}"
python -c "import sys; print('\n'.join(sys.path))" | grep -E "workspace|site-packages" | sed 's/^/  /'
echo ""

# Show recently modified files
echo -e "${YELLOW}Recently Modified Files:${NC}"
find /workspace -type f -name "*.py" -mtime -7 | grep -v "__pycache__" | sort | head -n 10 | sed 's/^/  /'
echo ""

# Display TASKS files
echo -e "${GREEN}📋 TASKS FILES${NC}"
echo "------------"
find /workspace -name "TASKS.md" -o -name "TASKS" | while read file; do
  echo "File: $file"
  echo "---"
  cat "$file" | head -n 20
  echo "..."
  echo ""
done

# Resource information
echo -e "${GREEN}💻 SYSTEM RESOURCES${NC}"
echo "-----------------"
echo "Disk space:"
df -h | grep -E "Filesystem|/$"
echo ""
echo "Memory usage:"
free -h
echo ""

# Display information about the background test service
echo -e "${GREEN}🧪 BACKGROUND TEST SERVICE${NC}"
echo "------------------------"
echo "The background test service automatically generates and runs tests when code changes."
echo "To start the background test service, run:"
echo "  ./scripts/run_background_tests.sh"
echo ""
echo "To set up Hugging Face models for test generation, run:"
echo "  ./scripts/setup_huggingface_models.sh"
echo ""
echo "The test dashboard is available at:"
echo "  http://localhost:8080"
echo ""

echo -e "${BLUE}========== END OF STARTUP INFORMATION ==========${NC}"
