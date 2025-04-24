# Hardware Optimization and Model Analysis

This guide explains how to optimize Augment Adam for your specific hardware and scientifically analyze model performance.

## Introduction

Augment Adam includes tools for automatically detecting your hardware capabilities and optimizing model settings accordingly. This allows you to get the best performance from your available hardware, whether you're running on a laptop, desktop, or server.

## Hardware Detection

The hardware detection system automatically identifies:

- CPU specifications (cores, architecture, frequency)
- Memory capacity and availability
- GPU availability and specifications
- Disk space
- Operating system details

This information is used to determine optimal settings for different model sizes and tasks.

## Automatic Optimization

Based on the detected hardware, Augment Adam can automatically optimize:

1. **Model Selection**: Recommending the best model size for your hardware
2. **Quantization Settings**: Using 4-bit or 8-bit quantization when appropriate
3. **Monte Carlo Parameters**: Adjusting particle count and batch size
4. **Parallel Processing**: Setting the optimal number of workers
5. **Context Window Size**: Configuring appropriate context window sizes
6. **GPU Utilization**: Enabling GPU acceleration when available

## Model Analysis

The model analyzer allows you to scientifically compare different models across various tasks:

1. **Performance Metrics**: Measuring tokens per second, load time, and memory usage
2. **Quality Assessment**: Evaluating output quality for different tasks
3. **Task-Specific Recommendations**: Finding the best model for each specific task
4. **Hardware-Specific Rankings**: Ranking models based on your specific hardware

## Using the Hardware Optimizer

### Command Line

```bash
# Run hardware detection and optimization
python -m examples.hardware_optimization

# Run hardware benchmark
python -m examples.hardware_optimization --benchmark

# Run full model analysis (may take a long time)
python -m examples.hardware_optimization --analyze-models
```

### Python API

```python
from augment_adam.utils.hardware_optimizer import (
    get_hardware_info, get_optimal_model_settings,
    benchmark_hardware
)
from augment_adam.models import create_model

# Get hardware information
hw_info = get_hardware_info()
print(f"CPU: {hw_info['cpu']['cores_physical']} physical cores")
print(f"GPU: {hw_info['gpu']['available']}")

# Get optimal settings for a small model with large context window
settings = get_optimal_model_settings("huggingface", "small_context")

# Create model with optimal settings
model = create_model(
    model_type="huggingface",
    model_size="small_context",
    **settings
)

# Run a benchmark
results = benchmark_hardware()
print(f"Tokens per second: {results['benchmarks']['tokens_per_second']}")
```

## FastAPI Integration

Augment Adam includes a FastAPI server that automatically applies hardware optimization:

```bash
# Start the server
python -m augment_adam.server

# The server will be available at http://localhost:8000
```

The server provides endpoints for:

- Creating models with optimal settings
- Creating agents with optimized models
- Generating text and chat responses
- Getting hardware information
- Listing available models and agents

## Best Practices

1. **Run Benchmarks First**: Always run benchmarks to understand your hardware capabilities
2. **Start Small**: Begin with smaller models and increase size if performance is acceptable
3. **Monitor Memory Usage**: Watch memory usage to avoid swapping
4. **Adjust Batch Size**: Decrease batch size if you encounter memory issues
5. **Use Quantization**: Enable 4-bit or 8-bit quantization for larger models
6. **Enable Caching**: Always use caching for better performance

## Example: Optimizing for Different Hardware

### Low-End Hardware (e.g., laptop with 8GB RAM)

```python
# Optimal settings for low-end hardware
settings = {
    "model_type": "huggingface",
    "model_size": "small",
    "load_in_8bit": True,
    "use_monte_carlo": True,
    "monte_carlo_particles": 50,
    "use_parallel_monte_carlo": True,
    "monte_carlo_workers": 2
}
```

### Mid-Range Hardware (e.g., desktop with 16GB RAM, GPU)

```python
# Optimal settings for mid-range hardware
settings = {
    "model_type": "huggingface",
    "model_size": "small_context",
    "device": "cuda",
    "use_monte_carlo": True,
    "monte_carlo_particles": 100,
    "use_parallel_monte_carlo": True,
    "monte_carlo_workers": 4,
    "use_gpu_monte_carlo": True
}
```

### High-End Hardware (e.g., server with 64GB RAM, multiple GPUs)

```python
# Optimal settings for high-end hardware
settings = {
    "model_type": "huggingface",
    "model_size": "medium_context",
    "device": "cuda",
    "use_flash_attention": True,
    "use_bettertransformer": True,
    "use_monte_carlo": True,
    "monte_carlo_particles": 200,
    "use_parallel_monte_carlo": True,
    "monte_carlo_workers": 8,
    "use_gpu_monte_carlo": True
}
```

## Conclusion

By leveraging hardware optimization and model analysis, you can get the best performance from Augment Adam on your specific hardware. This approach allows you to use smaller models effectively, even on limited hardware, while still achieving high-quality results.
