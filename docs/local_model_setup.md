# Local Model Setup for Test Automation

## Overview

This document provides instructions for setting up local open-source models to automate test generation for the Dukat project. Our goal is to use only open-source local models rather than cloud-based services, ensuring privacy and reducing dependency on external APIs.

## 1. Resource Assessment

First, we need to assess the available resources in the development environment to determine which models can run effectively.

```bash
# Check available CPU resources
lscpu

# Check available memory
free -h

# Check available disk space
df -h

# Check if NVIDIA GPU is available and its specifications
nvidia-smi

# If you have an AMD GPU, check its status
rocm-smi
```

## 2. Docker Configuration Assessment

Evaluate the current Docker configuration to ensure it can support local model execution:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# View current Docker resource limits
docker info | grep -i "memory\|cpu\|gpu"

# Check if Docker can access GPUs
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## 3. Recommended Local Models for Test Generation

Based on typical development machine specifications, here are recommended models for different aspects of test automation:

### Small Models (2-4GB VRAM/RAM)
- **TinyLlama (1.1B)**: Good for simple code completion and basic test scaffolding
- **Phi-2 (2.7B)**: Microsoft's model with good reasoning for simple test cases
- **Gemma-2B**: Google's efficient small model with good code understanding

### Medium Models (8-16GB VRAM/RAM)
- **CodeLlama-7B**: Meta's code-specialized model, good for test generation
- **Mistral-7B**: Strong general reasoning with good code capabilities
- **Gemma-7B**: Google's model with good instruction following

### Large Models (24GB+ VRAM/RAM)
- **CodeLlama-13B**: Better reasoning and test generation capabilities
- **Llama-3-8B**: Strong general reasoning with good code understanding
- **WizardCoder-15B**: Specialized for code generation and understanding

## 4. Docker Configuration Updates

Update the Docker configuration to support local model execution:

```yaml
# Example docker-compose.yml modifications
version: '3'
services:
  dukat-dev:
    image: dukat-dev:latest
    volumes:
      - .:/workspace
      - ./models:/models  # Mount a volume for storing models
    environment:
      - OLLAMA_HOST=http://ollama:11434
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ollama_data:
```

## 5. Model Setup with Ollama

