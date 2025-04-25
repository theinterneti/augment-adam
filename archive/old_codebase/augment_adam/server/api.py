"""FastAPI server for Augment Adam.

This module provides a FastAPI server for Augment Adam, allowing
access to models and agents via a REST API.

Version: 0.1.0
Created: 2025-04-29
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.utils.hardware_optimizer import (
    get_hardware_info, get_optimal_model_settings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Augment Adam API",
    description="API for Augment Adam models and agents",
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

# Global model and agent registry
model_registry = {}
agent_registry = {}


# Pydantic models for API
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    stop: Optional[List[str]] = None
    use_monte_carlo: Optional[bool] = None


class GenerateResponse(BaseModel):
    text: str
    tokens: int
    time: float


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: int = 100
    temperature: float = 0.7
    stop: Optional[List[str]] = None
    use_monte_carlo: Optional[bool] = None


class ChatResponse(BaseModel):
    message: ChatMessage
    tokens: int
    time: float


class ModelInfo(BaseModel):
    name: str
    type: str
    size: str
    provider: str
    device: str
    max_tokens: int
    settings: Dict[str, Any]


class AgentInfo(BaseModel):
    name: str
    type: str
    description: str
    model: str


class HardwareInfo(BaseModel):
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    gpu: Dict[str, Any]
    platform: Dict[str, Any]
    disk: Dict[str, Any]


class CreateModelRequest(BaseModel):
    model_type: str
    model_size: str
    model_name: Optional[str] = None
    use_optimal_settings: bool = True
    settings: Optional[Dict[str, Any]] = None


class CreateAgentRequest(BaseModel):
    agent_type: str
    name: str
    description: str
    model_id: str
    use_monte_carlo: bool = True
    monte_carlo_particles: Optional[int] = None


# Helper functions
def get_model(model_id: str):
    """Get a model from the registry.
    
    Args:
        model_id: ID of the model
        
    Returns:
        The model
        
    Raises:
        HTTPException: If model not found
    """
    if model_id not in model_registry:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return model_registry[model_id]


def get_agent(agent_id: str):
    """Get an agent from the registry.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        The agent
        
    Raises:
        HTTPException: If agent not found
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return agent_registry[agent_id]


# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Augment Adam API",
        "version": "0.1.0",
        "description": "API for Augment Adam models and agents"
    }


@app.get("/hardware", response_model=HardwareInfo)
async def get_hardware():
    """Get hardware information."""
    return get_hardware_info()


