#!/bin/bash
# Script to manage the MCP Context Engine services

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MASTER_SCRIPT="${SCRIPT_DIR}/manage_services.sh"

# Check if the master script exists
if [ ! -f "$MASTER_SCRIPT" ]; then
    echo "Error: Master service management script not found at ${MASTER_SCRIPT}"
    exit 1
fi

# Function to display usage information
usage() {
    echo "MCP Context Engine Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all MCP Context Engine services"
    echo "  stop        - Stop all MCP Context Engine services"
    echo "  restart     - Restart all MCP Context Engine services"
    echo "  status      - Check the status of all MCP Context Engine services"
    echo "  logs        - View logs from all MCP Context Engine services"
    echo "  logs [service] - View logs for a specific service"
    echo "  build       - Build all MCP Context Engine services"
    echo "  clean       - Remove all MCP Context Engine containers and volumes"
    echo "  test        - Run tests for the MCP Context Engine"
    echo "  help        - Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs mcp-context-engine"
}

# Process command line arguments
case "$1" in
    start|stop|restart|status|build|clean)
        "$MASTER_SCRIPT" mcp-context-engine "$1"
        ;;
    logs)
        "$MASTER_SCRIPT" mcp-context-engine logs "$2"
        ;;
    test)
        echo "Running tests for MCP Context Engine..."
        # Add your test commands here
        echo "Tests completed."
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac

exit 0