[Ollama](https://ollama.ai/) provides an easy way to run local models. Set up the recommended models:

```bash
# Install Ollama (if not using Docker)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models for test generation
ollama pull codellama:7b
ollama pull mistral:7b
ollama pull wizardcoder:15b

# For smaller systems
ollama pull tinyllama:1.1b
ollama pull phi2
```

## 6. Test Automation Integration

Update the Dukat configuration to use local models for test generation:

```python
# Example configuration in dukat/config.py
TEST_GENERATION_CONFIG = {
    "model_name": "codellama:7b",  # Use a smaller model if resources are limited
    "ollama_host": "http://ollama:11434",  # Or "http://localhost:11434" if not using Docker
    "temperature": 0.2,  # Lower temperature for more deterministic outputs
    "max_tokens": 2048,  # Adjust based on test complexity
}
```

## 7. Test Generation Tools Integration

Integrate with open-source test generation tools:

### Pynguin Integration

[Pynguin](https://github.com/se2p/pynguin) is an open-source test generator for Python:

```bash
# Install Pynguin
pip install pynguin

# Create a script to automate Pynguin test generation
cat > scripts/generate_pynguin_tests.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def generate_tests(module_path, output_dir):
    """Generate tests using Pynguin for the specified module."""
    project_root = Path(module_path).parent
    module_name = Path(module_path).stem
    
    cmd = [
        "pynguin",
        "--project-path", str(project_root),
        "--output-path", output_dir,
        "--module-name", module_name,
        "--algorithm", "DYNAMOSA",
        "--assertion-generation", "MUTATION",
        "--population", "50",
        "--budget", "60"
    ]
    
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_pynguin_tests.py <module_path> <output_dir>")
        sys.exit(1)
    
    generate_tests(sys.argv[1], sys.argv[2])
EOF

chmod +x scripts/generate_pynguin_tests.py
```

### Hypothesis Integration

[Hypothesis](https://github.com/HypothesisWorks/hypothesis) for property-based testing:

```bash
# Install Hypothesis
pip install hypothesis

# Create a template for property-based tests
cat > templates/hypothesis_test_template.py << 'EOF'
from hypothesis import given, strategies as st
import hypothesis.strategies as st
from {module_path} import {class_name}

class Test{class_name}:
    @given(st.integers(), st.integers())
    def test_{method_name}_properties(self, a, b):
        """Test properties of {method_name} using Hypothesis."""
        instance = {class_name}()
        result = instance.{method_name}(a, b)
        # Add assertions based on expected properties
EOF
```

## 8. Combined Approach for Test Generation

Create a script that combines LLM-based test generation with traditional tools:

```bash
cat > scripts/generate_tests.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

def generate_tests(source_file, output_dir, use_llm=True, use_pynguin=True, use_hypothesis=True):
    """Generate tests using multiple approaches."""
    module_name = Path(source_file).stem
    project_root = Path(source_file).parent
    
    os.makedirs(output_dir, exist_ok=True)
    
    if use_llm:
        print(f"Generating tests using local LLM for {source_file}...")
        # Call your LLM-based test generator here
        subprocess.run([
            "python", "-m", "dukat.tools.generate_tests",
            "--source-file", source_file,
            "--output-file", f"{output_dir}/test_{module_name}_llm.py"
        ])
    
    if use_pynguin:
        print(f"Generating tests using Pynguin for {source_file}...")
        subprocess.run([
            "pynguin",
            "--project-path", str(project_root),
            "--output-path", output_dir,
            "--module-name", module_name,
            "--algorithm", "DYNAMOSA",
            "--assertion-generation", "MUTATION",
            "--population", "50",
            "--budget", "60"
        ])
    
    if use_hypothesis:
        print(f"Generating property-based tests for {source_file}...")
        # Generate Hypothesis-based tests
        # This would typically involve analyzing the source file and generating
        # appropriate property-based tests
        
    print(f"All tests generated in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tests using multiple approaches")
    parser.add_argument("source_file", help="Path to the source file")
    parser.add_argument("output_dir", help="Directory to output generated tests")
    parser.add_argument("--no-llm", action="store_false", dest="use_llm", help="Skip LLM-based test generation")
    parser.add_argument("--no-pynguin", action="store_false", dest="use_pynguin", help="Skip Pynguin test generation")
    parser.add_argument("--no-hypothesis", action="store_false", dest="use_hypothesis", help="Skip Hypothesis test generation")
    
    args = parser.parse_args()
    generate_tests(args.source_file, args.output_dir, args.use_llm, args.use_pynguin, args.use_hypothesis)
EOF

chmod +x scripts/generate_tests.py
```

## 9. Monitoring and Optimization

Set up monitoring to track resource usage during test generation:

```bash
# Create a monitoring script
cat > scripts/monitor_resources.sh << 'EOF'
#!/bin/bash
# Simple resource monitoring during test generation

echo "Starting resource monitoring..."
echo "Press Ctrl+C to stop monitoring"

while true; do
    echo "======== $(date) ========"
    echo "CPU Usage:"
    top -bn1 | head -20
    echo ""
    echo "Memory Usage:"
    free -h
    echo ""
    echo "GPU Usage (if available):"
    nvidia-smi || echo "No NVIDIA GPU detected"
    echo ""
    sleep 5
done
EOF

chmod +x scripts/monitor_resources.sh
```

## Next Steps

1. Run the resource assessment commands to determine your system capabilities
2. Update Docker configuration based on your available resources
3. Pull appropriate models using Ollama
4. Integrate the test generation tools into your workflow
5. Create a CI pipeline that automatically generates and runs tests

By following these steps, you'll have a fully local, open-source test generation system that can help automate the creation of comprehensive tests for your codebase.
