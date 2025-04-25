"""MCP Agent Implementation.

This module provides an agent implementation designed for MCP integration.
MCP agents are designed to be deployed as MCP servers via fastapi-mcp.

Version: 0.1.0
Created: 2025-04-30
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
import asyncio

from augment_adam.models import ModelInterface
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.tools import Tool
from augment_adam.ai_agent.smc.potential import Potential

logger = logging.getLogger(__name__)


class MCPAgent(BaseAgent):
    """MCP Agent implementation.
    
    This class provides an agent implementation designed for MCP integration.
    MCP agents are designed to be deployed as MCP servers via fastapi-mcp.
    
    Attributes:
        name: Name of the agent
        description: Description of the agent
        model: The language model to use
        system_prompt: System prompt for the agent
        tools: List of tools available to the agent
        potentials: List of potentials for controlled generation
        output_format: Format for agent output (e.g., "text", "json")
        strict_output: Whether to enforce strict output format
        inference_settings: Settings for model inference
        mcp_config: MCP configuration
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model: ModelInterface,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        potentials: Optional[List[Potential]] = None,
        output_format: str = "json",  # Default to JSON for MCP
        strict_output: bool = True,   # Default to strict output for MCP
        mcp_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the MCP Agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            model: The language model to use
            system_prompt: System prompt for the agent
            tools: List of tools available to the agent
            potentials: List of potentials for controlled generation
            output_format: Format for agent output (e.g., "text", "json")
            strict_output: Whether to enforce strict output format
            mcp_config: MCP configuration
            **kwargs: Additional parameters for the agent
        """
        super().__init__(
            name=name,
            description=description,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            potentials=potentials,
            output_format=output_format,
            strict_output=strict_output,
            **kwargs
        )
        
        # Set MCP configuration
        self.mcp_config = mcp_config or {
            "version": "1.0",
            "schema": "https://raw.githubusercontent.com/microsoft/mcp/main/schemas/mcp-1.0.json",
            "description": description,
            "contact": {
                "name": name,
                "url": kwargs.get("contact_url", ""),
                "email": kwargs.get("contact_email", "")
            }
        }
        
        logger.info(f"Initialized MCP Agent '{name}'")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent.
        
        Returns:
            Default system prompt
        """
        return f"""You are {self.name}, {self.description}.
        
Your goal is to provide helpful, accurate, and concise responses to user queries.

IMPORTANT: You must respond in valid JSON format with the following structure:
{{
    "response": "Your response text here",
    "metadata": {{
        "confidence": 0.9,  // A value between 0 and 1
        "sources": []       // Optional list of sources
    }}
}}

Respond in a friendly and professional manner.
"""
    
    def _format_prompt(self, user_input: str) -> str:
        """Format the prompt for the model.
        
        Args:
            user_input: User input
            
        Returns:
            Formatted prompt
        """
        # Basic prompt format
        prompt = f"{self.system_prompt}\n\nUser: {user_input}\n\n{self.name}:"
        
        # Add output format instructions
        prompt += "\n\nRespond with a valid JSON object with the following structure:"
        prompt += """
{
    "response": "Your response text here",
    "metadata": {
        "confidence": 0.9,  // A value between 0 and 1
        "sources": []       // Optional list of sources
    }
}
"""
        
        # Add tool instructions if tools are available
        if self.tools:
            prompt += "\n\nYou have access to the following tools:\n"
            for tool in self.tools:
                prompt += f"- {tool.name}: {tool.description}\n"
            
            prompt += "\nTo use a tool, include the following in your response JSON:\n"
            prompt += """
{
    "response": "Your response text here",
    "metadata": {
        "confidence": 0.9,
        "sources": []
    },
    "tool_calls": [
        {
            "tool": "tool_name",
            "parameters": {
                "param1": "value1"
            }
        }
    ]
}
"""
        
        return prompt
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse the model output.
        
        Args:
            output: Model output
            
        Returns:
            Parsed output
        """
        # Extract JSON from output
        json_str = self._extract_json(output)
        
        try:
            # Parse JSON
            response_data = json.loads(json_str)
            
            # Check for required fields
            if "response" not in response_data:
                response_data["response"] = output
            
            if "metadata" not in response_data:
                response_data["metadata"] = {
                    "confidence": 0.8
                }
            
            # Check for tool calls
            if "tool_calls" in response_data:
                tool_calls = response_data["tool_calls"]
            else:
                # Try to extract tool calls from the old format
                tool_calls = self._extract_tool_calls(output)
            
            return {
                "response": response_data["response"],
                "parsed_response": response_data,
                "tool_calls": tool_calls
            }
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON output")
            
            if self.strict_output:
                # Try to fix JSON
                fixed_json = self._fix_json(json_str)
                try:
                    response_data = json.loads(fixed_json)
                    
                    # Check for required fields
                    if "response" not in response_data:
                        response_data["response"] = output
                    
                    if "metadata" not in response_data:
                        response_data["metadata"] = {
                            "confidence": 0.8
                        }
                    
                    # Check for tool calls
                    if "tool_calls" in response_data:
                        tool_calls = response_data["tool_calls"]
                    else:
                        # Try to extract tool calls from the old format
                        tool_calls = self._extract_tool_calls(output)
                    
                    return {
                        "response": response_data["response"],
                        "parsed_response": response_data,
                        "tool_calls": tool_calls,
                        "fixed_json": True
                    }
                except json.JSONDecodeError:
                    # Return error if strict output is required
                    return {
                        "response": output,
                        "error": "Failed to parse JSON output",
                        "tool_calls": self._extract_tool_calls(output)
                    }
            else:
                # Return text response if not strict
                return {
                    "response": output,
                    "tool_calls": self._extract_tool_calls(output)
                }
    
    def get_mcp_schema(self) -> Dict[str, Any]:
        """Get the MCP schema for the agent.
        
        Returns:
            MCP schema
        """
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": self.name,
                "description": self.description,
                "version": "1.0.0",
                "x-mcp": self.mcp_config
            },
            "paths": {
                "/process": {
                    "post": {
                        "summary": "Process user input",
                        "description": "Process user input and generate a response",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "input": {
                                                "type": "string",
                                                "description": "User input"
                                            },
                                            "context": {
                                                "type": "object",
                                                "description": "Additional context"
                                            }
                                        },
                                        "required": ["input"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "response": {
                                                    "type": "string",
                                                    "description": "Agent response"
                                                },
                                                "metadata": {
                                                    "type": "object",
                                                    "description": "Response metadata"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add tool endpoints if tools are available
        if self.tools:
            for tool in self.tools:
                tool_schema = tool.get_schema()
                
                schema["paths"][f"/tools/{tool.name}"] = {
                    "post": {
                        "summary": tool.description,
                        "description": tool.description,
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": tool_schema["parameters"]["properties"],
                                        "required": tool_schema["parameters"]["required"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
        
        return schema
