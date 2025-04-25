"""Complex integration tests for the agent coordination framework."""

import unittest
from unittest.mock import MagicMock, patch
import asyncio
import time
import random

from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep
from augment_adam.models.model_interface import ModelInterface


class SpecializedMockModel(ModelInterface):
    """Specialized mock model for testing complex scenarios."""
    
    def __init__(self, name="specialized_mock_model", specialty=None, delay=0):
        """Initialize the specialized mock model.
        
        Args:
            name: Name of the model
            specialty: Specialty of the model (research, coding, writing, etc.)
            delay: Delay in seconds to simulate processing time
        """
        self.name = name
        self.specialty = specialty
        self.delay = delay
        self.call_count = 0
        self.call_history = []
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt.
        
        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        # Record the call
        self.call_count += 1
        self.call_history.append({
            "prompt": prompt,
            "kwargs": kwargs,
            "timestamp": time.time()
        })
        
        # Simulate processing time
        if self.delay > 0:
            time.sleep(self.delay)
        
        # Generate response based on specialty
        if self.specialty == "research":
            if "fibonacci" in prompt.lower():
                return "Research: The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones. It starts with 0, 1, 1, 2, 3, 5, 8, 13, 21, ..."
            elif "sorting algorithm" in prompt.lower():
                return "Research: Sorting algorithms are used to rearrange elements in a list. Common algorithms include bubble sort, merge sort, quick sort, and heap sort."
            elif "neural network" in prompt.lower():
                return "Research: Neural networks are computing systems inspired by biological neural networks. They consist of layers of nodes (neurons) that process information."
            else:
                return f"Research on: {prompt}"
        
        elif self.specialty == "coding":
            if "fibonacci" in prompt.lower():
                return """```python
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    else:
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
```"""
            elif "sorting" in prompt.lower():
                return """```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```"""
            elif "neural" in prompt.lower():
                return """```python
import numpy as np

class SimpleNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.W1 = np.random.randn(input_size, hidden_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size)
        self.b2 = np.zeros(output_size)
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
```"""
            else:
                return f"Code for: {prompt}"
        
        elif self.specialty == "writing":
            if "fibonacci" in prompt.lower():
                return """# Fibonacci Function Documentation

## Overview
The Fibonacci function generates the Fibonacci sequence up to n numbers.

## Parameters
- n: The number of Fibonacci numbers to generate

## Returns
- A list containing the Fibonacci sequence

## Example
```python
fibonacci(5)  # Returns [0, 1, 1, 2, 3]
```

## Time Complexity
- Time Complexity: O(n)
- Space Complexity: O(n)
"""
            elif "sorting" in prompt.lower():
                return """# Merge Sort Documentation

## Overview
Merge Sort is a divide-and-conquer algorithm that divides the input array into two halves, recursively sorts them, and then merges the sorted halves.

## Parameters
- arr: The array to sort

## Returns
- A sorted array

## Example
```python
merge_sort([3, 1, 4, 1, 5, 9, 2, 6])  # Returns [1, 1, 2, 3, 4, 5, 6, 9]
```

## Time Complexity
- Time Complexity: O(n log n)
- Space Complexity: O(n)
"""
            elif "neural" in prompt.lower():
                return """# Simple Neural Network Documentation

## Overview
This class implements a simple neural network with one hidden layer.

## Parameters
- input_size: Number of input features
- hidden_size: Number of neurons in the hidden layer
- output_size: Number of output neurons

## Methods
- forward(X): Performs forward propagation
- sigmoid(x): Applies the sigmoid activation function

## Example
```python
nn = SimpleNeuralNetwork(10, 5, 1)
output = nn.forward(input_data)
```
"""
            else:
                return f"Documentation for: {prompt}"
        
        elif self.specialty == "review":
            if "fibonacci" in prompt.lower():
                return """Code Review:
1. The function handles edge cases correctly (n <= 0, n == 1, n == 2).
2. The implementation is efficient with O(n) time complexity.
3. Suggestion: Consider using a generator for memory efficiency with large sequences.
4. The function is well-structured and easy to understand.
"""
            elif "sorting" in prompt.lower():
                return """Code Review:
1. The merge sort implementation is correct.
2. The algorithm has the expected O(n log n) time complexity.
3. Suggestion: Consider an in-place implementation to reduce memory usage.
4. The merge function could be optimized by pre-allocating the result array.
"""
            elif "neural" in prompt.lower():
                return """Code Review:
1. The neural network implementation is basic but functional.
2. Suggestion: Add methods for training (backpropagation).
3. Consider adding bias terms to the layers.
4. The activation functions should be more configurable.
"""
            else:
                return f"Review of: {prompt}"
        
        elif self.specialty == "testing":
            if "fibonacci" in prompt.lower():
                return """```python
def test_fibonacci():
    assert fibonacci(0) == []
    assert fibonacci(1) == [0]
    assert fibonacci(2) == [0, 1]
    assert fibonacci(5) == [0, 1, 1, 2, 3]
    assert fibonacci(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    print("All tests passed!")
```"""
            elif "sorting" in prompt.lower():
                return """```python
def test_merge_sort():
    assert merge_sort([]) == []
    assert merge_sort([1]) == [1]
    assert merge_sort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]
    assert merge_sort([-1, -5, 0, 10, 5]) == [-5, -1, 0, 5, 10]
    print("All tests passed!")
```"""
            elif "neural" in prompt.lower():
                return """```python
def test_neural_network():
    nn = SimpleNeuralNetwork(2, 3, 1)
    output = nn.forward(np.array([[0, 0], [0, 1], [1, 0], [1, 1]]))
    assert output.shape == (4, 1)
    assert 0 <= output.all() <= 1  # Output should be between 0 and 1
    print("All tests passed!")
```"""
            else:
                return f"Tests for: {prompt}"
        
        else:
            # Generic response
            return f"Response to: {prompt}"
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [random.random() for _ in range(10)]
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.name,
            "specialty": self.specialty,
            "provider": "Mock",
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10,
            "call_count": self.call_count
        }


