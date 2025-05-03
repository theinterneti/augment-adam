#!/bin/bash
# Script to manage the MCP Context Engine services

set -e

# Define the path to the new management script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MASTER_SCRIPT="${SCRIPT_DIR}/docker/scripts/manage_mcp.sh"

# Check if the master script exists
if [ ! -f "$MASTER_SCRIPT" ]; then
    echo "Error: Master MCP management script not found at ${MASTER_SCRIPT}"
    echo "Please make sure the Docker scripts are properly set up."
    exit 1
fi

# Forward all arguments to the master script
"$MASTER_SCRIPT" "$@"
