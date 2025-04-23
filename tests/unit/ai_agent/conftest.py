"""
Test configuration for AI agent tests.

This module provides fixtures and configuration for testing
the AI agent in different environments.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Generator, Any

import pytest
import torch

# Determine available hardware for testing
HAS_CUDA = torch.cuda.is_available()
HAS_MPS = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
DEVICE_TYPE = "cuda" if HAS_CUDA else "mps" if HAS_MPS else "cpu"

# Skip markers for hardware-specific tests
skip_if_no_cuda = pytest.mark.skipif(not HAS_CUDA, reason="CUDA not available")
skip_if_no_gpu = pytest.mark.skipif(not (HAS_CUDA or HAS_MPS), reason="No GPU available")

# Test model configurations
TEST_MODELS = {
    "tiny": {
        "id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "description": "Tiny model for testing",
        "quantization": "none" if DEVICE_TYPE == "cpu" else "4bit"
    },
    "small": {
        "id": "microsoft/phi-2",
        "description": "Small model for testing",
        "quantization": "none" if DEVICE_TYPE == "cpu" else "4bit"
    }
}

@pytest.fixture
def temp_model_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for model files."""
    temp_dir = tempfile.mkdtemp(prefix="dukat_test_models_")
    temp_path = Path(temp_dir)
    
    yield temp_path
    
    # Clean up
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_config_file() -> Generator[Path, None, None]:
    """Create a temporary config file."""
    fd, path = tempfile.mkstemp(prefix="dukat_test_config_", suffix=".json")
    os.close(fd)
    
    yield Path(path)
    
    # Clean up
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def env_info() -> Dict[str, Any]:
    """Provide information about the test environment."""
    return {
        "device_type": DEVICE_TYPE,
        "has_cuda": HAS_CUDA,
        "has_mps": HAS_MPS,
        "cuda_device_count": torch.cuda.device_count() if HAS_CUDA else 0,
        "torch_version": torch.__version__,
    }
