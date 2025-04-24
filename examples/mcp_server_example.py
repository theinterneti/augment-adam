#!/usr/bin/env python
"""MCP Server Example.

This script demonstrates how to create an MCP server with agents.

Usage:
    python -m examples.mcp_server_example [--port PORT]
"""

import logging
import argparse
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MCP Server Example",
    description="Example of MCP server with agents",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent registry
agent_registry = {}


def create_mcp_agent(model_type="huggingface", model_size="small_context"):
    """Create an MCP agent."""
    # Get optimal settings
    settings = get_optimal_model_settings(model_type, model_size)
    
    # Create model
    model = create_model(
        model_type=model_type,
        model_size=model_size,
        **settings
    )
    
    # Create MCP agent
    system_prompt = """You are an MCP agent designed to be deployed as a server.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.

IMPORTANT: You must respond in valid JSON format with the following structure:
{
    "response": "Your response text here",
    "confidence": 0.9,
    "sources": []
}
"""
    
    agent = create_agent(
        agent_type="mcp",
        name="MCP Agent",
        description="An MCP agent for server deployment",
        model=model,
        system_prompt=system_prompt,
        output_format="json",
        strict_output=True
    )
    
    return agent


# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "MCP Server Example",
        "version": "0.1.0",
        "description": "Example of MCP server with agents"
    }


@app.get("/agents")
async def list_agents():
    """List all agents."""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": agent.name,
                "description": agent.description
            }
            for agent_id, agent in agent_registry.items()
        ]
    }


@app.post("/agents/{agent_id}/process")
async def process_input(agent_id: str, request: Request):
    """Process input with an agent."""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Parse request
    data = await request.json()
    user_input = data.get("input")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing input")
    
    # Process input
    result = agent.process(user_input)
    
    return result


@app.get("/schema")
async def get_schema():
    """Get the MCP schema."""
    if "mcp_agent" in agent_registry:
        agent = agent_registry["mcp_agent"]
        if hasattr(agent, "get_mcp_schema"):
            return agent.get_mcp_schema()
    
    return {
        "error": "MCP agent not found or does not support schema"
    }


# Create agents on startup
@app.on_event("startup")
async def startup_event():
    """Create agents on startup."""
    try:
        # Create MCP agent
        mcp_agent = create_mcp_agent()
        agent_registry["mcp_agent"] = mcp_agent
        
        logger.info("Created MCP agent")
    except Exception as e:
        logger.error(f"Error creating agents: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="MCP Server Example")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting MCP Server Example on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
