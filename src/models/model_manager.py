#!/usr/bin/env python3
"""
Model Manager for Dukat: Development Environment Assistant

This module handles the integration with open-source language models,
providing a unified interface for model inference with a focus on
Docker, WSL, and devcontainer development environments.
"""

import os
import json
import logging
import subprocess
import platform
import shutil
from typing import Dict, List, Optional, Union, Tuple

import requests

# Try to import optional dependencies
try:
    from huggingface_hub import HfApi
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for language model interactions with focus on development environments."""

    # Preferred models for development environment assistance
    PREFERRED_MODELS = {
        "docker": ["codellama:7b-instruct", "llama3:8b", "mistral:7b-instruct-v0.2"],
        "wsl": ["llama3:8b", "mistral:7b-instruct-v0.2", "codellama:7b-instruct"],
        "devcontainer": ["codellama:7b-instruct", "llama3:8b", "mistral:7b-instruct-v0.2"],
        "general": ["llama3:8b", "mistral:7b-instruct-v0.2", "gemma:7b"]
    }

    def __init__(self, model_name: str = "llama3:8b", use_local: bool = True, domain: str = "general"):
        """
        Initialize the model manager.

        Args:
            model_name: Name of the model to use
            use_local: Whether to use a local model (via Ollama) or a remote API
            domain: Domain of expertise (docker, wsl, devcontainer, general)
        """
        self.model_name = model_name
        self.use_local = use_local
        self.domain = domain
        self.ollama_url = "http://localhost:11434/api"

        # Check if Docker is available
        self.docker_available = self._check_docker_available()

        # Check if WSL is available (Windows only)
        self.wsl_available = self._check_wsl_available() if platform.system() == "Windows" else False

        logger.info(f"Initialized ModelManager with model={model_name}, local={use_local}, domain={domain}")
        logger.info(f"Environment: Docker={self.docker_available}, WSL={self.wsl_available}")

        # Try to use the best model for the domain if the specified model is not available
        if use_local:
            self._ensure_model_available()

    def _check_docker_available(self) -> bool:
        """Check if Docker is available on the system."""
        try:
            # Try to run 'docker version'
            result = subprocess.run(["docker", "version"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   check=False)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Docker not available: {e}")
            return False

    def _check_wsl_available(self) -> bool:
        """Check if WSL is available (Windows only)."""
        try:
            # Try to run 'wsl --status'
            result = subprocess.run(["wsl", "--status"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   check=False)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"WSL not available: {e}")
            return False

    def _ensure_model_available(self):
        """Ensure that the best model for the domain is available."""
        available_models = self.get_available_models()

        # If the current model is available, use it
        if self.model_name in available_models:
            return

        # Try to find the best available model for the domain
        for model in self.PREFERRED_MODELS.get(self.domain, self.PREFERRED_MODELS["general"]):
            if model in available_models:
                logger.info(f"Using {model} instead of {self.model_name} for {self.domain} domain")
                self.model_name = model
                return

        # If no preferred model is available, use the first available model
        if available_models:
            logger.info(f"Using {available_models[0]} as fallback model")
            self.model_name = available_models[0]

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            The model's response as a string
        """
        # Enhance the prompt with domain-specific context if system_prompt is not provided
        if system_prompt is None:
            if self.domain == "docker":
                system_prompt = "You are Dukat, a specialized Linux assistant for Docker. Provide clear, concise, and accurate information about Docker commands, Dockerfiles, and container management."
            elif self.domain == "wsl":
                system_prompt = "You are Dukat, a specialized Linux assistant for Windows Subsystem for Linux (WSL). Provide clear, concise, and accurate information about WSL setup, configuration, and usage."
            elif self.domain == "devcontainer":
                system_prompt = "You are Dukat, a specialized Linux assistant for VS Code devcontainers. Provide clear, concise, and accurate information about creating, configuring, and using devcontainers for development."
            else:
                system_prompt = "You are Dukat, a specialized Linux assistant for development environments. Provide clear, concise, and accurate information about Linux, Docker, WSL, and devcontainers."

        if self.use_local:
            return self._generate_local(prompt, system_prompt)
        else:
            # Implement remote API call here
            return "Remote API not implemented yet"

    def _generate_local(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using a local Ollama model."""
        try:
            # Check if Ollama is running and start it if not
            if not self._is_ollama_running():
                self._start_ollama()
                # Wait a bit for Ollama to start
                import time
                time.sleep(2)

            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_ctx": 4096
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            # Make the request to Ollama
            response = requests.post(f"{self.ollama_url}/generate", json=payload)
            response.raise_for_status()

            # Parse the response
            result = response.json()
            return result.get("response", "No response generated")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return f"Error: Could not generate response. Is Ollama running? ({str(e)})"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Error: {str(e)}"

    def _is_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_url}/tags")
            return response.status_code == 200
        except:
            return False

    def _start_ollama(self) -> bool:
        """Start Ollama if it's not running."""
        try:
            # Check if ollama command is available
            if shutil.which("ollama") is None:
                logger.error("Ollama is not installed")
                return False

            # Start Ollama in the background
            if platform.system() == "Windows":
                subprocess.Popen(["ollama", "serve"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["ollama", "serve"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               start_new_session=True)

            logger.info("Started Ollama service")
            return True
        except Exception as e:
            logger.error(f"Failed to start Ollama: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get a list of available models."""
        try:
            if self.use_local:
                try:
                    response = requests.get(f"{self.ollama_url}/tags")
                    response.raise_for_status()
                    result = response.json()
                    return [model["name"] for model in result.get("models", [])]
                except requests.exceptions.RequestException:
                    # If Ollama is not running, try to start it
                    if self._start_ollama():
                        # Wait a bit for Ollama to start
                        import time
                        time.sleep(2)
                        # Try again
                        response = requests.get(f"{self.ollama_url}/tags")
                        response.raise_for_status()
                        result = response.json()
                        return [model["name"] for model in result.get("models", [])]
                    return []
            else:
                # For remote API, return available models from Hugging Face if available
                if HUGGINGFACE_AVAILABLE:
                    api = HfApi()
                    models = api.list_models(author="meta-llama", limit=5)
                    return [model.modelId for model in models]
                return ["remote-model-1", "remote-model-2"]  # Placeholder
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

    def get_docker_info(self) -> Dict:
        """Get information about Docker installation."""
        if not self.docker_available:
            return {"available": False}

        try:
            # Get Docker version
            version_result = subprocess.run(["docker", "version", "--format", "'{{json .}}'"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          text=True,
                                          check=False)

            # Get Docker info
            info_result = subprocess.run(["docker", "info", "--format", "'{{json .}}'"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        check=False)

            # Parse the results
            version_data = json.loads(version_result.stdout.strip("'")) if version_result.returncode == 0 else {}
            info_data = json.loads(info_result.stdout.strip("'")) if info_result.returncode == 0 else {}

            return {
                "available": True,
                "version": version_data,
                "info": info_data
            }
        except Exception as e:
            logger.error(f"Error getting Docker info: {e}")
            return {"available": True, "error": str(e)}

    def get_wsl_info(self) -> Dict:
        """Get information about WSL installation (Windows only)."""
        if not self.wsl_available:
            return {"available": False}

        try:
            # Get WSL version
            version_result = subprocess.run(["wsl", "--version"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          text=True,
                                          check=False)

            # Get WSL distributions
            distro_result = subprocess.run(["wsl", "-l", "-v"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True,
                                         check=False)

            return {
                "available": True,
                "version": version_result.stdout if version_result.returncode == 0 else "",
                "distributions": distro_result.stdout if distro_result.returncode == 0 else ""
            }
        except Exception as e:
            logger.error(f"Error getting WSL info: {e}")
            return {"available": True, "error": str(e)}

# Example usage
if __name__ == "__main__":
    # Create a model manager for Docker domain
    docker_manager = ModelManager(model_name="codellama:7b-instruct", domain="docker")

    # Generate a response about Dockerfiles
    docker_response = docker_manager.generate_response(
        prompt="How do I create a multi-stage Dockerfile for a Python application?"
    )
    print("=== Docker Response ===\n", docker_response)

    # Create a model manager for WSL domain
    wsl_manager = ModelManager(domain="wsl")

    # Generate a response about WSL
    wsl_response = wsl_manager.generate_response(
        prompt="How do I set up WSL2 with Ubuntu and configure it for development?"
    )
    print("\n=== WSL Response ===\n", wsl_response)

    # Get Docker information
    docker_info = docker_manager.get_docker_info()
    print("\n=== Docker Info ===\n", json.dumps(docker_info, indent=2))

    # Get WSL information (Windows only)
    if platform.system() == "Windows":
        wsl_info = wsl_manager.get_wsl_info()
        print("\n=== WSL Info ===\n", json.dumps(wsl_info, indent=2))
