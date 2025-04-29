#!/usr/bin/env python3
"""
HuggingFace Model Implementation for Augment Adam

This module provides an implementation of the ModelBackend for HuggingFace models.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Generator, Union
import tempfile
import shutil

# Try to import optional dependencies
try:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, AutoConfig
    from transformers import BitsAndBytesConfig
    from huggingface_hub import snapshot_download, HfApi
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .model_backend import ModelBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HuggingFaceModel(ModelBackend):
    """HuggingFace Model implementation."""

    def __init__(
        self,
        model_id: str,
        model_config: Optional[Dict[str, Any]] = None,
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
        quantization: Optional[str] = "4bit",
        use_flash_attention: bool = True,
        embedding_model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the HuggingFace Model.

        Args:
            model_id: The ID of the model on HuggingFace Hub.
            model_config: Optional configuration for the model.
            cache_dir: Directory to cache models.
            device: Device to use for inference ("cpu", "cuda", "auto").
            quantization: Quantization method to use ("4bit", "8bit", None).
            use_flash_attention: Whether to use Flash Attention if available.
            embedding_model_id: ID of the embedding model to use.
            **kwargs: Additional arguments for model initialization.
        """
        if not HUGGINGFACE_AVAILABLE:
            raise ImportError("HuggingFace Transformers is not installed. Please install it with 'pip install transformers'.")

        self.model_id = model_id
        self.model_config = model_config or {}
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".cache", "augment_adam_models")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Set embedding model ID
        self.embedding_model_id = embedding_model_id or "sentence-transformers/all-MiniLM-L6-v2"

        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.embedding_model = None

        # Load model if HuggingFace is available
        if HUGGINGFACE_AVAILABLE:
            self._load_model(
                quantization=quantization,
                use_flash_attention=use_flash_attention,
                **kwargs
            )

    def _load_model(
        self,
        quantization: Optional[str] = "4bit",
        use_flash_attention: bool = True,
        **kwargs
    ):
        """
        Load the model and tokenizer.

        Args:
            quantization: Quantization method to use ("4bit", "8bit", None).
            use_flash_attention: Whether to use Flash Attention if available.
            **kwargs: Additional arguments for model loading.
        """
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )

            # Configure model loading parameters
            model_kwargs = {
                "cache_dir": self.cache_dir,
                "trust_remote_code": True,
                "device_map": "auto" if self.device == "cuda" else "cpu",
            }

            # Add torch dtype for GPU
            if self.device == "cuda":
                model_kwargs["torch_dtype"] = torch.float16

            # Configure quantization
            if quantization == "4bit" and self.device == "cuda":
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quantization == "8bit" and self.device == "cuda":
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_8bit=True
                )

            # Configure Flash Attention
            if use_flash_attention and self.device == "cuda":
                model_kwargs["attn_implementation"] = "flash_attention_2"

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                **model_kwargs
            )

            # Create generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if self.device == "cuda" else "cpu"
            )

            # Load embedding model if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer(
                    self.embedding_model_id,
                    cache_folder=self.cache_dir
                )

            # Save model path for sharing with other backends
            self._save_model_path_for_sharing()

            logger.info(f"Successfully loaded HuggingFace model: {self.model_id}")

        except Exception as e:
            logger.error(f"Failed to load HuggingFace model {self.model_id}: {e}")
            raise

    def _save_model_path_for_sharing(self):
        """Save the model path for sharing with other backends."""
        try:
            # Create a directory to store model paths
            shared_paths_dir = os.path.join(self.cache_dir, "shared_models")
            os.makedirs(shared_paths_dir, exist_ok=True)

            # Get model name without organization
            model_name = self.model_id.split("/")[-1] if "/" in self.model_id else self.model_id

            # Get the actual model directory
            model_dir = os.path.join(self.cache_dir, "models--" + self.model_id.replace("/", "--"))

            # Create a metadata file with information about the model
            metadata = {
                "model_id": self.model_id,
                "model_name": model_name,
                "model_path": model_dir,
                "device": self.device,
                "backend": "huggingface",
                "tokenizer_path": os.path.join(model_dir, "snapshots"),
                "embedding_model": self.embedding_model_id if self.embedding_model else None
            }

            # Save metadata
            metadata_path = os.path.join(shared_paths_dir, f"{model_name}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved model metadata for sharing: {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to save model metadata for sharing: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on the prompt.

        Args:
            prompt: The prompt to generate from.
            system_prompt: Optional system prompt for context.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more random).
            top_p: Nucleus sampling parameter.
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            The generated text.
        """
        if not self.is_available():
            raise RuntimeError("Model is not available. Please check if the model is loaded correctly.")

        try:
            # Prepare the prompt with system prompt if provided
            full_prompt = self.format_prompt(prompt, system_prompt)

            # Generate text
            generation_config = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": temperature > 0,
                "pad_token_id": self.tokenizer.eos_token_id
            }

            # Add stop sequences if provided
            if stop:
                generation_config["stopping_criteria"] = transformers.StoppingCriteriaList([
                    StopOnTokens(stop_sequences=stop, tokenizer=self.tokenizer)
                ])

            # Add additional kwargs
            for key, value in kwargs.items():
                if key not in generation_config:
                    generation_config[key] = value

            # Generate
            outputs = self.pipeline(
                full_prompt,
                **generation_config
            )

            # Extract generated text
            generated_text = outputs[0]["generated_text"]

            # Remove the prompt from the generated text
            if generated_text.startswith(full_prompt):
                generated_text = generated_text[len(full_prompt):].strip()

            return generated_text

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generating text: {str(e)}"

    def format_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Format the prompt according to the model's requirements.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.

        Returns:
            The formatted prompt.
        """
        if not system_prompt:
            return prompt

        # Format depends on the model family
        model_id_lower = self.model_id.lower()

        if "llama" in model_id_lower:
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "mistral" in model_id_lower:
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "qwen" in model_id_lower:
            return f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        elif "gemma" in model_id_lower:
            return f"<start_of_turn>user\n{system_prompt}\n\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
        else:
            # Generic format
            return f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate text based on a prompt, streaming the results.

        Args:
            prompt: The prompt to generate from.
            system_prompt: Optional system prompt for context.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more random).
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling).
            stop: List of strings that stop generation when encountered.
            **kwargs: Additional arguments for generation.

        Returns:
            A generator yielding chunks of generated text.
        """
        if not self.is_available():
            yield "Model is not available. Please check if the model is loaded correctly."
            return

        try:
            # Prepare the prompt with system prompt if provided
            full_prompt = self.format_prompt(prompt, system_prompt)

            # Tokenize the prompt
            input_ids = self.tokenizer(full_prompt, return_tensors="pt").input_ids.to(self.device)

            # Configure generation
            generation_config = transformers.GenerationConfig(
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Add stopping criteria if provided
            if stop:
                stopping_criteria = transformers.StoppingCriteriaList([
                    StopOnTokens(stop_sequences=stop, tokenizer=self.tokenizer)
                ])

            # Create a custom streamer that yields tokens
            class YieldingStreamer(transformers.TextStreamer):
                def __init__(self, tokenizer, skip_prompt=True):
                    super().__init__(tokenizer, skip_prompt=skip_prompt)
                    self.text_queue = []
                    self.yielded_text = ""

                def on_finalized_text(self, text, stream_end=False):
                    # Only yield the new text since last yield
                    new_text = text[len(self.yielded_text):]
                    if new_text:
                        self.text_queue.append(new_text)
                        self.yielded_text = text

            # Create the streamer
            streamer = YieldingStreamer(self.tokenizer, skip_prompt=True)

            # Start generation in a separate thread
            import threading

            def generate():
                self.model.generate(
                    input_ids,
                    generation_config=generation_config,
                    streamer=streamer,
                    stopping_criteria=stopping_criteria if stop else None
                )
                # Signal completion
                streamer.text_queue.append(None)

            # Start generation thread
            threading.Thread(target=generate).start()

            # Yield tokens as they become available
            while True:
                if streamer.text_queue:
                    token = streamer.text_queue.pop(0)
                    if token is None:  # End of generation
                        break
                    yield token
                else:
                    import time
                    time.sleep(0.01)  # Small delay to prevent CPU spinning

        except Exception as e:
            logger.error(f"Error streaming text: {e}")
            yield f"Error streaming text: {str(e)}"

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the text.

        Args:
            text: The text to count tokens for.

        Returns:
            The number of tokens.
        """
        if not self.is_available():
            raise RuntimeError("Model is not available. Please check if the model is loaded correctly.")

        tokens = self.tokenizer.encode(text)
        return len(tokens)

    def embed(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            The embedding vector.
        """
        if not self.is_available() or not self.embedding_model:
            raise RuntimeError("Embedding model is not available. Please check if sentence-transformers is installed.")

        embedding = self.embedding_model.encode(text, **kwargs)
        return embedding.tolist()

    def batch_embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: The texts to embed.
            **kwargs: Additional arguments for embedding.

        Returns:
            A list of embedding vectors.
        """
        if not self.is_available() or not self.embedding_model:
            raise RuntimeError("Embedding model is not available. Please check if sentence-transformers is installed.")

        embeddings = self.embedding_model.encode(texts, **kwargs)
        return [embedding.tolist() for embedding in embeddings]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            A dictionary containing model information.
        """
        if not self.is_available():
            return {
                "model_id": self.model_id,
                "available": False,
                "error": "Model not loaded",
                "backend": "huggingface"
            }

        try:
            config = self.model.config.to_dict()
            return {
                "model_id": self.model_id,
                "available": True,
                "device": self.device,
                "backend": "huggingface",
                "model_type": config.get("model_type", "unknown"),
                "vocab_size": config.get("vocab_size", 0),
                "hidden_size": config.get("hidden_size", 0),
                "num_hidden_layers": config.get("num_hidden_layers", 0),
                "num_attention_heads": config.get("num_attention_heads", 0),
                "max_position_embeddings": config.get("max_position_embeddings", 0),
                "embedding_model": self.embedding_model_id if self.embedding_model else None
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "model_id": self.model_id,
                "available": True,
                "backend": "huggingface",
                "error": str(e)
            }

    def is_available(self) -> bool:
        """
        Check if the model is available for use.

        Returns:
            True if the model is available, False otherwise.
        """
        return HUGGINGFACE_AVAILABLE and self.model is not None and self.tokenizer is not None

    def share_model(self, target_backend: str) -> bool:
        """
        Share this model with another backend.

        Args:
            target_backend: The backend to share the model with.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_available():
            logger.error("Cannot share model that is not available")
            return False

        try:
            # Currently only supports sharing with Ollama
            if target_backend.lower() != "ollama":
                logger.warning(f"Sharing with {target_backend} is not supported")
                return False

            # Create a directory to store model paths
            shared_paths_dir = os.path.join(self.cache_dir, "shared_models")
            os.makedirs(shared_paths_dir, exist_ok=True)

            # Get model name without organization
            model_name = self.model_id.split("/")[-1] if "/" in self.model_id else self.model_id

            # Get the actual model directory
            model_dir = os.path.join(self.cache_dir, "models--" + self.model_id.replace("/", "--"))

            # Create a Modelfile for Ollama
            modelfile_content = f"""
FROM {model_name}
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
"""

            # Save the Modelfile
            modelfile_path = os.path.join(shared_paths_dir, f"{model_name}.modelfile")
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)

            # Create a metadata file with information about the model
            metadata = {
                "model_id": self.model_id,
                "model_name": model_name,
                "model_path": model_dir,
                "modelfile_path": modelfile_path,
                "device": self.device,
                "backend": "huggingface",
                "target_backend": target_backend,
                "tokenizer_path": os.path.join(model_dir, "snapshots"),
                "embedding_model": self.embedding_model_id if self.embedding_model else None
            }

            # Save metadata
            metadata_path = os.path.join(shared_paths_dir, f"{model_name}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Shared model {self.model_id} with {target_backend}")
            return True

        except Exception as e:
            logger.error(f"Error sharing model with {target_backend}: {e}")
            return False


# Helper class for stopping generation on specific tokens
class StopOnTokens(transformers.StoppingCriteria):
    """Stopping criteria for generation when specific sequences are generated."""

    def __init__(self, stop_sequences: List[str], tokenizer: Any):
        """
        Initialize the stopping criteria.

        Args:
            stop_sequences: List of sequences that should stop generation.
            tokenizer: The tokenizer to use for encoding stop sequences.
        """
        super().__init__()
        self.stop_sequences = stop_sequences
        self.tokenizer = tokenizer

        # Tokenize stop sequences
        self.stop_ids = [
            self.tokenizer.encode(seq, add_special_tokens=False, return_tensors="pt")[0]
            for seq in stop_sequences
        ]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        """
        Check if generation should stop.

        Args:
            input_ids: The current generated token IDs.
            scores: The scores for the next token.

        Returns:
            True if generation should stop, False otherwise.
        """
        for stop_ids in self.stop_ids:
            if input_ids.shape[1] < len(stop_ids):
                continue

            if torch.all(input_ids[0, -len(stop_ids):] == stop_ids).item():
                return True

        return False
