"""Main entry point for the MCP-enabled context engine API."""

import os
import uvicorn
from mcp_context_engine.api.app import app

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8080"))
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)
