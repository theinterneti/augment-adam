# Using Small Models with Large Context Windows

This guide explains how to use small models with large context windows in Augment Adam, leveraging our Monte Carlo approach for better performance.

## Introduction

Traditional language models face a trade-off between model size and context window size. Larger models typically have better reasoning capabilities but require more computational resources, while smaller models are more efficient but may have limited capabilities.

Augment Adam addresses this challenge by:

1. Supporting small models with large context windows
2. Using Sequential Monte Carlo (SMC) techniques to enhance the capabilities of smaller models
3. Implementing efficient caching to improve performance
4. Providing advanced context management to make the most of available context windows

## Recommended Small Models with Large Context Windows

We recommend the following small models with large context windows:

| Model Size     | Hugging Face Model     | Ollama Model | Context Window |
| -------------- | ---------------------- | ------------ | -------------- |
| tiny_context   | Qwen/Qwen1.5-0.5B-Chat | qwen:0.5b    | 32K tokens     |
| small_context  | Qwen/Qwen1.5-0.5B-Chat | qwen:0.5b    | 32K tokens     |
| medium_context | Qwen/Qwen1.5-1.8B-Chat | qwen:1.8b    | 32K tokens     |
| long_context   | Qwen/Qwen1.5-7B-Chat   | qwen:7b      | 32K tokens     |

## Monte Carlo Approach

Our Sequential Monte Carlo (SMC) approach enhances the capabilities of smaller models by:

1. **Guided Generation**: Using potential functions to guide the model's generation process
2. **Multiple Candidates**: Exploring multiple generation paths simultaneously
3. **Weighted Sampling**: Prioritizing high-quality generation paths
4. **Batch Processing**: Efficiently processing tokens in batches
5. **Early Stopping**: Stopping generation when no improvement is detected

This approach allows smaller models to produce higher-quality outputs by leveraging domain-specific knowledge and constraints.

## Using Small Models with Large Context Windows

### Command Line Example

```bash
python -m examples.agent_core_example \
  --model-type huggingface \
  --model-size small_context \
  --use-cache \
  --use-monte-carlo \
  --monte-carlo-particles 100 \
  --agent conversational
```

### Python API Example

```python
from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential

# Create a small model with large context window
model = create_model(
    model_type="huggingface",
    model_size="small_context",
    use_cache=True,
    use_monte_carlo=True,
    monte_carlo_particles=100
)

# Create potentials for guided generation
potentials = [
    RegexPotential(
        pattern=r".*[.!?]$",
        name="sentence_ending_potential"
    )
]

# Create an agent using the model
agent = create_agent(
    agent_type="conversational",
    name="Conversational Agent",
    description="A conversational AI agent",
    model=model,
    potentials=potentials
)

# Generate a response
response = agent.generate("Tell me about the benefits of small models with large context windows.")
print(response)
```

## Caching System

Augment Adam includes a caching system that improves performance by:

1. **Model Caching**: Caching model weights and tokenizers
2. **Generation Caching**: Caching generated text for repeated prompts
3. **Embedding Caching**: Caching embeddings for repeated texts
4. **Named Volumes**: Using Docker named volumes for persistent caching

### Docker Compose Setup

```yaml
version: "3"

services:
  augment-adam:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./:/app
      - model-cache:/cache
    environment:
      - AUGMENT_CACHE_DIR=/cache
      - HF_TOKEN=${HF_TOKEN}
    ports:
      - "8000:8000"
    command: python -m augment_adam.server

volumes:
  model-cache:
    name: augment-adam-model-cache
```

## Advanced Context Management

To make the most of large context windows with smaller models, Augment Adam provides:

1. **Intelligent Chunking**: Breaking large documents into meaningful chunks
2. **Context Composition**: Combining relevant chunks for a coherent context
3. **Context Optimization**: Optimizing context to fit within the model's context window
4. **Relevance Scoring**: Prioritizing the most relevant information

## Parallel Processing

To further enhance performance, Augment Adam supports parallel processing for Monte Carlo sampling:

```bash
python -m examples.agent_core_example \
  --model-type huggingface \
  --model-size small_context \
  --use-cache \
  --use-monte-carlo \
  --use-parallel-monte-carlo \
  --monte-carlo-workers 4 \
  --monte-carlo-particles 100 \
  --agent conversational
```

Parallel processing distributes particle generation and evaluation across multiple CPU cores or GPU threads, significantly improving performance. This allows us to use more particles and explore more possibilities in the same amount of time.

For more details, see the [Parallel Monte Carlo Processing](parallel_monte_carlo.md) guide.

## Best Practices

1. **Use Quantization**: Enable 4-bit or 8-bit quantization for even more efficiency
2. **Tune Potentials**: Create domain-specific potentials for your use case
3. **Adjust Particle Count**: Use more particles for more complex tasks
4. **Enable Parallel Processing**: Use multiple cores or GPU for faster generation
5. **Enable Caching**: Always use caching for better performance
6. **Use Flash Attention**: Enable Flash Attention for faster inference on GPU

## Conclusion

By combining small models with large context windows and our Monte Carlo approach, Augment Adam provides a powerful and efficient solution for a wide range of AI applications. This approach allows you to get better performance from smaller models, reducing computational requirements while maintaining high-quality outputs.
