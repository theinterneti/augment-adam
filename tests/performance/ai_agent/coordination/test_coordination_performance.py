"""Performance tests for the agent coordination framework."""

import unittest
import time
import asyncio
import psutil
import os
import gc
import statistics
from unittest.mock import MagicMock
import random
import threading
from concurrent.futures import ThreadPoolExecutor

from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep


class FastMockAgent:
    """Fast mock agent for performance testing."""
    
    def __init__(self, name, delay=0):
        """Initialize the fast mock agent."""
        self.name = name
        self.delay = delay
    
    def process(self, input_text, context=None):
        """Process input and generate a response."""
        if self.delay > 0:
            time.sleep(self.delay)
        
        return {
            "response": f"Response from {self.name}: {input_text[:50]}..."
        }
    
    async def process_async(self, input_text, context=None):
        """Process input asynchronously."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        return {
            "response": f"Async response from {self.name}: {input_text[:50]}..."
        }
    
    def get_info(self):
        """Get information about the agent."""
        return {
            "name": self.name,
            "delay": self.delay
        }


class PerformanceMetrics:
    """Class to collect performance metrics."""
    
    def __init__(self):
        """Initialize the performance metrics."""
        self.process = psutil.Process(os.getpid())
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.cpu_percent = []
        self.memory_samples = []
        self.sampling_thread = None
        self.stop_sampling = False
    
    def start(self):
        """Start collecting metrics."""
        # Force garbage collection
        gc.collect()
        
        # Record start time and memory
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        
        # Start sampling thread
        self.stop_sampling = False
        self.sampling_thread = threading.Thread(target=self._sample_metrics)
        self.sampling_thread.daemon = True
        self.sampling_thread.start()
    
    def stop(self):
        """Stop collecting metrics."""
        # Record end time and memory
        self.end_time = time.time()
        self.end_memory = self.process.memory_info().rss
        
        # Stop sampling thread
        self.stop_sampling = True
        if self.sampling_thread:
            self.sampling_thread.join(timeout=1)
    
    def _sample_metrics(self):
        """Sample metrics in a separate thread."""
        while not self.stop_sampling:
            try:
                self.cpu_percent.append(self.process.cpu_percent(interval=0.1))
                self.memory_samples.append(self.process.memory_info().rss)
            except:
                pass
            time.sleep(0.1)
    
    def get_metrics(self):
        """Get the collected metrics."""
        elapsed_time = self.end_time - self.start_time
        memory_diff = self.end_memory - self.start_memory
        
        # Calculate statistics
        avg_cpu = statistics.mean(self.cpu_percent) if self.cpu_percent else 0
        max_cpu = max(self.cpu_percent) if self.cpu_percent else 0
        
        avg_memory = statistics.mean(self.memory_samples) if self.memory_samples else 0
        max_memory = max(self.memory_samples) if self.memory_samples else 0
        
        return {
            "elapsed_time": elapsed_time,
            "memory_diff": memory_diff,
            "avg_cpu_percent": avg_cpu,
            "max_cpu_percent": max_cpu,
            "avg_memory": avg_memory,
            "max_memory": max_memory,
            "start_memory": self.start_memory,
            "end_memory": self.end_memory
        }


class TestCoordinationPerformance(unittest.TestCase):
    """Performance tests for the agent coordination framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create agents with different delays
        self.agents = {}
        for i in range(10):
            delay = random.uniform(0, 0.01)  # Small delay for performance testing
            self.agents[f"agent{i}"] = FastMockAgent(f"Agent {i}", delay)
        
        # Create coordinator
        self.coordinator = AgentCoordinator("Performance Coordinator")
        
        # Register agents
        for agent_id, agent in self.agents.items():
            self.coordinator.register_agent(agent_id, agent)
        
        # Create team
        self.team = AgentTeam(
            name="Performance Team",
            description="A team for performance testing",
            coordinator=self.coordinator
        )
        
        # Add roles
        for i in range(5):
            self.team.add_role(
                role_name=f"role{i}",
                agent_id=f"agent{i}",
                description=f"Role {i}"
            )
    
    def test_coordinator_message_performance(self):
        """Test the performance of sending and processing messages."""
        # Create metrics collector
        metrics = PerformanceMetrics()
        
        # Define test parameters
        num_messages = 100
        
        # Start metrics collection
        metrics.start()
        
        # Send and process messages
        for i in range(num_messages):
            from_agent_id = f"agent{i % 10}"
            to_agent_id = f"agent{(i + 1) % 10}"
            
            message = self.coordinator.send_message(
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                message=f"Test message {i}"
            )
            
            self.coordinator.process_message(message)
        
        # Stop metrics collection
        metrics.stop()
        
        # Get metrics
        results = metrics.get_metrics()
        
        # Print results
        print(f"\nCoordinator Message Performance ({num_messages} messages):")
        print(f"Elapsed time: {results['elapsed_time']:.4f} seconds")
        print(f"Messages per second: {num_messages / results['elapsed_time']:.2f}")
        print(f"Memory difference: {results['memory_diff'] / 1024 / 1024:.2f} MB")
        print(f"Average CPU: {results['avg_cpu_percent']:.2f}%")
        print(f"Maximum CPU: {results['max_cpu_percent']:.2f}%")
        
        # Assert performance criteria
        self.assertLess(results['elapsed_time'] / num_messages, 0.01)  # Less than 10ms per message
    
    def test_team_workflow_performance(self):
        """Test the performance of executing team workflows."""
        # Create metrics collector
        metrics = PerformanceMetrics()
        
        # Define test parameters
        num_workflows = 10
        steps_per_workflow = 5
        
        # Create workflows
        workflows = []
        for i in range(num_workflows):
            workflow = Workflow(
                name=f"Workflow {i}",
                description=f"Performance test workflow {i}"
            )
            
            # Add steps
            for j in range(steps_per_workflow):
                role_index = (i + j) % 5
                workflow.add_process_step(
                    role=f"role{role_index}",
                    input=f"Process step {j} of workflow {i}"
                )
            
            workflows.append((f"Task {i}", workflow.to_list()))
        
        # Start metrics collection
        metrics.start()
        
        # Execute workflows
        for task, workflow in workflows:
            self.team.execute_workflow(task, workflow)
        
        # Stop metrics collection
        metrics.stop()
        
        # Get metrics
        results = metrics.get_metrics()
        
        # Print results
        print(f"\nTeam Workflow Performance ({num_workflows} workflows, {steps_per_workflow} steps each):")
        print(f"Elapsed time: {results['elapsed_time']:.4f} seconds")
        print(f"Workflows per second: {num_workflows / results['elapsed_time']:.2f}")
        print(f"Steps per second: {num_workflows * steps_per_workflow / results['elapsed_time']:.2f}")
        print(f"Memory difference: {results['memory_diff'] / 1024 / 1024:.2f} MB")
        print(f"Average CPU: {results['avg_cpu_percent']:.2f}%")
        print(f"Maximum CPU: {results['max_cpu_percent']:.2f}%")
        
        # Assert performance criteria
        self.assertLess(results['elapsed_time'] / (num_workflows * steps_per_workflow), 0.01)  # Less than 10ms per step
    
    async def _test_async_performance(self, num_tasks, num_steps):
        """Test the performance of asynchronous operations."""
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            workflow = Workflow(
                name=f"Async Workflow {i}",
                description=f"Async performance test workflow {i}"
            )
            
            # Add steps
            for j in range(num_steps):
                role_index = (i + j) % 5
                workflow.add_process_step(
                    role=f"role{role_index}",
                    input=f"Process step {j} of async workflow {i}"
                )
            
            tasks.append(self.team.execute_workflow_async(f"Async Task {i}", workflow.to_list()))
        
        # Execute tasks
        results = await asyncio.gather(*tasks)
        
        return results
    
    def test_async_performance(self):
        """Test the performance of asynchronous operations."""
        # Create metrics collector
        metrics = PerformanceMetrics()
        
        # Define test parameters
        num_tasks = 10
        num_steps = 5
        
        # Start metrics collection
        metrics.start()
        
        # Execute async tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(self._test_async_performance(num_tasks, num_steps))
        
        # Stop metrics collection
        metrics.stop()
        
        # Get metrics
        perf_results = metrics.get_metrics()
        
        # Print results
        print(f"\nAsync Performance ({num_tasks} tasks, {num_steps} steps each):")
        print(f"Elapsed time: {perf_results['elapsed_time']:.4f} seconds")
        print(f"Tasks per second: {num_tasks / perf_results['elapsed_time']:.2f}")
        print(f"Steps per second: {num_tasks * num_steps / perf_results['elapsed_time']:.2f}")
        print(f"Memory difference: {perf_results['memory_diff'] / 1024 / 1024:.2f} MB")
        print(f"Average CPU: {perf_results['avg_cpu_percent']:.2f}%")
        print(f"Maximum CPU: {perf_results['max_cpu_percent']:.2f}%")
        
        # Check results
        self.assertEqual(len(results), num_tasks)
        
        # Assert performance criteria
        # Async should be faster than sync for parallel tasks
        self.assertLess(perf_results['elapsed_time'], num_tasks * 0.05)  # Less than 50ms per task
    
    def test_memory_usage(self):
        """Test memory usage during coordination operations."""
        # Create metrics collector
        metrics = PerformanceMetrics()
        
        # Define test parameters
        num_messages = 1000
        message_size = 1000  # characters
        
        # Generate a large message
        large_message = "X" * message_size
        
        # Start metrics collection
        metrics.start()
        
        # Send messages with large content
        for i in range(num_messages):
            from_agent_id = f"agent{i % 10}"
            to_agent_id = f"agent{(i + 1) % 10}"
            
            self.coordinator.send_message(
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                message=f"{large_message} {i}"
            )
        
        # Stop metrics collection
        metrics.stop()
        
        # Get metrics
        results = metrics.get_metrics()
        
        # Print results
        print(f"\nMemory Usage ({num_messages} messages, {message_size} chars each):")
        print(f"Elapsed time: {results['elapsed_time']:.4f} seconds")
        print(f"Start memory: {results['start_memory'] / 1024 / 1024:.2f} MB")
        print(f"End memory: {results['end_memory'] / 1024 / 1024:.2f} MB")
        print(f"Memory difference: {results['memory_diff'] / 1024 / 1024:.2f} MB")
        print(f"Memory per message: {results['memory_diff'] / num_messages / 1024:.2f} KB")
        
        # Assert memory usage criteria
        # Memory usage should be reasonable
        self.assertLess(results['memory_diff'] / num_messages, 10 * 1024)  # Less than 10KB per message
    
    def test_cpu_usage(self):
        """Test CPU usage during coordination operations."""
        # Create metrics collector
        metrics = PerformanceMetrics()
        
        # Define test parameters
        num_concurrent = 4
        num_messages_per_thread = 100
        
        # Start metrics collection
        metrics.start()
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            # Submit tasks
            futures = []
            for i in range(num_concurrent):
                future = executor.submit(self._send_messages, i, num_messages_per_thread)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in futures:
                future.result()
        
        # Stop metrics collection
        metrics.stop()
        
        # Get metrics
        results = metrics.get_metrics()
        
        # Print results
        print(f"\nCPU Usage ({num_concurrent} threads, {num_messages_per_thread} messages each):")
        print(f"Elapsed time: {results['elapsed_time']:.4f} seconds")
        print(f"Average CPU: {results['avg_cpu_percent']:.2f}%")
        print(f"Maximum CPU: {results['max_cpu_percent']:.2f}%")
        
        # Assert CPU usage criteria
        # CPU usage should be reasonable for the number of threads
        self.assertLess(results['max_cpu_percent'], 100 * num_concurrent)  # Less than 100% per thread
    
    def _send_messages(self, thread_id, num_messages):
        """Send messages in a separate thread."""
        for i in range(num_messages):
            from_agent_id = f"agent{(thread_id * 2) % 10}"
            to_agent_id = f"agent{(thread_id * 2 + 1) % 10}"
            
            message = self.coordinator.send_message(
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                message=f"Thread {thread_id}, message {i}"
            )
            
            self.coordinator.process_message(message)
    
    def test_scaling_performance(self):
        """Test how performance scales with increasing workload."""
        # Define test parameters
        workloads = [10, 50, 100, 200, 500]
        
        # Collect results
        results = []
        
        for workload in workloads:
            # Create metrics collector
            metrics = PerformanceMetrics()
            
            # Start metrics collection
            metrics.start()
            
            # Send and process messages
            for i in range(workload):
                from_agent_id = f"agent{i % 10}"
                to_agent_id = f"agent{(i + 1) % 10}"
                
                message = self.coordinator.send_message(
                    from_agent_id=from_agent_id,
                    to_agent_id=to_agent_id,
                    message=f"Scaling test message {i}"
                )
                
                self.coordinator.process_message(message)
            
            # Stop metrics collection
            metrics.stop()
            
            # Get metrics
            perf_results = metrics.get_metrics()
            
            # Add to results
            results.append({
                "workload": workload,
                "elapsed_time": perf_results['elapsed_time'],
                "messages_per_second": workload / perf_results['elapsed_time'],
                "memory_diff": perf_results['memory_diff'],
                "avg_cpu_percent": perf_results['avg_cpu_percent']
            })
        
        # Print results
        print("\nScaling Performance:")
        print("Workload | Time (s) | Msgs/s | Memory (MB) | CPU (%)")
        print("-" * 60)
        for result in results:
            print(f"{result['workload']:8d} | {result['elapsed_time']:.4f} | {result['messages_per_second']:.2f} | {result['memory_diff'] / 1024 / 1024:.2f} | {result['avg_cpu_percent']:.2f}")
        
        # Check scaling
        # Time should scale roughly linearly with workload
        time_ratios = [results[i+1]['elapsed_time'] / results[i]['elapsed_time'] for i in range(len(results)-1)]
        workload_ratios = [results[i+1]['workload'] / results[i]['workload'] for i in range(len(results)-1)]
        
        # Calculate scaling factor (should be close to 1 for linear scaling)
        scaling_factors = [time_ratios[i] / workload_ratios[i] for i in range(len(time_ratios))]
        avg_scaling_factor = statistics.mean(scaling_factors)
        
        print(f"\nAverage scaling factor: {avg_scaling_factor:.2f}")
        print(f"Scaling factors: {[f'{sf:.2f}' for sf in scaling_factors]}")
        
        # Assert scaling criteria
        # Scaling should be roughly linear or better
        self.assertLess(avg_scaling_factor, 1.2)  # Less than 20% worse than linear


if __name__ == '__main__':
    unittest.main()