@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all models."""
    models = []
    
    for model_id, model in model_registry.items():
        model_info = model.get_model_info()
        
        models.append({
            "id": model_id,
            "name": model_info.get("name", "Unknown"),
            "type": model_info.get("type", "Unknown"),
            "size": model_id.split("_")[1] if "_" in model_id else "Unknown",
            "provider": model_info.get("provider", "Unknown"),
            "device": model_info.get("device", "Unknown"),
            "max_tokens": model_info.get("max_tokens", 0),
            "settings": model._settings if hasattr(model, "_settings") else {}
        })
    
    return models


@app.post("/models", response_model=ModelInfo)
async def create_model_endpoint(request: CreateModelRequest):
    """Create a new model.
    
    Args:
        request: Model creation request
        
    Returns:
        Information about the created model
    """
    try:
        # Generate model ID
        model_id = f"{request.model_type}_{request.model_size}"
        if model_id in model_registry:
            # If model already exists, return it
            logger.info(f"Model {model_id} already exists, returning existing model")
            model = model_registry[model_id]
        else:
            # Get settings
            if request.use_optimal_settings:
                settings = get_optimal_model_settings(request.model_type, request.model_size)
                
                # Override with custom settings if provided
                if request.settings:
                    settings.update(request.settings)
            else:
                settings = request.settings or {}
            
            # Create model
            logger.info(f"Creating model {model_id} with settings: {settings}")
            model = create_model(
                model_type=request.model_type,
                model_size=request.model_size,
                model_name=request.model_name,
                **settings
            )
            
            # Store settings for reference
            model._settings = settings
            
            # Add to registry
            model_registry[model_id] = model
        
        # Get model info
        model_info = model.get_model_info()
        
        return {
            "id": model_id,
            "name": model_info.get("name", "Unknown"),
            "type": model_info.get("type", "Unknown"),
            "size": request.model_size,
            "provider": model_info.get("provider", "Unknown"),
            "device": model_info.get("device", "Unknown"),
            "max_tokens": model_info.get("max_tokens", 0),
            "settings": model._settings if hasattr(model, "_settings") else {}
        }
    except Exception as e:
        logger.error(f"Error creating model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """Get information about a model.
    
    Args:
        model_id: ID of the model
        
    Returns:
        Information about the model
    """
    model = get_model(model_id)
    model_info = model.get_model_info()
    
    return {
        "id": model_id,
        "name": model_info.get("name", "Unknown"),
        "type": model_info.get("type", "Unknown"),
        "size": model_id.split("_")[1] if "_" in model_id else "Unknown",
        "provider": model_info.get("provider", "Unknown"),
        "device": model_info.get("device", "Unknown"),
        "max_tokens": model_info.get("max_tokens", 0),
        "settings": model._settings if hasattr(model, "_settings") else {}
    }


@app.post("/models/{model_id}/generate", response_model=GenerateResponse)
async def generate_text(model_id: str, request: GenerateRequest):
    """Generate text with a model.
    
    Args:
        model_id: ID of the model
        request: Generation request
        
    Returns:
        Generated text
    """
    model = get_model(model_id)
    
    try:
        # Generate text
        start_time = time.time()
        
        # Prepare generation parameters
        params = {
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stop": request.stop
        }
        
        # Add Monte Carlo parameter if provided
        if request.use_monte_carlo is not None:
            params["use_monte_carlo"] = request.use_monte_carlo
        
        # Generate text
        text = model.generate(**params)
        
        # Calculate time and tokens
        generation_time = time.time() - start_time
        token_count = len(text.split())
        
        return {
            "text": text,
            "tokens": token_count,
            "time": generation_time
        }
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    """List all agents."""
    agents = []
    
    for agent_id, agent in agent_registry.items():
        agents.append({
            "id": agent_id,
            "name": agent.name,
            "type": agent.agent_type,
            "description": agent.description,
            "model": agent.model_id if hasattr(agent, "model_id") else "Unknown"
        })
    
    return agents


@app.post("/agents", response_model=AgentInfo)
async def create_agent_endpoint(request: CreateAgentRequest):
    """Create a new agent.
    
    Args:
        request: Agent creation request
        
    Returns:
        Information about the created agent
    """
    try:
        # Get model
        model = get_model(request.model_id)
        
        # Generate agent ID
        agent_id = f"{request.agent_type}_{len(agent_registry)}"
        
        # Create agent
        logger.info(f"Creating agent {agent_id} with model {request.model_id}")
        
        # Prepare agent parameters
        params = {
            "agent_type": request.agent_type,
            "name": request.name,
            "description": request.description,
            "model": model,
            "use_monte_carlo": request.use_monte_carlo
        }
        
        # Add Monte Carlo particles if provided
        if request.monte_carlo_particles:
            params["monte_carlo_particles"] = request.monte_carlo_particles
        
        # Create agent
        agent = create_agent(**params)
        
        # Store model ID for reference
        agent.model_id = request.model_id
        
        # Add to registry
        agent_registry[agent_id] = agent
        
        return {
            "id": agent_id,
            "name": agent.name,
            "type": agent.agent_type,
            "description": agent.description,
            "model": request.model_id
        }
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent_info(agent_id: str):
    """Get information about an agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        Information about the agent
    """
    agent = get_agent(agent_id)
    
    return {
        "id": agent_id,
        "name": agent.name,
        "type": agent.agent_type,
        "description": agent.description,
        "model": agent.model_id if hasattr(agent, "model_id") else "Unknown"
    }


@app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Chat with an agent.
    
    Args:
        agent_id: ID of the agent
        request: Chat request
        
    Returns:
        Agent response
    """
    agent = get_agent(agent_id)
    
    try:
        # Process chat
        start_time = time.time()
        
        # Extract user message
        user_message = request.messages[-1].content
        
        # Process message
        response = agent.process(user_message)
        
        # Calculate time and tokens
        chat_time = time.time() - start_time
        token_count = len(response["response"].split())
        
        return {
            "message": {
                "role": "assistant",
                "content": response["response"]
            },
            "tokens": token_count,
            "time": chat_time
        }
    except Exception as e:
        logger.error(f"Error chatting with agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Create default models and agents on startup
@app.on_event("startup")
async def startup_event():
    """Create default models and agents on startup."""
    try:
        # Create small_context model
        model_id = "huggingface_small_context"
        settings = get_optimal_model_settings("huggingface", "small_context")
        
        logger.info(f"Creating default model {model_id} with settings: {settings}")
        model = create_model(
            model_type="huggingface",
            model_size="small_context",
            **settings
        )
        
        # Store settings for reference
        model._settings = settings
        
        # Add to registry
        model_registry[model_id] = model
        
        # Create conversational agent
        agent_id = "conversational_0"
        
        logger.info(f"Creating default agent {agent_id} with model {model_id}")
        agent = create_agent(
            agent_type="conversational",
            name="Conversational Agent",
            description="A conversational AI agent",
            model=model
        )
        
        # Store model ID for reference
        agent.model_id = model_id
        
        # Add to registry
        agent_registry[agent_id] = agent
        
        logger.info("Default models and agents created")
    except Exception as e:
        logger.error(f"Error creating default models and agents: {e}")


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    uvicorn.run(app, host=host, port=port)