class SpecializedMockAgent:
    """Specialized mock agent for testing complex scenarios."""
    
    def __init__(self, name, specialty=None, delay=0, error_rate=0):
        """Initialize the specialized mock agent.
        
        Args:
            name: Name of the agent
            specialty: Specialty of the agent (research, coding, writing, etc.)
            delay: Delay in seconds to simulate processing time
            error_rate: Probability of generating an error (0-1)
        """
        self.name = name
        self.specialty = specialty
        self.delay = delay
        self.error_rate = error_rate
        self.model = SpecializedMockModel(f"{name}_model", specialty, delay)
        self.call_count = 0
        self.call_history = []
    
    def process(self, input_text, context=None):
        """Process input and generate a response.
        
        Args:
            input_text: The input text to process
            context: Additional context
            
        Returns:
            Response dictionary
        """
        # Record the call
        self.call_count += 1
        self.call_history.append({
            "input": input_text,
            "context": context,
            "timestamp": time.time()
        })
        
        # Simulate processing time
        if self.delay > 0:
            time.sleep(self.delay)
        
        # Simulate errors
        if random.random() < self.error_rate:
            raise Exception(f"Error processing input: {input_text}")
        
        # Generate response
        response = self.model.generate(input_text)
        
        return {
            "response": f"{self.name} ({self.specialty}): {response}",
            "processing_time": self.delay,
            "call_count": self.call_count
        }
    
    async def process_async(self, input_text, context=None):
        """Process input asynchronously.
        
        Args:
            input_text: The input text to process
            context: Additional context
            
        Returns:
            Response dictionary
        """
        # Record the call
        self.call_count += 1
        self.call_history.append({
            "input": input_text,
            "context": context,
            "timestamp": time.time(),
            "async": True
        })
        
        # Simulate processing time
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        # Simulate errors
        if random.random() < self.error_rate:
            raise Exception(f"Error processing input: {input_text}")
        
        # Generate response
        response = self.model.generate(input_text)
        
        return {
            "response": f"{self.name} ({self.specialty}): {response}",
            "processing_time": self.delay,
            "call_count": self.call_count,
            "async": True
        }
    
    def get_info(self):
        """Get information about the agent."""
        return {
            "name": self.name,
            "specialty": self.specialty,
            "model": self.model.get_model_info(),
            "call_count": self.call_count
        }


