# GPU-Accelerated Test Generation

This document explains how to use GPU acceleration for test generation in the Dukat project.

## Prerequisites

- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- NVIDIA Container Toolkit (nvidia-docker2) installed
- Docker and Docker Compose

## Setup

The test generation environment is configured to automatically detect and use NVIDIA GPUs if available. The setup script will:

1. Check if an NVIDIA GPU is available
2. Enable GPU support in the Docker Compose configuration
3. Build the Docker images with CUDA support
4. Pull the necessary Ollama models
5. Verify GPU support in the containers

To set up the environment, run:

```bash
cd augment-adam
./scripts/setup_test_gen.sh
```

## Verifying GPU Support

You can verify that GPU acceleration is working correctly by running:

```bash
docker-compose -f docker-compose.test-gen.yml run --rm test-generator python /app/scripts/verify_gpu.py
```

This script will check:
- If the NVIDIA GPU is detected at the system level
- If PyTorch can access the GPU
- If Ollama can use the GPU for inference

## GPU Configuration

The Docker Compose configuration includes the following GPU-related settings:

### For the Ollama service:

```yaml
deploy:
  resources:
    limits:
      memory: 16G
    reservations:
      memory: 8G
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### For the test-generator service:

```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## Models and GPU Memory Requirements

Different models have different GPU memory requirements:

- **TinyLlama (1.1B)**: ~2GB VRAM
- **CodeLlama (7B)**: ~14GB VRAM
- **WizardCoder (15B)**: ~30GB VRAM

Choose the appropriate model based on your GPU's memory capacity.

## Troubleshooting

If you encounter issues with GPU acceleration:

1. Verify that the NVIDIA Container Toolkit is installed:
   ```bash
   nvidia-container-cli --version
   ```

2. Check that Docker can access the GPU:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
   ```

3. Ensure your GPU has enough memory for the model you're trying to use.

4. Check the Ollama logs for any GPU-related errors:
   ```bash
   docker-compose -f docker-compose.test-gen.yml logs ollama
   ```

5. If PyTorch cannot access the GPU, try reinstalling it with the correct CUDA version:
   ```bash
   pip uninstall -y torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

## Performance Considerations

- GPU acceleration provides significant speedup for model inference, especially for larger models
- The first run may be slower due to model loading and CUDA initialization
- For small models or simple test generation tasks, the CPU may be sufficient
