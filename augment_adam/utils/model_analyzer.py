"""Model performance analyzer.

This module provides utilities for analyzing and comparing model performance
across different tasks and configurations.

Version: 0.1.0
Created: 2025-04-29
"""

import logging
import os
import json
import time
import csv
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from tqdm import tqdm

from augment_adam.models import create_model
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential
from augment_adam.ai_agent.smc.advanced_potentials import (
    StylePotential, CONVERSATIONAL_STYLE, TECHNICAL_STYLE
)

logger = logging.getLogger(__name__)


class ModelAnalyzer:
    """Model performance analyzer.
    
    This class provides methods for analyzing and comparing model performance
    across different tasks and configurations.
    
    Attributes:
        results_dir: Directory to store results
        models_to_test: List of models to test
        tasks: List of tasks to test
    """
    
    def __init__(
        self,
        results_dir: str = "model_analysis_results",
        models_to_test: Optional[List[Dict[str, Any]]] = None,
        tasks: Optional[List[str]] = None
    ):
        """Initialize the Model Analyzer.
        
        Args:
            results_dir: Directory to store results
            models_to_test: List of models to test
            tasks: List of tasks to test
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Default models to test if none provided
        self.models_to_test = models_to_test or [
            {"type": "huggingface", "size": "small"},
            {"type": "huggingface", "size": "small_context"},
            {"type": "huggingface", "size": "medium"},
            {"type": "huggingface", "size": "medium_context"},
            {"type": "ollama", "size": "small"},
            {"type": "ollama", "size": "medium"}
        ]
        
        # Default tasks to test if none provided
        self.tasks = tasks or [
            "text_generation",
            "conversation",
            "code_generation",
            "summarization"
        ]
        
        # Load test data
        self.test_data = self._load_test_data()
        
        logger.info(f"Initialized Model Analyzer with {len(self.models_to_test)} models and {len(self.tasks)} tasks")
    
    def _load_test_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load test data for different tasks.
        
        Returns:
            Dictionary mapping task names to lists of test examples
        """
        # Default test data
        test_data = {
            "text_generation": [
                {"prompt": "Write a short story about a robot learning to feel emotions.", "max_tokens": 200},
                {"prompt": "Explain the concept of quantum computing to a high school student.", "max_tokens": 150},
                {"prompt": "Describe the process of photosynthesis in plants.", "max_tokens": 150}
            ],
            "conversation": [
                {"messages": [{"role": "user", "content": "Hello, how are you today?"}]},
                {"messages": [{"role": "user", "content": "Can you help me plan a birthday party for my 10-year-old?"}]},
                {"messages": [{"role": "user", "content": "What are some good books to read about artificial intelligence?"}]}
            ],
            "code_generation": [
                {"prompt": "Write a Python function to find the Fibonacci sequence up to n.", "max_tokens": 150},
                {"prompt": "Create a simple React component that displays a counter with increment and decrement buttons.", "max_tokens": 200},
                {"prompt": "Write a SQL query to find the top 5 customers who have spent the most money.", "max_tokens": 100}
            ],
            "summarization": [
                {"text": "The field of artificial intelligence has seen rapid advancement in recent years, with breakthroughs in natural language processing, computer vision, and reinforcement learning. These advancements have led to the development of systems that can understand and generate human language, recognize objects and faces in images, and learn to play complex games at superhuman levels. However, these developments also raise important ethical questions about privacy, bias, and the future of work. As AI systems become more integrated into our daily lives, it is crucial to ensure they are developed and deployed in ways that benefit humanity while minimizing potential harms.", "max_tokens": 50},
                {"text": "Climate change is one of the most pressing challenges facing humanity today. Rising global temperatures due to greenhouse gas emissions are leading to more frequent and severe weather events, rising sea levels, and disruptions to ecosystems worldwide. Addressing this challenge requires coordinated action at local, national, and international levels, including transitioning to renewable energy sources, improving energy efficiency, and developing sustainable agricultural practices. While the scale of the challenge is daunting, there are also opportunities for innovation and economic growth in the transition to a low-carbon economy.", "max_tokens": 50}
            ]
        }
        
        # Try to load custom test data if available
        try:
            custom_data_path = os.path.join(self.results_dir, "test_data.json")
            if os.path.exists(custom_data_path):
                with open(custom_data_path, "r") as f:
                    custom_data = json.load(f)
                
                # Merge custom data with default data
                for task, examples in custom_data.items():
                    if task in test_data:
                        test_data[task].extend(examples)
                    else:
                        test_data[task] = examples
                
                logger.info(f"Loaded custom test data from {custom_data_path}")
        except Exception as e:
            logger.warning(f"Failed to load custom test data: {e}")
        
        return test_data
    
    def save_test_data(self) -> None:
        """Save current test data to file."""
        try:
            data_path = os.path.join(self.results_dir, "test_data.json")
            with open(data_path, "w") as f:
                json.dump(self.test_data, f, indent=2)
            
            logger.info(f"Saved test data to {data_path}")
        except Exception as e:
            logger.error(f"Failed to save test data: {e}")
    
    def add_test_example(self, task: str, example: Dict[str, Any]) -> None:
        """Add a test example for a specific task.
        
        Args:
            task: Task name
            example: Test example
        """
        if task not in self.test_data:
            self.test_data[task] = []
        
        self.test_data[task].append(example)
        logger.info(f"Added test example for task '{task}'")
        
        # Save updated test data
        self.save_test_data()
    
    def analyze_model(
        self,
        model_type: str,
        model_size: str,
        tasks: Optional[List[str]] = None,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """Analyze a specific model across different tasks.
        
        Args:
            model_type: Type of model
            model_size: Size of model
            tasks: List of tasks to test (if None, use all tasks)
            save_results: Whether to save results to file
            
        Returns:
            Dictionary with analysis results
        """
        tasks = tasks or self.tasks
        
        # Get optimal settings for this model
        settings = get_optimal_model_settings(model_type, model_size)
        
        # Create model
        try:
            start_time = time.time()
            model = create_model(
                model_type=model_type,
                model_size=model_size,
                **settings
            )
            load_time = time.time() - start_time
            
            # Initialize results
            results = {
                "model_type": model_type,
                "model_size": model_size,
                "settings": settings,
                "load_time": load_time,
                "tasks": {}
            }
            
            # Add model info
            if hasattr(model, "get_model_info"):
                results["model_info"] = model.get_model_info()
            
            # Test each task
            for task in tasks:
                if task not in self.test_data:
                    logger.warning(f"No test data for task '{task}', skipping")
                    continue
                
                task_results = self._test_task(model, task)
                results["tasks"][task] = task_results
            
            # Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics(results)
            results["overall_metrics"] = overall_metrics
            
            # Save results if requested
            if save_results:
                self._save_model_results(results)
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to analyze model {model_type}/{model_size}: {e}")
            return {
                "model_type": model_type,
                "model_size": model_size,
                "settings": settings,
                "error": str(e)
            }
    
    def _test_task(self, model: Any, task: str) -> Dict[str, Any]:
        """Test a model on a specific task.
        
        Args:
            model: Model to test
            task: Task to test
            
        Returns:
            Dictionary with task results
        """
        examples = self.test_data[task]
        results = {
            "examples": []
        }
        
        total_time = 0
        total_tokens = 0
        
        for example in examples:
            try:
                # Process example based on task type
                if task == "text_generation":
                    start_time = time.time()
                    output = model.generate(
                        prompt=example["prompt"],
                        max_tokens=example.get("max_tokens", 100)
                    )
                    process_time = time.time() - start_time
                    
                    # Estimate token count (rough approximation)
                    token_count = len(output.split())
                    
                    example_result = {
                        "prompt": example["prompt"],
                        "output": output,
                        "time": process_time,
                        "tokens": token_count,
                        "tokens_per_second": token_count / process_time if process_time > 0 else 0
                    }
                
                elif task == "conversation":
                    # Create a conversational agent
                    agent = create_agent(
                        agent_type="conversational",
                        name="Test Agent",
                        description="A test agent",
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
                    
                    # Process conversation
                    start_time = time.time()
                    response = agent.process(example["messages"][0]["content"])
                    process_time = time.time() - start_time
                    
                    # Estimate token count
                    token_count = len(response["response"].split())
                    
                    example_result = {
                        "messages": example["messages"],
                        "response": response["response"],
                        "time": process_time,
                        "tokens": token_count,
                        "tokens_per_second": token_count / process_time if process_time > 0 else 0
                    }
                
                elif task == "code_generation":
                    # Create a coding agent
                    agent = create_agent(
                        agent_type="coding",
                        name="Test Agent",
                        description="A test agent",
                        model=model,
                        potentials=[
                            RegexPotential(
                                pattern=r"(def |class |import |from |if |for |while |return |with |try |except |finally )",
                                name="code_keyword_potential"
                            ),
                            StylePotential(
                                style_patterns=TECHNICAL_STYLE,
                                name="technical_style_potential"
                            )
                        ]
                    )
                    
                    # Process code generation
                    start_time = time.time()
                    response = agent.process(example["prompt"])
                    process_time = time.time() - start_time
                    
                    # Estimate token count
                    token_count = len(response["response"].split())
                    
                    example_result = {
                        "prompt": example["prompt"],
                        "code": response["response"],
                        "time": process_time,
                        "tokens": token_count,
                        "tokens_per_second": token_count / process_time if process_time > 0 else 0
                    }
                
                elif task == "summarization":
                    start_time = time.time()
                    summary = model.generate(
                        prompt=f"Summarize the following text:\n\n{example['text']}\n\nSummary:",
                        max_tokens=example.get("max_tokens", 50)
                    )
                    process_time = time.time() - start_time
                    
                    # Estimate token count
                    token_count = len(summary.split())
                    
                    example_result = {
                        "text": example["text"],
                        "summary": summary,
                        "time": process_time,
                        "tokens": token_count,
                        "tokens_per_second": token_count / process_time if process_time > 0 else 0
                    }
                
                else:
                    # Unknown task
                    logger.warning(f"Unknown task '{task}', skipping example")
                    continue
                
                # Add example result
                results["examples"].append(example_result)
                
                # Update totals
                total_time += process_time
                total_tokens += token_count
            
            except Exception as e:
                logger.error(f"Failed to process example for task '{task}': {e}")
                results["examples"].append({
                    "error": str(e)
                })
        
        # Calculate task metrics
        results["metrics"] = {
            "total_time": total_time,
            "total_tokens": total_tokens,
            "average_time_per_example": total_time / len(examples) if examples else 0,
            "average_tokens_per_second": total_tokens / total_time if total_time > 0 else 0
        }
        
        return results
    
    def _calculate_overall_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall metrics from task results.
        
        Args:
            results: Results dictionary
            
        Returns:
            Dictionary with overall metrics
        """
        total_time = 0
        total_tokens = 0
        total_examples = 0
        
        for task, task_results in results["tasks"].items():
            if "metrics" in task_results:
                total_time += task_results["metrics"]["total_time"]
                total_tokens += task_results["metrics"]["total_tokens"]
                total_examples += len(task_results["examples"])
        
        return {
            "total_time": total_time,
            "total_tokens": total_tokens,
            "total_examples": total_examples,
            "average_time_per_example": total_time / total_examples if total_examples > 0 else 0,
            "average_tokens_per_second": total_tokens / total_time if total_time > 0 else 0,
            "load_time": results["load_time"]
        }
    
    def _save_model_results(self, results: Dict[str, Any]) -> None:
        """Save model analysis results to file.
        
        Args:
            results: Results dictionary
        """
        try:
            # Create model-specific directory
            model_dir = os.path.join(
                self.results_dir,
                f"{results['model_type']}_{results['model_size']}"
            )
            os.makedirs(model_dir, exist_ok=True)
            
            # Save full results
            results_path = os.path.join(model_dir, "results.json")
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            
            # Save summary
            summary_path = os.path.join(model_dir, "summary.json")
            summary = {
                "model_type": results["model_type"],
                "model_size": results["model_size"],
                "settings": results["settings"],
                "overall_metrics": results["overall_metrics"],
                "task_metrics": {
                    task: task_results["metrics"]
                    for task, task_results in results["tasks"].items()
                    if "metrics" in task_results
                }
            }
            
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Saved model results to {model_dir}")
        except Exception as e:
            logger.error(f"Failed to save model results: {e}")
    
    def run_analysis(self, save_csv: bool = True) -> Dict[str, Any]:
        """Run analysis on all models and tasks.
        
        Args:
            save_csv: Whether to save results as CSV
            
        Returns:
            Dictionary with analysis results
        """
        all_results = {}
        
        for model_config in tqdm(self.models_to_test, desc="Analyzing models"):
            model_type = model_config["type"]
            model_size = model_config["size"]
            
            logger.info(f"Analyzing model {model_type}/{model_size}")
            
            results = self.analyze_model(
                model_type=model_type,
                model_size=model_size,
                save_results=True
            )
            
            all_results[f"{model_type}_{model_size}"] = results
        
        # Save comparison CSV if requested
        if save_csv:
            self._save_comparison_csv(all_results)
        
        return all_results
    
    def _save_comparison_csv(self, all_results: Dict[str, Dict[str, Any]]) -> None:
        """Save comparison of all models as CSV.
        
        Args:
            all_results: Dictionary mapping model names to results
        """
        try:
            # Create CSV file
            csv_path = os.path.join(self.results_dir, "model_comparison.csv")
            
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                
                # Write header
                header = ["Model", "Type", "Size", "Load Time (s)", "Total Time (s)", 
                          "Total Tokens", "Tokens/Second"]
                
                # Add task-specific headers
                for task in self.tasks:
                    header.extend([
                        f"{task} Time (s)",
                        f"{task} Tokens",
                        f"{task} Tokens/Second"
                    ])
                
                writer.writerow(header)
                
                # Write data for each model
                for model_name, results in all_results.items():
                    row = [
                        model_name,
                        results["model_type"],
                        results["model_size"],
                        round(results["load_time"], 2),
                        round(results["overall_metrics"]["total_time"], 2),
                        results["overall_metrics"]["total_tokens"],
                        round(results["overall_metrics"]["average_tokens_per_second"], 2)
                    ]
                    
                    # Add task-specific metrics
                    for task in self.tasks:
                        if task in results["tasks"] and "metrics" in results["tasks"][task]:
                            metrics = results["tasks"][task]["metrics"]
                            row.extend([
                                round(metrics["total_time"], 2),
                                metrics["total_tokens"],
                                round(metrics["average_tokens_per_second"], 2)
                            ])
                        else:
                            row.extend(["N/A", "N/A", "N/A"])
                    
                    writer.writerow(row)
            
            logger.info(f"Saved model comparison to {csv_path}")
        except Exception as e:
            logger.error(f"Failed to save comparison CSV: {e}")
    
    def get_best_models(self, metric: str = "average_tokens_per_second", top_n: int = 3) -> List[Dict[str, Any]]:
        """Get the best performing models based on a specific metric.
        
        Args:
            metric: Metric to use for ranking
            top_n: Number of top models to return
            
        Returns:
            List of top models with their metrics
        """
        # Load all results
        all_results = {}
        
        for model_config in self.models_to_test:
            model_type = model_config["type"]
            model_size = model_config["size"]
            model_name = f"{model_type}_{model_size}"
            
            # Try to load results
            try:
                results_path = os.path.join(
                    self.results_dir,
                    model_name,
                    "summary.json"
                )
                
                if os.path.exists(results_path):
                    with open(results_path, "r") as f:
                        results = json.load(f)
                    
                    all_results[model_name] = results
            except Exception as e:
                logger.warning(f"Failed to load results for {model_name}: {e}")
        
        # Rank models based on metric
        ranked_models = []
        
        for model_name, results in all_results.items():
            if "overall_metrics" in results and metric in results["overall_metrics"]:
                ranked_models.append({
                    "name": model_name,
                    "type": results["model_type"],
                    "size": results["model_size"],
                    "metric_value": results["overall_metrics"][metric],
                    "overall_metrics": results["overall_metrics"]
                })
        
        # Sort by metric (higher is better)
        ranked_models.sort(key=lambda x: x["metric_value"], reverse=True)
        
        # Return top N
        return ranked_models[:top_n]
    
    def get_task_specific_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get task-specific model recommendations.
        
        Returns:
            Dictionary mapping tasks to lists of recommended models
        """
        recommendations = {}
        
        for task in self.tasks:
            # Load all results
            task_results = []
            
            for model_config in self.models_to_test:
                model_type = model_config["type"]
                model_size = model_config["size"]
                model_name = f"{model_type}_{model_size}"
                
                # Try to load results
                try:
                    results_path = os.path.join(
                        self.results_dir,
                        model_name,
                        "summary.json"
                    )
                    
                    if os.path.exists(results_path):
                        with open(results_path, "r") as f:
                            results = json.load(f)
                        
                        if "task_metrics" in results and task in results["task_metrics"]:
                            task_results.append({
                                "name": model_name,
                                "type": results["model_type"],
                                "size": results["model_size"],
                                "metric_value": results["task_metrics"][task]["average_tokens_per_second"],
                                "task_metrics": results["task_metrics"][task]
                            })
                except Exception as e:
                    logger.warning(f"Failed to load results for {model_name}: {e}")
            
            # Sort by metric (higher is better)
            task_results.sort(key=lambda x: x["metric_value"], reverse=True)
            
            # Add to recommendations
            recommendations[task] = task_results[:3]  # Top 3
        
        return recommendations
