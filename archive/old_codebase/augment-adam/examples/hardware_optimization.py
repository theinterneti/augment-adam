#!/usr/bin/env python
"""Hardware optimization and model analysis example.

This script demonstrates how to use the hardware optimizer and model analyzer
to find the best models and configurations for your hardware.

Usage:
    python -m examples.hardware_optimization [--analyze-models] [--benchmark] [--optimize]

Options:
    --analyze-models    Run full model analysis (may take a long time)
    --benchmark         Run hardware benchmark
    --optimize          Generate optimized settings for models
"""

import argparse
import logging
import json
import os
from typing import Dict, List, Any, Optional

from augment_adam.utils.hardware_optimizer import (
    get_hardware_info, get_optimal_model_settings,
    get_optimal_monte_carlo_settings, benchmark_hardware,
    save_hardware_profile
)
from augment_adam.utils.model_analyzer import ModelAnalyzer
from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential
from augment_adam.ai_agent.smc.advanced_potentials import (
    StylePotential, CONVERSATIONAL_STYLE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_hardware_info():
    """Print hardware information."""
    hw_info = get_hardware_info()
    
    print("\n===== HARDWARE INFORMATION =====")
    print(f"CPU: {hw_info['cpu']['processor']} ({hw_info['cpu']['cores_physical']} physical cores, {hw_info['cpu']['cores_logical']} logical cores)")
    
    memory_gb = hw_info["memory"]["total"] / (1024 ** 3)
    print(f"Memory: {memory_gb:.1f} GB")
    
    if hw_info["gpu"]["available"]:
        print("\nGPU Information:")
        for i, (name, memory) in enumerate(zip(hw_info["gpu"]["names"], hw_info["gpu"]["memory"])):
            memory_gb = memory / (1024 ** 3)
            print(f"  GPU {i}: {name} ({memory_gb:.1f} GB)")
    elif hw_info["gpu"].get("mps_available", False):
        print("\nApple Silicon GPU (MPS) available")
    else:
        print("\nNo GPU detected")
    
    print(f"\nOperating System: {hw_info['platform']['system']} {hw_info['platform']['release']}")
    
    disk_gb = hw_info["disk"]["total"] / (1024 ** 3)
    free_disk_gb = hw_info["disk"]["free"] / (1024 ** 3)
    print(f"Disk: {disk_gb:.1f} GB total, {free_disk_gb:.1f} GB free")
    
    # Save hardware profile
    save_hardware_profile("hardware_profile.json")
    print("\nHardware profile saved to hardware_profile.json")


def print_optimal_settings():
    """Print optimal settings for different model sizes."""
    model_sizes = [
        "small", "tiny_context", "small_context", 
        "medium", "medium_context", "large", "long_context", "xl"
    ]
    
    print("\n===== OPTIMAL MODEL SETTINGS =====")
    
    for model_size in model_sizes:
        print(f"\nSettings for {model_size} models:")
        
        # Get settings for Hugging Face
        hf_settings = get_optimal_model_settings("huggingface", model_size)
        print(f"  Hugging Face:")
        for key, value in hf_settings.items():
            print(f"    {key}: {value}")
        
        # Get settings for Ollama
        ollama_settings = get_optimal_model_settings("ollama", model_size)
        print(f"  Ollama:")
        for key, value in ollama_settings.items():
            print(f"    {key}: {value}")


def run_benchmark():
    """Run hardware benchmark."""
    print("\n===== RUNNING HARDWARE BENCHMARK =====")
    print("This will load a small model and run some basic tests...")
    
    results = benchmark_hardware(model_type="huggingface", model_size="small")
    
    print("\nBenchmark Results:")
    print(f"  Model Load Time: {results['benchmarks']['model_load_time']:.2f} seconds")
    print(f"  Generation Time: {results['benchmarks']['generation_time']:.2f} seconds")
    print(f"  Tokens per Second: {results['benchmarks']['tokens_per_second']:.2f}")
    
    if "embedding_time" in results["benchmarks"]:
        print(f"  Embedding Time: {results['benchmarks']['embedding_time']:.2f} seconds")
        print(f"  Embedding Dimensions: {results['benchmarks']['embedding_dimensions']}")
    
    # Save benchmark results
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nBenchmark results saved to benchmark_results.json")


def run_model_analysis():
    """Run model analysis."""
    print("\n===== RUNNING MODEL ANALYSIS =====")
    print("This will analyze multiple models across different tasks.")
    print("Warning: This may take a long time to complete.")
    
    # Create analyzer
    analyzer = ModelAnalyzer(
        results_dir="model_analysis_results",
        models_to_test=[
            {"type": "huggingface", "size": "small"},
            {"type": "huggingface", "size": "small_context"},
            {"type": "huggingface", "size": "medium"},
            {"type": "ollama", "size": "small"}
        ],
        tasks=["text_generation", "conversation", "code_generation"]
    )
    
    # Run analysis
    print("\nAnalyzing models... (this may take a while)")
    results = analyzer.run_analysis()
    
    # Get best models
    best_models = analyzer.get_best_models()
    
    print("\nBest Models Overall:")
    for i, model in enumerate(best_models):
        print(f"  {i+1}. {model['name']}: {model['metric_value']:.2f} tokens/second")
    
    # Get task-specific recommendations
    recommendations = analyzer.get_task_specific_recommendations()
    
    print("\nTask-Specific Recommendations:")
    for task, models in recommendations.items():
        print(f"\n  {task.replace('_', ' ').title()}:")
        for i, model in enumerate(models):
            print(f"    {i+1}. {model['name']}: {model['metric_value']:.2f} tokens/second")
    
    print("\nAnalysis complete. Results saved to model_analysis_results/")


def create_optimized_agent():
    """Create an agent with optimized settings."""
    print("\n===== CREATING OPTIMIZED AGENT =====")
    
    # Get optimal settings for small_context model
    settings = get_optimal_model_settings("huggingface", "small_context")
    
    print("Using the following settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    # Create model
    print("\nCreating model...")
    model = create_model(
        model_type="huggingface",
        model_size="small_context",
        **settings
    )
    
    # Create agent
    print("Creating agent...")
    agent = create_agent(
        agent_type="conversational",
        name="Optimized Agent",
        description="An agent optimized for the current hardware",
        model=model,
        potentials=[
            RegexPotential(
                pattern=r".*[.!?]$",
                name="sentence_ending_potential"
            ),
            StylePotential(
                style_patterns=CONVERSATIONAL_STYLE,
                name="conversational_style_potential"
            )
        ]
    )
    
    # Test agent
    print("\nTesting agent...")
    prompt = "What are the benefits of using small models with large context windows?"
    
    print(f"User: {prompt}")
    response = agent.process(prompt)
    
    print(f"Agent: {response['response']}")
    
    print("\nAgent created and tested successfully!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Hardware optimization and model analysis")
    parser.add_argument("--analyze-models", action="store_true", help="Run full model analysis")
    parser.add_argument("--benchmark", action="store_true", help="Run hardware benchmark")
    parser.add_argument("--optimize", action="store_true", help="Generate optimized settings")
    
    args = parser.parse_args()
    
    # Print hardware information
    print_hardware_info()
    
    # Run benchmark if requested
    if args.benchmark:
        run_benchmark()
    
    # Print optimal settings if requested
    if args.optimize:
        print_optimal_settings()
    
    # Run model analysis if requested
    if args.analyze_models:
        run_model_analysis()
    
    # Create optimized agent
    create_optimized_agent()


if __name__ == "__main__":
    main()
