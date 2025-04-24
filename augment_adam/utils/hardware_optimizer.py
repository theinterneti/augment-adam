"""Hardware detection and optimization utilities.

This module provides utilities for detecting hardware capabilities
and optimizing performance parameters accordingly.

Version: 0.1.0
Created: 2025-04-29
"""

import logging
import os
import platform
import multiprocessing as mp
import psutil
import json
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Cache for hardware info to avoid repeated detection
_hardware_info_cache = None


def get_hardware_info() -> Dict[str, Any]:
    """Get detailed information about the hardware.
    
    Returns:
        Dictionary containing hardware information
    """
    global _hardware_info_cache
    
    if _hardware_info_cache is not None:
        return _hardware_info_cache
    
    info = {
        "cpu": {
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
            "architecture": platform.machine(),
            "processor": platform.processor()
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        }
    }
    
    # Add GPU information if available
    try:
        import torch
        info["gpu"] = {
            "available": torch.cuda.is_available(),
            "count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [],
            "memory": [torch.cuda.get_device_properties(i).total_memory for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else []
        }
        
        # Check for MPS (Apple Silicon)
        if platform.system() == "Darwin" and platform.machine() == "arm64":
            info["gpu"]["mps_available"] = torch.backends.mps.is_available()
        else:
            info["gpu"]["mps_available"] = False
    except ImportError:
        info["gpu"] = {
            "available": False,
            "count": 0,
            "names": [],
            "memory": []
        }
    
    # Add disk information
    info["disk"] = {
        "total": psutil.disk_usage('/').total,
        "free": psutil.disk_usage('/').free
    }
    
    # Cache the result
    _hardware_info_cache = info
    
    return info


def get_optimal_workers(task_type: str = "cpu_bound") -> int:
    """Get the optimal number of workers for parallel processing.
    
    Args:
        task_type: Type of task ("cpu_bound", "io_bound", or "gpu_bound")
        
    Returns:
        Optimal number of workers
    """
    hw_info = get_hardware_info()
    
    if task_type == "cpu_bound":
        # For CPU-bound tasks, use physical cores minus 1 (leave one for system)
        physical_cores = hw_info["cpu"]["cores_physical"]
        return max(1, physical_cores - 1)
    
    elif task_type == "io_bound":
        # For I/O-bound tasks, use logical cores times 2
        logical_cores = hw_info["cpu"]["cores_logical"]
        return logical_cores * 2
    
    elif task_type == "gpu_bound":
        # For GPU-bound tasks, use number of GPUs times 2
        if hw_info["gpu"]["available"]:
            return max(2, hw_info["gpu"]["count"] * 2)
        elif hw_info["gpu"].get("mps_available", False):
            return 2  # For Apple Silicon MPS
        else:
            # Fall back to CPU if no GPU
            return get_optimal_workers("cpu_bound")
    
    else:
        # Default to CPU-bound
        return get_optimal_workers("cpu_bound")


def get_optimal_batch_size(model_size: str, task_type: str = "generation") -> int:
    """Get the optimal batch size based on hardware and model size.
    
    Args:
        model_size: Size of the model ("small", "medium", "large", "xl")
        task_type: Type of task ("generation", "embedding", "classification")
        
    Returns:
        Optimal batch size
    """
    hw_info = get_hardware_info()
    
    # Base batch sizes for different model sizes
    base_batch_sizes = {
        "small": 32,
        "tiny_context": 24,
        "small_context": 16,
        "medium": 8,
        "medium_context": 4,
        "large": 2,
        "long_context": 1,
        "xl": 1
    }
    
    # Get base batch size
    base_batch_size = base_batch_sizes.get(model_size, 8)
    
    # Adjust based on available memory
    available_memory_gb = hw_info["memory"]["available"] / (1024 ** 3)
    
    # Memory requirements per item in batch (rough estimates in GB)
    memory_per_item = {
        "small": 0.1,
        "tiny_context": 0.15,
        "small_context": 0.2,
        "medium": 0.5,
        "medium_context": 0.7,
        "large": 1.5,
        "long_context": 2.0,
        "xl": 4.0
    }
    
    # Calculate memory-based batch size
    mem_req = memory_per_item.get(model_size, 0.5)
    memory_batch_size = int(available_memory_gb / (mem_req * 1.5))  # 1.5x safety factor
    
    # If GPU is available, adjust based on GPU memory
    if hw_info["gpu"]["available"] and hw_info["gpu"]["count"] > 0:
        gpu_memory_gb = hw_info["gpu"]["memory"][0] / (1024 ** 3)
        gpu_batch_size = int(gpu_memory_gb / (mem_req * 1.2))  # 1.2x safety factor
        memory_batch_size = min(memory_batch_size, gpu_batch_size)
    
    # Final batch size is the minimum of base and memory-based
    batch_size = min(base_batch_size, max(1, memory_batch_size))
    
    # Adjust based on task type
    if task_type == "embedding":
        batch_size = batch_size * 2  # Embeddings use less memory
    elif task_type == "classification":
        batch_size = batch_size * 1.5  # Classification uses less memory
    
    return max(1, int(batch_size))


def get_optimal_monte_carlo_settings(
    model_size: str,
    use_gpu: bool = False
) -> Dict[str, Any]:
    """Get optimal settings for Monte Carlo sampling.
    
    Args:
        model_size: Size of the model
        use_gpu: Whether to use GPU
        
    Returns:
        Dictionary of optimal settings
    """
    hw_info = get_hardware_info()
    
    # Base settings
    settings = {
        "use_monte_carlo": True,
        "use_parallel_monte_carlo": True,
        "monte_carlo_workers": get_optimal_workers("gpu_bound" if use_gpu else "cpu_bound"),
        "monte_carlo_batch_size": get_optimal_batch_size(model_size, "generation"),
        "use_gpu_monte_carlo": use_gpu and hw_info["gpu"]["available"]
    }
    
    # Particle counts based on model size
    particle_counts = {
        "small": 150,
        "tiny_context": 120,
        "small_context": 100,
        "medium": 80,
        "medium_context": 60,
        "large": 40,
        "long_context": 30,
        "xl": 20
    }
    
    # Set particle count
    settings["monte_carlo_particles"] = particle_counts.get(model_size, 50)
    
    # Adjust for GPU if available
    if settings["use_gpu_monte_carlo"]:
        # Can use more particles with GPU
        settings["monte_carlo_particles"] = int(settings["monte_carlo_particles"] * 1.5)
        
        # Adjust batch size for GPU
        settings["monte_carlo_batch_size"] = max(10, settings["monte_carlo_batch_size"])
    
    # Set timeout based on model size (in seconds)
    timeout_settings = {
        "small": 30,
        "tiny_context": 40,
        "small_context": 45,
        "medium": 60,
        "medium_context": 75,
        "large": 90,
        "long_context": 120,
        "xl": 180
    }
    
    settings["monte_carlo_timeout"] = timeout_settings.get(model_size, 60)
    
    return settings


def get_optimal_model_settings(
    model_type: str,
    model_size: str,
    task_type: str = "generation"
) -> Dict[str, Any]:
    """Get optimal model settings based on hardware and model.
    
    Args:
        model_type: Type of model ("huggingface", "ollama", etc.)
        model_size: Size of the model
        task_type: Type of task
        
    Returns:
        Dictionary of optimal settings
    """
    hw_info = get_hardware_info()
    
    # Base settings
    settings = {
        "use_cache": True
    }
    
    # Determine if GPU should be used
    use_gpu = hw_info["gpu"]["available"]
    
    # Set device based on available hardware
    if use_gpu:
        settings["device"] = "cuda"
    elif hw_info["gpu"].get("mps_available", False):
        settings["device"] = "mps"
    else:
        settings["device"] = "cpu"
    
    # Set quantization based on model size and hardware
    if model_type == "huggingface":
        if model_size in ["large", "long_context", "xl"]:
            # Large models need quantization
            if use_gpu:
                settings["load_in_4bit"] = True
            else:
                settings["load_in_8bit"] = True
        elif model_size in ["medium", "medium_context"]:
            # Medium models may need quantization on limited hardware
            if hw_info["memory"]["total"] < 16 * (1024 ** 3):  # Less than 16GB RAM
                settings["load_in_8bit"] = True
        
        # Add Flash Attention for GPU
        if use_gpu:
            settings["use_flash_attention"] = True
            settings["use_bettertransformer"] = True
    
    # Add Monte Carlo settings for small models
    if model_size in ["small", "tiny_context", "small_context"]:
        monte_carlo_settings = get_optimal_monte_carlo_settings(model_size, use_gpu)
        settings.update(monte_carlo_settings)
    
    # Set context window size based on model size
    from augment_adam.models.model_factory import DEFAULT_CONTEXT_SIZES
    if model_size in DEFAULT_CONTEXT_SIZES:
        settings["context_window_size"] = DEFAULT_CONTEXT_SIZES[model_size]
    
    return settings


def save_hardware_profile(file_path: str = "hardware_profile.json") -> None:
    """Save hardware profile to a file.
    
    Args:
        file_path: Path to save the profile
    """
    hw_info = get_hardware_info()
    
    try:
        with open(file_path, "w") as f:
            json.dump(hw_info, f, indent=2)
        
        logger.info(f"Hardware profile saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save hardware profile: {e}")


def load_hardware_profile(file_path: str = "hardware_profile.json") -> Optional[Dict[str, Any]]:
    """Load hardware profile from a file.
    
    Args:
        file_path: Path to load the profile from
        
    Returns:
        Hardware profile or None if file doesn't exist
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, "r") as f:
            profile = json.load(f)
        
        logger.info(f"Hardware profile loaded from {file_path}")
        return profile
    except Exception as e:
        logger.error(f"Failed to load hardware profile: {e}")
        return None


def benchmark_hardware(model_type: str = "huggingface", model_size: str = "small") -> Dict[str, Any]:
    """Run a quick benchmark to measure hardware performance.
    
    Args:
        model_type: Type of model to benchmark with
        model_size: Size of model to benchmark with
        
    Returns:
        Dictionary with benchmark results
    """
    import time
    from augment_adam.models import create_model
    
    results = {
        "hardware": get_hardware_info(),
        "benchmarks": {}
    }
    
    # Get optimal settings
    settings = get_optimal_model_settings(model_type, model_size)
    
    try:
        # Create model
        start_time = time.time()
        model = create_model(
            model_type=model_type,
            model_size=model_size,
            **settings
        )
        load_time = time.time() - start_time
        
        results["benchmarks"]["model_load_time"] = load_time
        
        # Test generation
        prompt = "The quick brown fox jumps over the lazy dog."
        
        start_time = time.time()
        output = model.generate(
            prompt=prompt,
            max_tokens=50
        )
        generation_time = time.time() - start_time
        
        results["benchmarks"]["generation_time"] = generation_time
        results["benchmarks"]["tokens_per_second"] = 50 / generation_time
        
        # Test embedding if available
        if hasattr(model, "get_embedding"):
            try:
                start_time = time.time()
                embedding = model.get_embedding(prompt)
                embedding_time = time.time() - start_time
                
                results["benchmarks"]["embedding_time"] = embedding_time
                results["benchmarks"]["embedding_dimensions"] = len(embedding)
            except Exception as e:
                logger.warning(f"Embedding benchmark failed: {e}")
        
        # Add settings used
        results["settings"] = settings
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        results["error"] = str(e)
    
    return results
