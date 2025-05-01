#!/usr/bin/env python3
"""
Model Manager for Augment Adam

This module handles the integration with language models,
providing a unified interface for model inference with a focus on
efficient model sharing between HuggingFace and Ollama.
"""

import os
import json
import logging
import subprocess
import platform
import shutil
import time
from typing import Dict, List, Optional, Union, Tuple, Generator, Any

import requests

# Import model backend and registry
from .model_backend import ModelBackend
from .model_registry import ModelRegistry, get_registry
from .huggingface_model import HuggingFaceModel
from .ollama_model import OllamaModel

# Try to import optional dependencies
try:
    from huggingface_hub import HfApi, snapshot_download
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

# Try to import HuggingFace transformers
try:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    from transformers import BitsAndBytesConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for language model interactions with efficient model sharing."""

    # Recommended models for different use cases
    RECOMMENDED_MODELS = {
        # HuggingFace models
        "huggingface": {
            "default": "mistralai/Mistral-7B-Instruct-v0.2",
            "small": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "medium": "microsoft/phi-2",
            "large": "meta-llama/Llama-3-8b-chat-hf",
            "xl": "meta-llama/Llama-3-70b-chat-hf",
            "code": "codellama/CodeLlama-7b-instruct-hf",
            "embedding": "sentence-transformers/all-MiniLM-L6-v2",
            # Qwen 3 models
            "qwen3_small": "Qwen/Qwen3-0.6B-Chat",
            "qwen3_medium": "Qwen/Qwen3-1.7B-Chat",
            "qwen3_large": "Qwen/Qwen3-4B-Chat",
            "qwen3_xl": "Qwen/Qwen3-8B-Chat",
            "qwen3_xxl": "Qwen/Qwen3-14B-Chat",
            "qwen3_xxxl": "Qwen/Qwen3-32B-Chat",
            # Qwen 3 MoE models
            "qwen3_moe_small": "Qwen/Qwen3-30B-A3B-Chat",
            "qwen3_moe_large": "Qwen/Qwen3-235B-A22B-Chat",
        },
        # Ollama models
        "ollama": {
            "default": "llama3",
            "small": "phi2",
            "medium": "mistral",
            "large": "llama3",
            "xl": "llama3:70b",
            "code": "codellama:7b",
            # Qwen 3 models
            "qwen3_small": "qwen3:0.6b",
            "qwen3_medium": "qwen3:1.7b",
            "qwen3_large": "qwen3:4b",
            "qwen3_xl": "qwen3:8b",
            "qwen3_xxl": "qwen3:14b",
            "qwen3_xxxl": "qwen3:32b",
            # Domain-specific models
            "docker": "codellama:7b-instruct",
            "wsl": "llama3:8b",
            "devcontainer": "codellama:7b-instruct",
            "general": "llama3:8b"
        }
    }

    # Default context window sizes for different model sizes
    DEFAULT_CONTEXT_SIZES = {
        "small": 2048,
        "medium": 4096,
        "large": 8192,
        "xl": 16384,
        "xxl": 32768,
        "xxxl": 32768,
        "qwen3_small": 32768,
        "qwen3_medium": 32768,
        "qwen3_large": 32768,
        "qwen3_xl": 128000,
        "qwen3_xxl": 128000,
        "qwen3_xxxl": 128000,
        "qwen3_moe_small": 128000,
        "qwen3_moe_large": 128000,
    }

    def __init__(
        self,
        model_type: str = "ollama",
        model_name: Optional[str] = None,
        model_size: str = "medium",
        use_local: bool = True,
        cache_dir: Optional[str] = None,
        domain: str = "general",
        **kwargs
    ):
        """
        Initialize the model manager.

        Args:
            model_type: Type of model to use ("huggingface" or "ollama")
            model_name: Name of the model to use (if None, will use recommended model for size)
            model_size: Size of the model to use (small, medium, large, xl, etc.)
            use_local: Whether to use local models (True) or remote APIs (False)
            cache_dir: Directory to cache models (shared between HuggingFace and Ollama)
            domain: Domain of expertise (general, docker, wsl, devcontainer, etc.)
            **kwargs: Additional arguments for model initialization
        """
        self.model_type = model_type
        self.model_size = model_size
        self.use_local = use_local
        self.domain = domain

        # Use a shared cache directory for both HuggingFace and Ollama
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Check if Docker is available
        self.docker_available = self._check_docker_available()

        # Check if WSL is available (Windows only)
        self.wsl_available = self._check_wsl_available() if platform.system() == "Windows" else False

        # Determine model name based on type and size if not provided
        if model_name is None:
            if model_type == "huggingface":
                # Use recommended HuggingFace model for the size
                self.model_name = self.RECOMMENDED_MODELS["huggingface"].get(
                    model_size,
                    self.RECOMMENDED_MODELS["huggingface"]["default"]
                )
            else:
                # Use recommended Ollama model for the size or domain
                if model_size.startswith("qwen3"):
                    # Use Qwen 3 model
                    self.model_name = self.RECOMMENDED_MODELS["ollama"].get(
                        model_size,
                        self.RECOMMENDED_MODELS["ollama"]["default"]
                    )
                else:
                    # Use domain-specific model if available
                    self.model_name = self.RECOMMENDED_MODELS["ollama"].get(
                        domain,
                        self.RECOMMENDED_MODELS["ollama"]["default"]
                    )
        else:
            self.model_name = model_name

        logger.info(f"Initialized ModelManager with model={self.model_name}, type={model_type}, size={model_size}, domain={domain}")
        logger.info(f"Environment: Docker={self.docker_available}, WSL={self.wsl_available}")

        # Initialize the model registry
        self.registry = get_registry()
        
        # Register backends
        self.registry.register_backend("huggingface", HuggingFaceModel)
        self.registry.register_backend("ollama", OllamaModel)
        
        # Initialize the model
        self.model = self._init_model(**kwargs)

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

    def _init_model(self, **kwargs) -> Optional[ModelBackend]:
        """Initialize the model based on the specified type."""
        try:
            # Create model configuration
            model_config = {
                "domain": self.domain,
                "model_size": self.model_size,
                "context_size": self.DEFAULT_CONTEXT_SIZES.get(
                    self.model_size,
                    4096  # Default context size
                )
            }
            
            # Add any additional configuration from kwargs
            model_config.update(kwargs.get("model_config", {}))
            
            # Create the model
            if self.model_type == "huggingface" and TRANSFORMERS_AVAILABLE:
                # Create HuggingFace model
                model = self.registry.create_model(
                    backend_name="huggingface",
                    model_id=self.model_name,
                    model_config=model_config,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
                
                # Share with Ollama if requested
                if kwargs.get("share_with_ollama", True):
                    model.share_model("ollama")
                    
                return model
            elif self.model_type == "ollama":
                # Create Ollama model
                return self.registry.create_model(
                    backend_name="ollama",
                    model_id=self.model_name,
                    model_config=model_config,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
            else:
                logger.error(f"Unsupported model type: {self.model_type}")
                return None
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            return None

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Generate a response from the model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            **kwargs: Additional arguments for generation

        Returns:
            The model's response as a string
        """
        # Enhance the prompt with domain-specific context if system_prompt is not provided
        if system_prompt is None:
            if self.domain == "docker":
                system_prompt = "You are a specialized assistant for Docker. Provide clear, concise, and accurate information about Docker commands, Dockerfiles, and container management."
            elif self.domain == "wsl":
                system_prompt = "You are a specialized assistant for Windows Subsystem for Linux (WSL). Provide clear, concise, and accurate information about WSL setup, configuration, and usage."
            elif self.domain == "devcontainer":
                system_prompt = "You are a specialized assistant for VS Code devcontainers. Provide clear, concise, and accurate information about creating, configuring, and using devcontainers for development."
            elif self.domain == "code":
                system_prompt = "You are a specialized coding assistant. Provide clear, concise, and accurate information about programming, code patterns, and best practices."
            else:
                system_prompt = "You are a helpful assistant. Provide clear, concise, and accurate information."

        # Check if model is available
        if not self.model or not self.model.is_available():
            # Try to initialize the model again
            self.model = self._init_model()
            if not self.model or not self.model.is_available():
                return "Model is not available. Please check your configuration."

        # Generate response
        try:
            return self.model.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            **kwargs: Additional arguments for generation

        Returns:
            A generator yielding chunks of the model's response
        """
        # Enhance the prompt with domain-specific context if system_prompt is not provided
        if system_prompt is None:
            if self.domain == "docker":
                system_prompt = "You are a specialized assistant for Docker. Provide clear, concise, and accurate information about Docker commands, Dockerfiles, and container management."
            elif self.domain == "wsl":
                system_prompt = "You are a specialized assistant for Windows Subsystem for Linux (WSL). Provide clear, concise, and accurate information about WSL setup, configuration, and usage."
            elif self.domain == "devcontainer":
                system_prompt = "You are a specialized assistant for VS Code devcontainers. Provide clear, concise, and accurate information about creating, configuring, and using devcontainers for development."
            elif self.domain == "code":
                system_prompt = "You are a specialized coding assistant. Provide clear, concise, and accurate information about programming, code patterns, and best practices."
            else:
                system_prompt = "You are a helpful assistant. Provide clear, concise, and accurate information."

        # Check if model is available
        if not self.model or not self.model.is_available():
            # Try to initialize the model again
            self.model = self._init_model()
            if not self.model or not self.model.is_available():
                yield "Model is not available. Please check your configuration."
                return

        # Generate streaming response
        try:
            yield from self.model.generate_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            yield f"Error generating streaming response: {str(e)}"

    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get a list of available models.

        Returns:
            A dictionary of available models by type
        """
        available_models = {
            "huggingface": [],
            "ollama": []
        }

        # Check HuggingFace models
        if HUGGINGFACE_AVAILABLE:
            try:
                # Get recommended Qwen 3 models
                qwen3_models = [
                    model for key, model in self.RECOMMENDED_MODELS["huggingface"].items()
                    if "qwen3" in key
                ]
                available_models["huggingface"].extend(qwen3_models)

                # Add other popular models
                api = HfApi()
                popular_models = api.list_models(
                    filter="text-generation",
                    sort="downloads",
                    limit=5
                )
                available_models["huggingface"].extend([model.modelId for model in popular_models])
            except Exception as e:
                logger.error(f"Error getting HuggingFace models: {e}")

        # Check Ollama models
        try:
            # Get list of models from Ollama
            ollama_model = self.registry.create_model(
                backend_name="ollama",
                model_id="llama3",  # Doesn't matter which model, we just need an instance
                cache_dir=self.cache_dir
            )
            
            if ollama_model and ollama_model.is_available():
                # Get list of models from Ollama
                response = requests.get(f"{ollama_model.api_url}/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    available_models["ollama"] = [model.get("name") for model in models]
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")

        # If we're only interested in one type, return just those models
        if self.model_type == "huggingface":
            return available_models["huggingface"]
        elif self.model_type == "ollama":
            return available_models["ollama"]

        return available_models

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

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            A dictionary containing model information.
        """
        if not self.model or not self.model.is_available():
            return {
                "model_id": self.model_name,
                "model_type": self.model_type,
                "available": False,
                "error": "Model not available"
            }
            
        # Get model info from the backend
        model_info = self.model.get_model_info()
        
        # Add additional information
        model_info.update({
            "model_type": self.model_type,
            "model_size": self.model_size,
            "domain": self.domain,
            "cache_dir": self.cache_dir
        })
        
        return model_info

    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to embed.
            **kwargs: Additional arguments for embedding.
            
        Returns:
            The embedding vector.
        """
        if not self.model or not self.model.is_available():
            raise RuntimeError("Model is not available. Please check your configuration.")
            
        return self.model.embed(text, **kwargs)
        
    def batch_embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: The texts to embed.
            **kwargs: Additional arguments for embedding.
            
        Returns:
            A list of embedding vectors.
        """
        if not self.model or not self.model.is_available():
            raise RuntimeError("Model is not available. Please check your configuration.")
            
        return self.model.batch_embed(texts, **kwargs)


# Singleton instance
_model_manager = None


def get_model_manager(**kwargs) -> ModelManager:
    """
    Get the singleton ModelManager instance.

    Args:
        **kwargs: Arguments to pass to ModelManager constructor if creating a new instance

    Returns:
        The ModelManager instance
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(**kwargs)
    return _model_manager


# Example usage
if __name__ == "__main__":
    # Create a model manager for Qwen 3
    qwen_manager = ModelManager(
        model_type="huggingface",
        model_size="qwen3_medium",
        domain="code"
    )

    # Generate a response about Python
    qwen_response = qwen_manager.generate_response(
        prompt="What are the key features of Python 3.12?",
        temperature=0.7,
        max_tokens=500
    )
    print("=== Qwen 3 Response ===\n", qwen_response)

    # Create a model manager for Docker domain
    docker_manager = ModelManager(model_type="ollama", domain="docker")

    # Generate a response about Dockerfiles
    docker_response = docker_manager.generate_response(
        prompt="How do I create a multi-stage Dockerfile for a Python application?"
    )
    print("\n=== Docker Response ===\n", docker_response)

    # Get available models
    available_models = qwen_manager.get_available_models()
    print("\n=== Available Models ===\n", json.dumps(available_models, indent=2))

    # Get Docker information
    docker_info = docker_manager.get_docker_info()
    print("\n=== Docker Info ===\n", json.dumps(docker_info, indent=2))

    # Get WSL information (Windows only)
    if platform.system() == "Windows":
        wsl_info = docker_manager.get_wsl_info()
        print("\n=== WSL Info ===\n", json.dumps(wsl_info, indent=2))
