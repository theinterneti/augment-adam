#!/usr/bin/env python
"""Agent MCP Example.

This script demonstrates how to create and use MCP agents.

Usage:
    python -m examples.agent_mcp_example [--port PORT]
"""

import argparse
import logging
import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.tools import Tool
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent MCP Example",
    description="Example of MCP agents",
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


# Example tool
class CalculatorTool(Tool):
    """Calculator tool."""
    
    def __init__(self):
        """Initialize the Calculator tool."""
        super().__init__(
            name="calculator",
            description="Perform basic arithmetic calculations",
            parameters={
                "expression": {
                    "type": "str",
                    "description": "The arithmetic expression to evaluate",
                    "required": True
                }
            }
        )
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """Execute the calculator tool.
        
        Args:
            expression: The arithmetic expression to evaluate
            
        Returns:
            The result of the calculation
        """
        try:
            # Evaluate the expression
            result = eval(expression)
            
            return {
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression
            }


# Create agents
def create_mcp_agent():
    """Create an MCP agent."""
    # Get optimal settings for small_context model
    settings = get_optimal_model_settings("huggingface", "small_context")
    
    # Create model
    model = create_model(
        model_type="huggingface",
        model_size="small_context",
        **settings
    )
    
    # Create calculator tool
    calculator_tool = CalculatorTool()
    
    # Create MCP agent
    agent = create_agent(
        agent_type="mcp",
        name="Calculator Agent",
        description="An agent that can perform calculations",
        model=model,
        tools=[calculator_tool],
        output_format="json",
        strict_output=True
    )
    
    return agent


def create_worker_agent():
    """Create a worker agent."""
    # Get optimal settings for small_context model
    settings = get_optimal_model_settings("huggingface", "small_context")
    
    # Create model
    model = create_model(
        model_type="huggingface",
        model_size="small_context",
        **settings
    )
    
    # Create calculator tool
    calculator_tool = CalculatorTool()
    
    # Create worker agent
    agent = create_agent(
        agent_type="worker",
        name="Calculator Worker",
        description="A worker agent that can perform calculations",
        model=model,
        tools=[calculator_tool],
        output_format="json",
        strict_output=True,
        max_concurrent_tasks=3
    )
    
    return agent


# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Agent MCP Example",
        "version": "0.1.0",
        "description": "Example of MCP agents"
    }


@app.get("/agents")
async def list_agents():
    """List all agents."""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": agent.name,
                "type": agent.__class__.__name__,
                "description": agent.description
            }
            for agent_id, agent in agent_registry.items()
        ]
    }


@app.post("/agents/{agent_id}/process")
async def process_input(agent_id: str, request: Request):
    """Process input with an agent.
    
    Args:
        agent_id: ID of the agent
        request: Request object
        
    Returns:
        Agent response
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Parse request
    data = await request.json()
    user_input = data.get("input")
    context = data.get("context")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing input")
    
    # Process input
    if hasattr(agent, "process_async"):
        result = await agent.process_async(user_input, context)
    else:
        result = agent.process(user_input, context)
    
    return result


@app.post("/agents/{agent_id}/submit_task")
async def submit_task(agent_id: str, request: Request):
    """Submit a task to a worker agent.
    
    Args:
        agent_id: ID of the agent
        request: Request object
        
    Returns:
        Task ID
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Check if agent is a worker
    if not hasattr(agent, "submit_task"):
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} is not a worker agent")
    
    # Parse request
    data = await request.json()
    user_input = data.get("input")
    context = data.get("context")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing input")
    
    # Submit task
    task_id = await agent.submit_task(user_input, context)
    
    return {
        "task_id": task_id
    }


@app.get("/agents/{agent_id}/tasks/{task_id}")
async def get_task_status(agent_id: str, task_id: str):
    """Get the status of a task.
    
    Args:
        agent_id: ID of the agent
        task_id: ID of the task
        
    Returns:
        Task status
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Check if agent is a worker
    if not hasattr(agent, "get_task_status"):
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} is not a worker agent")
    
    # Get task status
    status = agent.get_task_status(task_id)
    
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return status


@app.get("/agents/{agent_id}/tasks")
async def get_all_tasks(agent_id: str):
    """Get all tasks for a worker agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        All tasks
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Check if agent is a worker
    if not hasattr(agent, "get_all_tasks"):
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} is not a worker agent")
    
    # Get all tasks
    tasks = agent.get_all_tasks()
    
    return {
        "tasks": tasks
    }


@app.post("/agents/{agent_id}/tools/{tool_name}")
async def execute_tool(agent_id: str, tool_name: str, request: Request):
    """Execute a tool directly.
    
    Args:
        agent_id: ID of the agent
        tool_name: Name of the tool
        request: Request object
        
    Returns:
        Tool result
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Get agent
    agent = agent_registry[agent_id]
    
    # Get tool
    tool = None
    for t in agent.tools:
        if t.name == tool_name:
            tool = t
            break
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    # Parse request
    data = await request.json()
    
    # Execute tool
    try:
        result = tool.execute(**data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Create agents on startup
@app.on_event("startup")
async def startup_event():
    """Create agents on startup."""
    try:
        # Create MCP agent
        mcp_agent = create_mcp_agent()
        agent_registry["mcp_agent"] = mcp_agent
        
        # Create worker agent
        worker_agent = create_worker_agent()
        agent_registry["worker_agent"] = worker_agent
        
        # Start worker agent
        await worker_agent.start()
        
        logger.info("Created agents")
    except Exception as e:
        logger.error(f"Error creating agents: {e}")


# Stop agents on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Stop agents on shutdown."""
    try:
        # Stop worker agent
        for agent_id, agent in agent_registry.items():
            if hasattr(agent, "stop"):
                await agent.stop()
        
        logger.info("Stopped agents")
    except Exception as e:
        logger.error(f"Error stopping agents: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Agent MCP Example")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Agent MCP Example on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
