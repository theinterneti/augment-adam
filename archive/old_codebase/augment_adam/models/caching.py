"""Model caching system.

This module provides a caching system for models to improve performance.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
import json
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import torch
from pathlib import Path

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)

# Default cache directory
DEFAULT_CACHE_DIR = os.environ.get(
    "AUGMENT_CACHE_DIR", 
    os.path.join(os.path.expanduser("~"), ".augment_adam", "cache")
)

# Named volume for Docker environments
DOCKER_CACHE_DIR = "/cache"

# Use Docker volume if available, otherwise use default
CACHE_DIR = DOCKER_CACHE_DIR if os.path.exists(DOCKER_CACHE_DIR) else DEFAULT_CACHE_DIR


class ModelCache:
    """Cache for model artifacts.
    
    This class provides a caching system for model artifacts like
    tokenizers, embeddings, and generated text.
    
    Attributes:
        cache_dir: Directory for cache storage
        model_name: Name of the model
        provider: Provider of the model
        max_cache_size: Maximum cache size in bytes
        current_cache_size: Current cache size in bytes
    """
    
    def __init__(
        self,
        model_name: str,
        provider: str,
        cache_dir: Optional[str] = None,
        max_cache_size: int = 1024 * 1024 * 1024,  # 1 GB
        **kwargs
    ):
        """Initialize the Model Cache.
        
        Args:
            model_name: Name of the model
            provider: Provider of the model
            cache_dir: Directory for cache storage
            max_cache_size: Maximum cache size in bytes
            **kwargs: Additional parameters
        """
        self.model_name = model_name
        self.provider = provider
        self.max_cache_size = max_cache_size
        
        # Set cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Use model-specific subdirectory in the cache directory
            model_hash = hashlib.md5(f"{provider}_{model_name}".encode()).hexdigest()[:8]
            self.cache_dir = os.path.join(CACHE_DIR, model_hash)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create subdirectories for different cache types
        self.embeddings_dir = os.path.join(self.cache_dir, "embeddings")
        self.generations_dir = os.path.join(self.cache_dir, "generations")
        self.tokenizer_dir = os.path.join(self.cache_dir, "tokenizer")
        self.model_dir = os.path.join(self.cache_dir, "model")
        
        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(self.generations_dir, exist_ok=True)
        os.makedirs(self.tokenizer_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load cache metadata
        self.metadata_path = os.path.join(self.cache_dir, "metadata.json")
        self.metadata = self._load_metadata()
        
        # Calculate current cache size
        self.current_cache_size = self._calculate_cache_size()
        
        logger.info(f"Initialized model cache for {provider}/{model_name} at {self.cache_dir}")
        logger.info(f"Current cache size: {self.current_cache_size / (1024 * 1024):.2f} MB")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata.
        
        Returns:
            Cache metadata
        """
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        
        # Default metadata
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "embeddings": {},
            "generations": {},
            "tokenizer": {},
            "model": {},
            "last_access": {}
        }
    
    def _save_metadata(self) -> None:
        """Save cache metadata."""
        try:
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")
    
    def _calculate_cache_size(self) -> int:
        """Calculate current cache size.
        
        Returns:
            Current cache size in bytes
        """
        total_size = 0
        
        for dirpath, _, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        
        return total_size
    
    def _cleanup_cache(self) -> None:
        """Clean up cache if it exceeds the maximum size."""
        if self.current_cache_size <= self.max_cache_size:
            return
        
        # Get all cache entries with their last access time
        entries = []
        
        for cache_type in ["embeddings", "generations", "tokenizer", "model"]:
            for key, info in self.metadata[cache_type].items():
                if key in self.metadata["last_access"]:
                    entries.append({
                        "type": cache_type,
                        "key": key,
                        "size": info.get("size", 0),
                        "last_access": self.metadata["last_access"][key]
                    })
        
        # Sort by last access time (oldest first)
        entries.sort(key=lambda x: x["last_access"])
        
        # Remove entries until cache size is below the maximum
        for entry in entries:
            if self.current_cache_size <= self.max_cache_size:
                break
            
            cache_type = entry["type"]
            key = entry["key"]
            
            # Remove from cache
            if cache_type == "embeddings":
                self._remove_embedding(key)
            elif cache_type == "generations":
                self._remove_generation(key)
            elif cache_type == "tokenizer":
                self._remove_tokenizer(key)
            elif cache_type == "model":
                self._remove_model(key)
    
    def _remove_embedding(self, key: str) -> None:
        """Remove an embedding from the cache.
        
        Args:
            key: Embedding key
        """
        if key in self.metadata["embeddings"]:
            file_path = os.path.join(self.embeddings_dir, f"{key}.pkl")
            
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                os.remove(file_path)
                self.current_cache_size -= size
            
            del self.metadata["embeddings"][key]
            if key in self.metadata["last_access"]:
                del self.metadata["last_access"][key]
            
            self._save_metadata()
    
    def _remove_generation(self, key: str) -> None:
        """Remove a generation from the cache.
        
        Args:
            key: Generation key
        """
        if key in self.metadata["generations"]:
            file_path = os.path.join(self.generations_dir, f"{key}.txt")
            
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                os.remove(file_path)
                self.current_cache_size -= size
            
            del self.metadata["generations"][key]
            if key in self.metadata["last_access"]:
                del self.metadata["last_access"][key]
            
            self._save_metadata()
    
    def _remove_tokenizer(self, key: str) -> None:
        """Remove a tokenizer from the cache.
        
        Args:
            key: Tokenizer key
        """
        if key in self.metadata["tokenizer"]:
            dir_path = os.path.join(self.tokenizer_dir, key)
            
            if os.path.exists(dir_path):
                size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                for file_name in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file_name))
                os.rmdir(dir_path)
                self.current_cache_size -= size
            
            del self.metadata["tokenizer"][key]
            if key in self.metadata["last_access"]:
                del self.metadata["last_access"][key]
            
            self._save_metadata()
    
    def _remove_model(self, key: str) -> None:
        """Remove a model from the cache.
        
        Args:
            key: Model key
        """
        if key in self.metadata["model"]:
            dir_path = os.path.join(self.model_dir, key)
            
            if os.path.exists(dir_path):
                size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                for file_name in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file_name))
                os.rmdir(dir_path)
                self.current_cache_size -= size
            
            del self.metadata["model"][key]
            if key in self.metadata["last_access"]:
                del self.metadata["last_access"][key]
            
            self._save_metadata()
    
    def _update_last_access(self, key: str) -> None:
        """Update last access time for a cache entry.
        
        Args:
            key: Cache key
        """
        import time
        self.metadata["last_access"][key] = time.time()
        self._save_metadata()
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get an embedding from the cache.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Embedding if found, None otherwise
        """
        # Create a key for the embedding
        key = hashlib.md5(text.encode()).hexdigest()
        
        # Check if embedding exists in cache
        if key in self.metadata["embeddings"]:
            file_path = os.path.join(self.embeddings_dir, f"{key}.pkl")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        embedding = pickle.load(f)
                    
                    # Update last access time
                    self._update_last_access(key)
                    
                    return embedding
                except Exception as e:
                    logger.warning(f"Failed to load embedding from cache: {e}")
        
        return None
    
    def save_embedding(self, text: str, embedding: List[float]) -> None:
        """Save an embedding to the cache.
        
        Args:
            text: Text the embedding is for
            embedding: Embedding to save
        """
        # Create a key for the embedding
        key = hashlib.md5(text.encode()).hexdigest()
        
        # Save embedding to cache
        file_path = os.path.join(self.embeddings_dir, f"{key}.pkl")
        
        try:
            with open(file_path, "wb") as f:
                pickle.dump(embedding, f)
            
            # Update metadata
            size = os.path.getsize(file_path)
            self.metadata["embeddings"][key] = {
                "text_hash": key,
                "size": size,
                "dimensions": len(embedding)
            }
            self._update_last_access(key)
            
            # Update cache size
            self.current_cache_size += size
            
            # Clean up cache if necessary
            self._cleanup_cache()
        except Exception as e:
            logger.warning(f"Failed to save embedding to cache: {e}")
    
    def get_generation(self, prompt: str, params: Dict[str, Any]) -> Optional[str]:
        """Get a generation from the cache.
        
        Args:
            prompt: Prompt for generation
            params: Generation parameters
            
        Returns:
            Generated text if found, None otherwise
        """
        # Create a key for the generation
        params_str = json.dumps(params, sort_keys=True)
        key = hashlib.md5((prompt + params_str).encode()).hexdigest()
        
        # Check if generation exists in cache
        if key in self.metadata["generations"]:
            file_path = os.path.join(self.generations_dir, f"{key}.txt")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        generation = f.read()
                    
                    # Update last access time
                    self._update_last_access(key)
                    
                    return generation
                except Exception as e:
                    logger.warning(f"Failed to load generation from cache: {e}")
        
        return None
    
    def save_generation(self, prompt: str, params: Dict[str, Any], generation: str) -> None:
        """Save a generation to the cache.
        
        Args:
            prompt: Prompt for generation
            params: Generation parameters
            generation: Generated text
        """
        # Create a key for the generation
        params_str = json.dumps(params, sort_keys=True)
        key = hashlib.md5((prompt + params_str).encode()).hexdigest()
        
        # Save generation to cache
        file_path = os.path.join(self.generations_dir, f"{key}.txt")
        
        try:
            with open(file_path, "w") as f:
                f.write(generation)
            
            # Update metadata
            size = os.path.getsize(file_path)
            self.metadata["generations"][key] = {
                "prompt_hash": hashlib.md5(prompt.encode()).hexdigest(),
                "params_hash": hashlib.md5(params_str.encode()).hexdigest(),
                "size": size,
                "length": len(generation)
            }
            self._update_last_access(key)
            
            # Update cache size
            self.current_cache_size += size
            
            # Clean up cache if necessary
            self._cleanup_cache()
        except Exception as e:
            logger.warning(f"Failed to save generation to cache: {e}")
    
    def get_tokenizer_path(self) -> Optional[str]:
        """Get the path to the cached tokenizer.
        
        Returns:
            Path to tokenizer if found, None otherwise
        """
        # Use a fixed key for the tokenizer
        key = "default"
        
        # Check if tokenizer exists in cache
        if key in self.metadata["tokenizer"]:
            dir_path = os.path.join(self.tokenizer_dir, key)
            
            if os.path.exists(dir_path) and os.listdir(dir_path):
                # Update last access time
                self._update_last_access(key)
                
                return dir_path
        
        return None
    
    def save_tokenizer(self, tokenizer: Any) -> str:
        """Save a tokenizer to the cache.
        
        Args:
            tokenizer: Tokenizer to save
            
        Returns:
            Path to saved tokenizer
        """
        # Use a fixed key for the tokenizer
        key = "default"
        
        # Create directory for tokenizer
        dir_path = os.path.join(self.tokenizer_dir, key)
        os.makedirs(dir_path, exist_ok=True)
        
        try:
            # Save tokenizer
            tokenizer.save_pretrained(dir_path)
            
            # Calculate size
            size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
            
            # Update metadata
            self.metadata["tokenizer"][key] = {
                "size": size
            }
            self._update_last_access(key)
            
            # Update cache size
            self.current_cache_size += size
            
            # Clean up cache if necessary
            self._cleanup_cache()
            
            return dir_path
        except Exception as e:
            logger.warning(f"Failed to save tokenizer to cache: {e}")
            return dir_path
    
    def get_model_path(self) -> Optional[str]:
        """Get the path to the cached model.
        
        Returns:
            Path to model if found, None otherwise
        """
        # Use a fixed key for the model
        key = "default"
        
        # Check if model exists in cache
        if key in self.metadata["model"]:
            dir_path = os.path.join(self.model_dir, key)
            
            if os.path.exists(dir_path) and os.listdir(dir_path):
                # Update last access time
                self._update_last_access(key)
                
                return dir_path
        
        return None
    
    def save_model_weights(self, model: Any) -> str:
        """Save model weights to the cache.
        
        Args:
            model: Model to save
            
        Returns:
            Path to saved model
        """
        # Use a fixed key for the model
        key = "default"
        
        # Create directory for model
        dir_path = os.path.join(self.model_dir, key)
        os.makedirs(dir_path, exist_ok=True)
        
        try:
            # Save model
            model.save_pretrained(dir_path)
            
            # Calculate size
            size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
            
            # Update metadata
            self.metadata["model"][key] = {
                "size": size
            }
            self._update_last_access(key)
            
            # Update cache size
            self.current_cache_size += size
            
            # Clean up cache if necessary
            self._cleanup_cache()
            
            return dir_path
        except Exception as e:
            logger.warning(f"Failed to save model to cache: {e}")
            return dir_path
    
    def clear(self) -> None:
        """Clear the cache."""
        try:
            # Remove all files
            for dirpath, dirnames, filenames in os.walk(self.cache_dir):
                for filename in filenames:
                    if filename != "metadata.json":  # Keep metadata file
                        os.remove(os.path.join(dirpath, filename))
            
            # Reset metadata
            self.metadata = {
                "model_name": self.model_name,
                "provider": self.provider,
                "embeddings": {},
                "generations": {},
                "tokenizer": {},
                "model": {},
                "last_access": {}
            }
            self._save_metadata()
            
            # Reset cache size
            self.current_cache_size = os.path.getsize(self.metadata_path)
            
            logger.info(f"Cleared cache for {self.provider}/{self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")


# Global cache registry
_cache_registry = {}


def get_model_cache(
    model_name: str,
    provider: str,
    cache_dir: Optional[str] = None,
    max_cache_size: int = 1024 * 1024 * 1024,  # 1 GB
    **kwargs
) -> ModelCache:
    """Get a model cache.
    
    Args:
        model_name: Name of the model
        provider: Provider of the model
        cache_dir: Directory for cache storage
        max_cache_size: Maximum cache size in bytes
        **kwargs: Additional parameters
        
    Returns:
        Model cache
    """
    global _cache_registry
    
    # Create a key for the cache
    key = f"{provider}_{model_name}"
    
    # Check if cache exists
    if key not in _cache_registry:
        # Create a new cache
        _cache_registry[key] = ModelCache(
            model_name=model_name,
            provider=provider,
            cache_dir=cache_dir,
            max_cache_size=max_cache_size,
            **kwargs
        )
    
    return _cache_registry[key]
