#!/bin/bash
# Script to set up integration between the devcontainer and MCP Context Engine

set -e

echo "Setting up MCP Context Engine integration..."

# Check if the MCP Context Engine is running
if ! curl -s http://mcp-context-engine:8080/health > /dev/null; then
    echo "MCP Context Engine is not running or not accessible."
    echo "Make sure the MCP Context Engine services are running."
    echo "You can start them with: ./scripts/manage_mcp_context_engine.sh start"
    exit 1
fi

# Set up environment variables for MCP Context Engine
echo "Setting up environment variables..."
export MCP_ENGINE_URL="http://mcp-context-engine:8080"
export MCP_ENGINE_API_KEY="test-api-key"

# Add environment variables to .bashrc for persistence
if ! grep -q "MCP_ENGINE_URL" ~/.bashrc; then
    echo "# MCP Context Engine environment variables" >> ~/.bashrc
    echo "export MCP_ENGINE_URL=\"http://mcp-context-engine:8080\"" >> ~/.bashrc
    echo "export MCP_ENGINE_API_KEY=\"test-api-key\"" >> ~/.bashrc
fi

# Test connection to MCP Context Engine
echo "Testing connection to MCP Context Engine..."
if curl -s -H "Authorization: Bearer $MCP_ENGINE_API_KEY" "$MCP_ENGINE_URL/health" | grep -q "ok"; then
    echo "Connection to MCP Context Engine successful!"
else
    echo "Failed to connect to MCP Context Engine."
    echo "Please check the MCP Context Engine logs for more information."
    exit 1
fi

echo "MCP Context Engine integration setup completed successfully."
