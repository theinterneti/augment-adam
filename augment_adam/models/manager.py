"""
Model manager for the AI coding agent.

This module provides the ModelManager class for downloading,
loading, and using local LLM models.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    BitsAndBytesConfig
)

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages local LLM models for the AI coding agent using Hugging Face.

    This class handles downloading, loading, and inference with local models,
    optimized for code generation and related tasks.
    """

    def __init__(
        self,
        models_dir: str = "~/.augment_adam/models",
        config_path: str = "~/.augment_adam/config.json",
        default_model: str = "codellama/CodeLlama-13b-Instruct-hf"
    ):
        # Set up directories
        self.models_dir = Path(os.path.expanduser(models_dir))
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = Path(os.path.expanduser(config_path))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.loaded_models = {}
        self.default_model = default_model
        self.config = self._load_config()

        # Determine available hardware
        self.device_map = self._determine_device_map()
        logger.info(f"Using device map: {self.device_map}")

    def _determine_device_map(self) -> Union[str, Dict]:
        """Determine the optimal device mapping based on available hardware."""
        if torch.cuda.is_available():
            logger.info(f"CUDA available: {torch.cuda.device_count()} devices")
            return "auto"  # Let transformers handle the mapping
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("MPS (Apple Silicon) available")
            return "mps"
        else:
            logger.info("Using CPU for inference")
            return "cpu"

    def _load_config(self) -> Dict:
        """Load configuration from disk or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")

        # Default configuration
        default_config = {
            "models": {
                "codellama/CodeLlama-13b-Instruct-hf": {
                    "description": "Code Llama 13B Instruct model",
                    "quantization": "4bit",
                    "default_parameters": {
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "max_new_tokens": 1024
                    }
                },
                "Phind/Phind-CodeLlama-34B-v2": {
                    "description": "Phind Code Llama 34B model",
                    "quantization": "4bit",
                    "default_parameters": {
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "max_new_tokens": 1024
                    }
                },
                "WizardLM/WizardCoder-Python-34B-V1.0": {
                    "description": "WizardCoder Python 34B model",
                    "quantization": "4bit",
                    "default_parameters": {
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "max_new_tokens": 1024
                    }
                },
                "mistralai/Mistral-7B-Instruct-v0.2": {
                    "description": "Mistral 7B Instruct model",
                    "quantization": "4bit",
                    "default_parameters": {
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "max_new_tokens": 1024
                    }
                }
            },
            "default_model": self.default_model
        }

        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _save_config(self) -> None:
        """Save current configuration to disk."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _infer_model_type(self, model_id: str) -> str:
        """
        Infer the model type from the model ID.

        Args:
            model_id: The model ID

        Returns:
            str: The inferred model type
        """
        model_id_lower = model_id.lower()

        # Check for known model types
        if 'tinyllama' in model_id_lower or 'llama' in model_id_lower:
            return 'llama'
        elif 'mistral' in model_id_lower:
            return 'mistral'
        elif 'gpt' in model_id_lower:
            return 'gpt2'
        elif 'bert' in model_id_lower:
            return 'bert'
        elif 'roberta' in model_id_lower:
            return 'roberta'
        elif 't5' in model_id_lower:
            return 't5'
        elif 'falcon' in model_id_lower:
            return 'falcon'
        elif 'bloom' in model_id_lower:
            return 'bloom'
        elif 'opt' in model_id_lower:
            return 'opt'
        elif 'gemma' in model_id_lower:
            return 'gemma'

        # Default to 'auto' if we can't infer
        return 'auto'

    def _format_prompt(self, prompt: str, system_prompt: Optional[str] = None, model_id: str = None) -> str:
        """
        Format the prompt according to the model's requirements.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            model_id: The model ID

        Returns:
            str: The formatted prompt
        """
        if not system_prompt:
            return prompt

        model_id_lower = model_id.lower() if model_id else ""

        # Format depends on the model
        if "mistral" in model_id_lower:
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "llama" in model_id_lower and "instruct" in model_id_lower:
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "codellama" in model_id_lower and "instruct" in model_id_lower:
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "wizard" in model_id_lower:
            return f"### System: {system_prompt}\n\n### User: {prompt}\n\n### Assistant:"
        elif "tinyllama" in model_id_lower:
            return f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>"
        else:
            # Generic format
            return f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

    def _clean_response(self, response: str, model_id: str) -> str:
        """
        Clean the model response based on model-specific patterns.

        Args:
            response: The raw model response
            model_id: The model ID

        Returns:
            str: The cleaned response
        """
        model_id_lower = model_id.lower() if model_id else ""

        # Clean up based on model type
        if "mistral" in model_id_lower or "codellama" in model_id_lower:
            # Remove any trailing [INST] or similar tags
            if "[/INST]" in response:
                response = response.split("[/INST]")[0]
        elif "tinyllama" in model_id_lower:
            # Remove any trailing user or system tags
            if "<|user|>" in response:
                response = response.split("<|user|>")[0]
            if "<|system|>" in response:
                response = response.split("<|system|>")[0]
        elif "llama" in model_id_lower:
            # Handle other llama models
            if "[/INST]" in response:
                response = response.split("[/INST]")[0]

        return response.strip()

    def download_model(
        self,
        model_id: str,
        revision: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """
        Download a model from Hugging Face Hub.

        Args:
            model_id: The Hugging Face model ID
            revision: Specific model revision to download
            force: Whether to force re-download if model exists

        Returns:
            bool: Success status
        """
        try:
            # Create model directory
            model_dir = self.models_dir / model_id.split('/')[-1]

            if model_dir.exists() and not force:
                logger.info(f"Model {model_id} already downloaded. Use force=True to re-download.")
                return True

            model_dir.mkdir(exist_ok=True, parents=True)

            logger.info(f"Downloading model {model_id}...")

            # Download tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                revision=revision,
                cache_dir=model_dir,
                trust_remote_code=True
            )
            tokenizer.save_pretrained(model_dir)
            logger.info(f"Tokenizer for {model_id} downloaded successfully")

            # Download model configuration and weights
            # Use AutoConfig instead of trying to access config_class directly
            from transformers import AutoConfig, AutoModelForCausalLM

            # Download configuration
            model_config = AutoConfig.from_pretrained(
                model_id,
                revision=revision,
                cache_dir=model_dir,
                trust_remote_code=True
            )

            # Download model weights
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                revision=revision,
                cache_dir=model_dir,
                config=model_config,
                trust_remote_code=True,
                local_files_only=False
            )
            model.save_pretrained(model_dir)
            logger.info(f"Model weights for {model_id} downloaded successfully")

            # Add model_type if it's missing
            if not hasattr(model_config, 'model_type'):
                # Infer model type from model ID
                model_config.model_type = self._infer_model_type(model_id)
                model_config.save_pretrained(model_dir)
                logger.info(f"Added model_type '{model_config.model_type}' to config for {model_id}")

            # Add to config if not present
            if model_id not in self.config["models"]:
                self.config["models"][model_id] = {
                    "description": f"Model {model_id}",
                    "quantization": "4bit",
                    "default_parameters": {
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "max_new_tokens": 1024
                    }
                }
                self._save_config()

            logger.info(f"Model {model_id} downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error downloading model {model_id}: {e}")
            return False

    def load_model(
        self,
        model_id: str,
        quantization: Optional[str] = None,
        force_reload: bool = False
    ) -> bool:
        """
        Load a model into memory.

        Args:
            model_id: The model ID to load
            quantization: Quantization method (4bit, 8bit, none)
            force_reload: Whether to force reload if already loaded

        Returns:
            bool: Success status
        """
        try:
            # Check if model is already loaded
            if model_id in self.loaded_models and not force_reload:
                logger.info(f"Model {model_id} already loaded")
                return True

            # Get model directory
            model_name = model_id.split('/')[-1]
            model_dir = self.models_dir / model_name

            # If model doesn't exist locally, try to download it
            if not model_dir.exists():
                logger.info(f"Model {model_id} not found locally. Attempting to download...")
                if not self.download_model(model_id):
                    return False

            # Determine quantization method
            if quantization is None:
                if model_id in self.config["models"]:
                    quantization = self.config["models"][model_id].get("quantization", "4bit")
                else:
                    quantization = "4bit"  # Default to 4-bit quantization

            logger.info(f"Loading model {model_id} with {quantization} quantization...")

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_dir,
                trust_remote_code=True
            )

            # Configure quantization
            load_kwargs = {
                "device_map": self.device_map,
                "trust_remote_code": True,
            }

            if self.device_map != "cpu":
                load_kwargs["torch_dtype"] = torch.float16

            if quantization == "4bit":
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quantization == "8bit":
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_8bit=True
                )

            # Check if we need to handle model_type
            # Load the config first
            from transformers import AutoConfig
            config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)

            # Add model_type if it's missing
            if not hasattr(config, 'model_type'):
                # Infer model type from model ID
                config.model_type = self._infer_model_type(model_id)
                config.save_pretrained(model_dir)
                logger.info(f"Added model_type '{config.model_type}' to config for {model_id}")

            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_dir,
                **load_kwargs
            )

            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device_map=self.device_map
            )

            # Store in loaded models
            self.loaded_models[model_id] = {
                "model": model,
                "tokenizer": tokenizer,
                "pipeline": pipe,
                "quantization": quantization
            }

            logger.info(f"Model {model_id} loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            return False

    def generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text using the specified model.

        Args:
            prompt: The input prompt
            model_id: The model ID to use (defaults to default_model)
            system_prompt: Optional system prompt for instruction models
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            max_new_tokens: Maximum new tokens to generate
            **kwargs: Additional generation parameters

        Returns:
            Tuple[str, Dict]: Generated text and metadata
        """
        # Use default model if none specified
        if model_id is None:
            model_id = self.config.get("default_model", self.default_model)

        # Load model if not already loaded
        if model_id not in self.loaded_models:
            if not self.load_model(model_id):
                return "", {"error": f"Failed to load model {model_id}"}

        # Get model config and pipeline
        model_config = self.config["models"].get(model_id, {})
        pipe = self.loaded_models[model_id]["pipeline"]
        tokenizer = self.loaded_models[model_id]["tokenizer"]

        # Set generation parameters
        gen_kwargs = {}

        # Use config defaults if not specified
        default_params = model_config.get("default_parameters", {})
        gen_kwargs["temperature"] = temperature if temperature is not None else default_params.get("temperature", 0.7)
        gen_kwargs["top_p"] = top_p if top_p is not None else default_params.get("top_p", 0.95)
        gen_kwargs["max_new_tokens"] = max_new_tokens if max_new_tokens is not None else default_params.get("max_new_tokens", 1024)
        gen_kwargs["do_sample"] = gen_kwargs["temperature"] > 0

        # Add any additional kwargs
        gen_kwargs.update(kwargs)

        # Prepare full prompt with system prompt if provided
        full_prompt = self._format_prompt(prompt, system_prompt, model_id)

        logger.info(f"Generating with model {model_id}")
        logger.debug(f"Prompt: {full_prompt[:100]}...")

        try:
            # Generate text
            result = pipe(
                full_prompt,
                **gen_kwargs
            )

            generated_text = result[0]["generated_text"]

            # Extract only the new content
            response = generated_text[len(full_prompt):]

            # Clean up response based on model-specific patterns
            response = self._clean_response(response, model_id)

            metadata = {
                "model": model_id,
                "prompt_tokens": len(tokenizer.encode(full_prompt)),
                "completion_tokens": len(tokenizer.encode(response)),
                "parameters": gen_kwargs
            }

            return response.strip(), metadata

        except Exception as e:
            logger.error(f"Error generating text with {model_id}: {e}")
            return "", {"error": str(e)}

    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.

        Args:
            model_id: The model ID to unload

        Returns:
            bool: Success status
        """
        if model_id in self.loaded_models:
            try:
                # Delete model components
                del self.loaded_models[model_id]["pipeline"]
                del self.loaded_models[model_id]["model"]
                del self.loaded_models[model_id]["tokenizer"]
                del self.loaded_models[model_id]

                # Force garbage collection
                import gc
                gc.collect()

                # Clear CUDA cache if available
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                logger.info(f"Model {model_id} unloaded successfully")
                return True
            except Exception as e:
                logger.error(f"Error unloading model {model_id}: {e}")
                return False
        else:
            logger.warning(f"Model {model_id} not loaded")
            return False

    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all downloaded models with their details.

        Returns:
            List[Dict]: List of model information dictionaries
        """
        models = []

        # Check local model directories
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                # Find matching model ID in config
                model_id = None
                for mid in self.config["models"]:
                    if mid.split('/')[-1] == model_dir.name:
                        model_id = mid
                        break

                if not model_id:
                    # Use directory name as fallback
                    model_id = model_dir.name

                # Get config info if available
                config_info = self.config["models"].get(model_id, {})

                models.append({
                    "id": model_id,
                    "name": model_dir.name,
                    "description": config_info.get("description", "No description"),
                    "quantization": config_info.get("quantization", "unknown"),
                    "is_loaded": model_id in self.loaded_models,
                    "is_default": model_id == self.config.get("default_model")
                })

        return models

    def list_loaded_models(self) -> List[Dict[str, Any]]:
        """
        List all currently loaded models with their details.

        Returns:
            List[Dict]: List of loaded model information
        """
        return [
            {
                "id": model_id,
                "name": model_id.split('/')[-1],
                "quantization": info["quantization"],
                "is_default": model_id == self.config.get("default_model")
            }
            for model_id, info in self.loaded_models.items()
        ]

    def set_default_model(self, model_id: str) -> bool:
        """
        Set the default model.

        Args:
            model_id: The model ID to set as default

        Returns:
            bool: Success status
        """
        if model_id in self.config["models"]:
            self.config["default_model"] = model_id
            self._save_config()
            logger.info(f"Default model set to {model_id}")
            return True
        else:
            logger.warning(f"Model {model_id} not found in config")
            return False
