"""Configuration management for the Augment Adam assistant.

This module provides configuration settings for the Augment Adam assistant.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, Optional
import os
import logging
from pathlib import Path
import yaml

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MemoryConfig(BaseModel):
    """Configuration for the memory system.
    
    Attributes:
        vector_db: The vector database to use (chroma or faiss).
        persist_dir: Directory to persist memory data.
    """
    
    vector_db: str = Field(default="chroma", description="Vector database to use")
    persist_dir: str = Field(
        default="~/.augment_adam/memory",
        description="Directory to persist memory data",
    )


class Config(BaseModel):
    """Configuration for the Augment Adam assistant.
    
    Attributes:
        model: The model to use for inference.
        ollama_host: The host address for the Ollama API.
        memory: Configuration for the memory system.
        log_level: The logging level to use.
    """
    
    model: str = Field(default="llama3:8b", description="Model to use for inference")
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama API endpoint",
    )
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    log_level: str = Field(default="INFO", description="Logging level")


def get_config_path() -> Path:
    """Get the path to the configuration file.
    
    Returns:
        The path to the configuration file.
    """
    # Check for config in current directory
    if os.path.exists("config.yaml"):
        return Path("config.yaml")
    
    # Check for config in user's home directory
    home_config = os.path.expanduser("~/.augment_adam/config.yaml")
    if os.path.exists(home_config):
        return Path(home_config)
    
    # Return default path
    return Path(os.path.expanduser("~/.augment_adam/config.yaml"))


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        The loaded configuration.
    """
    # Get config path
    path = Path(config_path) if config_path else get_config_path()
    
    # Create default config
    config = Config()
    
    # Try to load config from file
    try:
        if path.exists():
            with open(path, "r") as f:
                config_dict = yaml.safe_load(f)
                
                if config_dict:
                    # Update config with loaded values
                    config = Config.model_validate(config_dict)
                    logger.info(f"Loaded configuration from {path}")
                else:
                    logger.warning(f"Empty configuration file: {path}")
        else:
            logger.info(f"Configuration file not found: {path}")
            
            # Create directory if it doesn't exist
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default config
            save_config(config, str(path))
    
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
    
    return config


def save_config(config: Config, config_path: Optional[str] = None) -> bool:
    """Save configuration to a file.
    
    Args:
        config: The configuration to save.
        config_path: Path to the configuration file.
        
    Returns:
        True if successful, False otherwise.
    """
    # Get config path
    path = Path(config_path) if config_path else get_config_path()
    
    try:
        # Create directory if it doesn't exist
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save config
        with open(path, "w") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)
        
        logger.info(f"Saved configuration to {path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False


# Singleton instance for easy access
default_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get or load the configuration.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        The loaded configuration.
    """
    global default_config
    
    if default_config is None:
        default_config = load_config(config_path)
    
    return default_config
