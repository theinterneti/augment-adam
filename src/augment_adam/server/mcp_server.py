"""
MCP Server implementation for Augment Adam.

This module provides a FastAPI-based MCP server implementation that can be used
to expose Augment Adam functionality to VS Code and other MCP clients.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)

class MCPTool(BaseModel):
    """Model for an MCP tool."""
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    returns: Dict[str, Any] = Field(default_factory=dict, description="Return type for the tool")

class MCPToolRequest(BaseModel):
    """Model for an MCP tool request."""
    name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool call")

class MCPToolResponse(BaseModel):
    """Model for an MCP tool response."""
    result: Any = Field(..., description="Result of the tool call")
    error: Optional[str] = Field(None, description="Error message if the tool call failed")

class MCPServer:
    """MCP Server implementation for Augment Adam."""

    def __init__(self, app: FastAPI):
        """Initialize the MCP server.
        
        Args:
            app: FastAPI application to mount the MCP server on
        """
        self.app = app
        self.router = APIRouter(prefix="/mcp", tags=["MCP"])
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: Dict[str, MCPTool] = {}
        
        # Set up CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Set up routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up the MCP routes."""
        
        @self.router.get("/tools")
        async def get_tools() -> List[MCPTool]:
            """Get the list of available tools."""
            return list(self.tool_descriptions.values())
        
        @self.router.post("/call")
        async def call_tool(request: MCPToolRequest) -> MCPToolResponse:
            """Call a tool."""
            tool_name = request.name
            
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            try:
                tool_func = self.tools[tool_name]
                start_time = time.time()
                
                # Call the tool function
                if callable(tool_func):
                    result = await tool_func(**request.parameters)
                    
                end_time = time.time()
                logger.info(f"Tool '{tool_name}' called in {end_time - start_time:.2f}s")
                
                return MCPToolResponse(result=result)
            except Exception as e:
                logger.exception(f"Error calling tool '{tool_name}': {e}")
                return MCPToolResponse(result=None, error=str(e))
        
        @self.router.get("/connection")
        async def check_connection():
            """Check if the MCP server is running."""
            return {"status": "connected"}
    
    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict[str, Any] = None, returns: Dict[str, Any] = None):
        """Register a tool with the MCP server.
        
        Args:
            name: Name of the tool
            func: Function to call when the tool is invoked
            description: Description of the tool
            parameters: Parameters for the tool
            returns: Return type for the tool
        """
        if parameters is None:
            parameters = {}
        
        if returns is None:
            returns = {}
        
        self.tools[name] = func
        self.tool_descriptions[name] = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            returns=returns
        )
        
        logger.info(f"Registered tool '{name}'")
    
    def mount(self):
        """Mount the MCP server on the FastAPI app."""
        self.app.include_router(self.router)
        logger.info("MCP server mounted")

# Convenience function to create an MCP server
def create_mcp_server(app: FastAPI) -> MCPServer:
    """Create an MCP server.
    
    Args:
        app: FastAPI application to mount the MCP server on
        
    Returns:
        MCPServer instance
    """
    server = MCPServer(app)
    server.mount()
    return server