class TestComplexCoordination(unittest.TestCase):
    """Complex integration tests for the agent coordination framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create specialized mock agents
        self.research_agent = SpecializedMockAgent("Research Agent", "research", delay=0.1)
        self.coding_agent = SpecializedMockAgent("Coding Agent", "coding", delay=0.2)
        self.writing_agent = SpecializedMockAgent("Writing Agent", "writing", delay=0.1)
        self.review_agent = SpecializedMockAgent("Review Agent", "review", delay=0.2)
        self.testing_agent = SpecializedMockAgent("Testing Agent", "testing", delay=0.1)
        
        # Create error-prone agent
        self.error_agent = SpecializedMockAgent("Error Agent", "error", delay=0.1, error_rate=0.5)
        
        # Create coordinator
        self.coordinator = AgentCoordinator("Complex Coordinator")
        
        # Register agents
        self.coordinator.register_agent("research", self.research_agent)
        self.coordinator.register_agent("coding", self.coding_agent)
        self.coordinator.register_agent("writing", self.writing_agent)
        self.coordinator.register_agent("review", self.review_agent)
        self.coordinator.register_agent("testing", self.testing_agent)
        self.coordinator.register_agent("error", self.error_agent)
        
        # Create team
        self.team = AgentTeam(
            name="Development Team",
            description="A team for software development",
            coordinator=self.coordinator
        )
        
        # Add roles
        self.team.add_role(
            role_name="researcher",
            agent_id="research",
            description="Researches topics"
        )
        
        self.team.add_role(
            role_name="developer",
            agent_id="coding",
            description="Writes code"
        )
        
        self.team.add_role(
            role_name="technical_writer",
            agent_id="writing",
            description="Creates documentation"
        )
        
        self.team.add_role(
            role_name="code_reviewer",
            agent_id="review",
            description="Reviews code"
        )
        
        self.team.add_role(
            role_name="tester",
            agent_id="testing",
            description="Writes tests"
        )
        
        self.team.add_role(
            role_name="error_handler",
            agent_id="error",
            description="Handles errors"
        )
    
    def test_complex_workflow(self):
        """Test a complex workflow with multiple steps and dependencies."""
        # Define a task
        task = "Implement a Fibonacci sequence generator"
        
        # Create workflow
        workflow = Workflow(
            name="Complex Development Workflow",
            description="Workflow for creating a software component with review and testing"
        )
        
        # Add steps
        workflow.add_process_step(
            role="researcher",
            input=f"Research: {task}",
            description="Research the topic"
        )
        
        workflow.add_message_step(
            from_role="researcher",
            to_role="developer",
            message="Based on this research, please implement: {researcher_result}",
            description="Send research to developer"
        )
        
        workflow.add_message_step(
            from_role="developer",
            to_role="code_reviewer",
            message="Please review this code: {developer_response}",
            description="Send code to reviewer"
        )
        
        workflow.add_message_step(
            from_role="code_reviewer",
            to_role="developer",
            message="Here's my review. Please update the code: {code_reviewer_response}",
            description="Send review to developer"
        )
        
        workflow.add_process_step(
            role="developer",
            input="Update the code based on the review: {code_reviewer_response}",
            description="Update code based on review"
        )
        
        workflow.add_message_step(
            from_role="developer",
            to_role="tester",
            message="Please write tests for this code: {developer_result}",
            description="Send updated code to tester"
        )
        
        workflow.add_message_step(
            from_role="developer",
            to_role="technical_writer",
            message="Please write documentation for this code: {developer_result}",
            description="Send code to technical writer"
        )
        
        # Execute workflow
        result = self.team.execute_workflow(task, workflow.to_list())
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["results"]), 7)
        
        # Check the research step
        self.assertEqual(result["results"][0]["role"], "researcher")
        self.assertEqual(result["results"][0]["action"], "process")
        self.assertIn("Fibonacci sequence", result["results"][0]["output"])
        
        # Check the coding step
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("def fibonacci", result["results"][1]["output"].lower())
        
        # Check the review step
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "send_message")
        self.assertEqual(result["results"][2]["recipient"], "code_reviewer")
        self.assertIn("Code Review", result["results"][2]["output"])
        
        # Check the update step
        self.assertEqual(result["results"][3]["role"], "code_reviewer")
        self.assertEqual(result["results"][3]["action"], "send_message")
        self.assertEqual(result["results"][3]["recipient"], "developer")
        
        # Check the testing step
        self.assertEqual(result["results"][5]["role"], "developer")
        self.assertEqual(result["results"][5]["action"], "send_message")
        self.assertEqual(result["results"][5]["recipient"], "tester")
        self.assertIn("test_fibonacci", result["results"][5]["output"].lower())
        
        # Check the documentation step
        self.assertEqual(result["results"][6]["role"], "developer")
        self.assertEqual(result["results"][6]["action"], "send_message")
        self.assertEqual(result["results"][6]["recipient"], "technical_writer")
        self.assertIn("Documentation", result["results"][6]["output"])
    
    def test_parallel_workflows(self):
        """Test multiple workflows running in parallel."""
        # Define tasks
        tasks = [
            "Implement a Fibonacci sequence generator",
            "Create a merge sort algorithm",
            "Build a simple neural network"
        ]
        
        # Create workflows
        workflows = []
        
        for task in tasks:
            workflow = Workflow(
                name=f"Workflow for {task}",
                description=f"Workflow for {task}"
            )
            
            workflow.add_process_step(
                role="researcher",
                input=f"Research: {task}",
                description="Research the topic"
            )
            
            workflow.add_message_step(
                from_role="researcher",
                to_role="developer",
                message="Based on this research, please implement: {researcher_result}",
                description="Send research to developer"
            )
            
            workflow.add_message_step(
                from_role="developer",
                to_role="technical_writer",
                message="Please write documentation for this code: {developer_response}",
                description="Send code to technical writer"
            )
            
            workflows.append((task, workflow.to_list()))
        
        # Execute workflows in parallel
        async def execute_workflow(task, workflow):
            return await self.team.execute_workflow_async(task, workflow)
        
        # Run the workflows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tasks = [execute_workflow(task, workflow) for task, workflow in workflows]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        
        # Check the results
        self.assertEqual(len(results), 3)
        
        # Check each result
        for i, result in enumerate(results):
            task = workflows[i][0]
            self.assertEqual(result["task"], task)
            self.assertEqual(len(result["results"]), 3)
            
            # Check the research step
            self.assertEqual(result["results"][0]["role"], "researcher")
            self.assertEqual(result["results"][0]["action"], "process")
            
            # Check the coding step
            self.assertEqual(result["results"][1]["role"], "researcher")
            self.assertEqual(result["results"][1]["action"], "send_message")
            self.assertEqual(result["results"][1]["recipient"], "developer")
            
            # Check the documentation step
            self.assertEqual(result["results"][2]["role"], "developer")
            self.assertEqual(result["results"][2]["action"], "send_message")
            self.assertEqual(result["results"][2]["recipient"], "technical_writer")
    
    def test_error_handling(self):
        """Test error handling in workflows."""
        # Define a task
        task = "Process with error"
        
        # Create workflow with error-prone agent
        workflow = Workflow(
            name="Error Workflow",
            description="Workflow with error handling"
        )
        
        # Add steps
        workflow.add_process_step(
            role="error_handler",
            input=f"Process this: {task}",
            description="Process with error"
        )
        
        # Execute workflow with try/except
        try:
            self.team.execute_workflow(task, workflow.to_list())
            # If we get here, the error wasn't raised (which can happen due to randomness)
            pass
        except Exception as e:
            # Check that the error was raised
            self.assertIn("Error processing input", str(e))
    
    def test_dynamic_workflow(self):
        """Test a workflow that changes based on intermediate results."""
        # Define a task
        task = "Implement a Fibonacci sequence generator"
        
        # Create a dynamic workflow based on the results
        class DynamicWorkflow:
            def __init__(self, team):
                self.team = team
                self.steps = []
                self.results = {}
            
            async def execute(self, task):
                # Step 1: Research
                research_result = await self._execute_step(
                    "researcher",
                    "process",
                    f"Research: {task}"
                )
                
                # Step 2: Coding
                coding_result = await self._execute_step(
                    "developer",
                    "process",
                    f"Implement based on this research: {research_result}"
                )
                
                # Step 3: Decide next steps based on coding result
                if "fibonacci" in coding_result.lower():
                    # If it's a Fibonacci implementation, add testing
                    testing_result = await self._execute_step(
                        "tester",
                        "process",
                        f"Write tests for this code: {coding_result}"
                    )
                    
                    # Add documentation
                    doc_result = await self._execute_step(
                        "technical_writer",
                        "process",
                        f"Write documentation for this code: {coding_result}"
                    )
                    
                    return {
                        "task": task,
                        "steps": self.steps,
                        "results": self.results,
                        "final_result": {
                            "code": coding_result,
                            "tests": testing_result,
                            "documentation": doc_result
                        }
                    }
                else:
                    # For other implementations, add review
                    review_result = await self._execute_step(
                        "code_reviewer",
                        "process",
                        f"Review this code: {coding_result}"
                    )
                    
                    return {
                        "task": task,
                        "steps": self.steps,
                        "results": self.results,
                        "final_result": {
                            "code": coding_result,
                            "review": review_result
                        }
                    }
            
            async def _execute_step(self, role, action, input_text):
                # Get agent for role
                agent = self.team.get_agent_for_role(role)
                
                # Execute step
                if action == "process":
                    result = await agent.process_async(input_text)
                    response = result["response"]
                else:
                    raise ValueError(f"Unknown action: {action}")
                
                # Record step
                step = {
                    "role": role,
                    "action": action,
                    "input": input_text,
                    "output": response
                }
                
                self.steps.append(step)
                self.results[role] = response
                
                return response
        
        # Execute dynamic workflow
        dynamic_workflow = DynamicWorkflow(self.team)
        
        # Run the workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(dynamic_workflow.execute(task))
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["steps"]), 4)  # Research, coding, testing, documentation
        self.assertIn("researcher", result["results"])
        self.assertIn("developer", result["results"])
        self.assertIn("tester", result["results"])
        self.assertIn("technical_writer", result["results"])
        self.assertIn("code", result["final_result"])
        self.assertIn("tests", result["final_result"])
        self.assertIn("documentation", result["final_result"])
    
    def test_feedback_loop(self):
        """Test a workflow with feedback loops."""
        # Define a task
        task = "Implement a Fibonacci sequence generator"
        
        # Create a workflow with feedback loops
        async def execute_feedback_workflow(task, max_iterations=3):
            results = []
            
            # Step 1: Research
            research_agent = self.team.get_agent_for_role("researcher")
            research_result = await research_agent.process_async(f"Research: {task}")
            results.append({
                "step": "research",
                "output": research_result["response"]
            })
            
            # Step 2: Initial coding
            coding_agent = self.team.get_agent_for_role("developer")
            coding_result = await coding_agent.process_async(
                f"Implement based on this research: {research_result['response']}"
            )
            results.append({
                "step": "initial_coding",
                "output": coding_result["response"]
            })
            
            # Step 3: Review and improve in a loop
            current_code = coding_result["response"]
            
            for i in range(max_iterations):
                # Review the code
                review_agent = self.team.get_agent_for_role("code_reviewer")
                review_result = await review_agent.process_async(f"Review this code: {current_code}")
                results.append({
                    "step": f"review_{i+1}",
                    "output": review_result["response"]
                })
                
                # Improve the code based on review
                improved_result = await coding_agent.process_async(
                    f"Improve this code based on the review: {current_code}\n\nReview: {review_result['response']}"
                )
                results.append({
                    "step": f"improve_{i+1}",
                    "output": improved_result["response"]
                })
                
                # Update current code
                current_code = improved_result["response"]
                
                # Check if we've reached a satisfactory state
                if "suggestion" not in review_result["response"].lower():
                    break
            
            # Final step: Documentation
            writing_agent = self.team.get_agent_for_role("technical_writer")
            doc_result = await writing_agent.process_async(f"Write documentation for this code: {current_code}")
            results.append({
                "step": "documentation",
                "output": doc_result["response"]
            })
            
            return {
                "task": task,
                "results": results,
                "final_code": current_code,
                "iterations": i + 1,
                "documentation": doc_result["response"]
            }
        
        # Execute feedback workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(execute_feedback_workflow(task))
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertGreaterEqual(len(result["results"]), 5)  # At least research, coding, 1 review, 1 improve, doc
        self.assertIn("final_code", result)
        self.assertIn("iterations", result)
        self.assertIn("documentation", result)
        
        # Check that we have review and improve steps
        review_steps = [r for r in result["results"] if r["step"].startswith("review_")]
        improve_steps = [r for r in result["results"] if r["step"].startswith("improve_")]
        
        self.assertGreaterEqual(len(review_steps), 1)
        self.assertGreaterEqual(len(improve_steps), 1)
        self.assertEqual(len(review_steps), len(improve_steps))


if __name__ == '__main__':
    unittest.main()
