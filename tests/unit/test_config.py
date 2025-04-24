"""Tests for the configuration module.

This module contains tests for the configuration management functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from augment_adam.config import Config, MemoryConfig, load_config, save_config


def test_default_config():
    """Test that the default configuration is created correctly."""
    config = Config()

    assert config.model == "llama3:8b"
    assert config.ollama_host == "http://localhost:11434"
    assert config.memory.vector_db == "chroma"
    assert config.memory.persist_dir == "~/.augment_adam/memory"
    assert config.log_level == "INFO"


def test_custom_config():
    """Test that a custom configuration is created correctly."""
    config = Config(
        model="mistral:7b-instruct-v0.2",
        ollama_host="http://localhost:12345",
        memory=MemoryConfig(
            vector_db="faiss",
            persist_dir="/tmp/augment_adam/memory",
        ),
        log_level="DEBUG",
    )

    assert config.model == "mistral:7b-instruct-v0.2"
    assert config.ollama_host == "http://localhost:12345"
    assert config.memory.vector_db == "faiss"
    assert config.memory.persist_dir == "/tmp/augment_adam/memory"
    assert config.log_level == "DEBUG"


def test_save_and_load_config():
    """Test saving and loading a configuration."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a config file path
        config_path = os.path.join(temp_dir, "config.yaml")

        # Create a custom config
        config = Config(
            model="mistral:7b-instruct-v0.2",
            ollama_host="http://localhost:12345",
            memory=MemoryConfig(
                vector_db="faiss",
                persist_dir="/tmp/augment_adam/memory",
            ),
            log_level="DEBUG",
        )

        # Save the config
        save_config(config, config_path)

        # Check that the file exists
        assert os.path.exists(config_path)

        # Load the config
        loaded_config = load_config(config_path)

        # Check that the loaded config matches the original
        assert loaded_config.model == config.model
        assert loaded_config.ollama_host == config.ollama_host
        assert loaded_config.memory.vector_db == config.memory.vector_db
        assert loaded_config.memory.persist_dir == config.memory.persist_dir
        assert loaded_config.log_level == config.log_level


def test_load_nonexistent_config():
    """Test loading a configuration that doesn't exist."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a config file path that doesn't exist
        config_path = os.path.join(temp_dir, "nonexistent.yaml")

        # Load the config
        config = load_config(config_path)

        # Check that the default config is returned
        assert config.model == "llama3:8b"
        assert config.ollama_host == "http://localhost:11434"
        assert config.memory.vector_db == "chroma"
        assert config.memory.persist_dir == "~/.augment_adam/memory"
        assert config.log_level == "INFO"

        # Check that the file was created
        assert os.path.exists(config_path)


def test_memory_config_override(self):
    config = load_config({
        'memory': {
            'persist_dir': '/tmp/augment_adam/memory',
        }
    })
    assert config.memory.persist_dir == '/tmp/augment_adam/memory'
