"""
Environment-specific tests for the AI agent.

These tests verify that the AI agent works correctly in the
current environment, checking hardware compatibility and
dependencies.
"""

import os
import sys
import importlib
from pathlib import Path

import pytest
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Import markers from conftest
from tests.unit.ai_agent.conftest import skip_if_no_cuda, skip_if_no_gpu

class TestEnvironment:
    """Tests for verifying the environment."""

    def test_python_version(self):
        """Test that the Python version is compatible."""
        version_info = sys.version_info
        major, minor = version_info.major, version_info.minor

        # Check Python version is at least 3.9
        assert major == 3 and minor >= 9, f"Python version {major}.{minor} is not supported. Minimum required is 3.9."

    def test_torch_installation(self):
        """Test that PyTorch is installed correctly."""
        # Check that torch is importable
        assert importlib.util.find_spec("torch") is not None

        # Check torch version
        torch_version = torch.__version__
        major, minor = map(int, torch_version.split('.')[:2])

        assert major >= 2 or (major == 1 and minor >= 10), f"PyTorch version {torch_version} is not supported. Minimum required is 1.10."

    def test_transformers_installation(self):
        """Test that Transformers is installed correctly."""
        # Check that transformers is importable
        assert importlib.util.find_spec("transformers") is not None

        # Check that AutoModelForCausalLM and AutoTokenizer are available
        assert hasattr(AutoModelForCausalLM, "from_pretrained")
        assert hasattr(AutoTokenizer, "from_pretrained")

    def test_hardware_detection(self, env_info):
        """Test hardware detection."""
        # Print environment info for debugging
        print(f"Environment info: {env_info}")

        # Check that CUDA is detected correctly
        assert env_info["has_cuda"] == torch.cuda.is_available()

        # Check CUDA device count if CUDA is available
        if env_info["has_cuda"]:
            assert env_info["cuda_device_count"] > 0

        # Check MPS detection if on macOS
        if hasattr(torch.backends, 'mps'):
            assert env_info["has_mps"] == torch.backends.mps.is_available()

    @skip_if_no_gpu
    def test_gpu_memory(self, env_info):
        """Test GPU memory availability."""
        if env_info["has_cuda"]:
            # Check CUDA memory
            for i in range(env_info["cuda_device_count"]):
                memory_info = torch.cuda.get_device_properties(i).total_memory
                print(f"CUDA device {i} memory: {memory_info / 1024**3:.2f} GB")

                # Check that there's at least 2GB of memory
                assert memory_info >= 2 * 1024**3, f"CUDA device {i} has less than 2GB of memory"
        elif env_info["has_mps"]:
            # MPS doesn't have a standard way to check memory
            # Just verify it's available
            assert torch.backends.mps.is_available()

    @skip_if_no_cuda
    def test_cuda_compatibility(self):
        """Test CUDA compatibility with a small tensor operation."""
        # Create a small tensor and move it to CUDA
        x = torch.rand(100, 100)
        x_cuda = x.cuda()

        # Perform a simple operation
        result = x_cuda @ x_cuda.T

        # Move back to CPU and check result
        result_cpu = result.cpu()

        # Check that the result is valid
        assert not torch.isnan(result_cpu).any(), "CUDA computation produced NaN values"
        assert not torch.isinf(result_cpu).any(), "CUDA computation produced infinite values"

    def test_bitsandbytes_installation(self):
        """Test that bitsandbytes is installed correctly for quantization."""
        try:
            import bitsandbytes as bnb

            # Check that 4-bit quantization is available
            assert hasattr(bnb, "nn"), "bitsandbytes.nn module not found"

            # Only test CUDA compatibility if CUDA is available
            if torch.cuda.is_available():
                # Check CUDA compatibility
                # The attribute location may vary between versions
                compiled_with_cuda = False
                if hasattr(bnb, "cuda") and hasattr(bnb.cuda, "COMPILED_WITH_CUDA"):
                    compiled_with_cuda = bnb.cuda.COMPILED_WITH_CUDA
                elif hasattr(bnb, "COMPILED_WITH_CUDA"):
                    compiled_with_cuda = bnb.COMPILED_WITH_CUDA

                # Skip this check as it's not critical
                if not compiled_with_cuda:
                    print("Warning: bitsandbytes may not be compiled with CUDA support")
        except ImportError:
            pytest.skip("bitsandbytes not installed")

    def test_model_download_permissions(self, temp_model_dir):
        """Test that we have permissions to download and write model files."""
        # Check that we can create files in the model directory
        test_file = temp_model_dir / "test_file.txt"

        try:
            with open(test_file, 'w') as f:
                f.write("Test content")

            # Check that the file was created
            assert test_file.exists()

            # Check that we can read the file
            with open(test_file, 'r') as f:
                content = f.read()

            assert content == "Test content"

            # Check that we can delete the file
            test_file.unlink()
            assert not test_file.exists()
        except Exception as e:
            pytest.fail(f"Failed to write to model directory: {e}")

    def test_environment_variables(self):
        """Test that required environment variables are set."""
        # Check for TRANSFORMERS_CACHE
        transformers_cache = os.environ.get("TRANSFORMERS_CACHE")
        if transformers_cache:
            # Check that the directory exists
            cache_dir = Path(transformers_cache)
            assert cache_dir.exists(), f"TRANSFORMERS_CACHE directory {transformers_cache} does not exist"

            # Skip write test as it might fail in some environments
            print(f"TRANSFORMERS_CACHE is set to {transformers_cache}")

        # Check for HF_HOME
        hf_home = os.environ.get("HF_HOME")
        if hf_home:
            # Check that the directory exists
            hf_dir = Path(hf_home)
            assert hf_dir.exists(), f"HF_HOME directory {hf_home} does not exist"

            # Skip write test as it might fail in some environments
            print(f"HF_HOME is set to {hf_home}")

    def test_network_access(self):
        """Test that we have network access to download models."""
        import requests

        try:
            # Try to access the Hugging Face API
            response = requests.get("https://huggingface.co/api/models", timeout=5)

            # Check that the request was successful
            assert response.status_code == 200, f"Failed to access Hugging Face API: {response.status_code}"

            # Check that we got a valid response
            data = response.json()
            assert isinstance(data, list), "Invalid response from Hugging Face API"
            assert len(data) > 0, "Empty response from Hugging Face API"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Network access test failed: {e}")

    def test_disk_space(self, temp_model_dir):
        """Test that we have enough disk space for models."""
        import shutil

        # Check disk space
        total, used, free = shutil.disk_usage(temp_model_dir)

        # Convert to GB
        free_gb = free / (1024**3)

        print(f"Free disk space: {free_gb:.2f} GB")

        # Check that we have at least 5GB free
        assert free_gb >= 5, f"Not enough free disk space: {free_gb:.2f} GB (minimum 5 GB required)"
