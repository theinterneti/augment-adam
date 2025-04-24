"""Stress tests for the agent coordination framework."""

import unittest
import time
import asyncio
import threading
import random
import queue
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from unittest.mock import MagicMock

from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StressMockAgent:
    """Mock agent for stress testing."""
    
    def __init__(self, name, delay_range=(0.001, 0.01), error_rate=0.01):
        """Initialize the stress mock agent.
        
        Args:
            name: Name of the agent
            delay_range: Range of random delays (min, max)
            error_rate: Probability of generating an error (0-1)
        """
        self.name = name
        self.delay_range = delay_range
        self.error_rate = error_rate
        self.call_count = 0
        self.error_count = 0
        self.lock = threading.RLock()
    
    def process(self, input_text, context=None):
        """Process input and generate a response."""
        with self.lock:
            self.call_count += 1
            call_id = self.call_count
        
        # Random delay
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
        # Random error
        if random.random() < self.error_rate:
            with self.lock:
                self.error_count += 1
            raise Exception(f"Simulated error in {self.name} (call {call_id})")
        
        return {
            "response": f"Response from {self.name} (call {call_id}): {input_text[:30]}...",
            "delay": delay,
            "call_id": call_id
        }
    
    async def process_async(self, input_text, context=None):
        """Process input asynchronously."""
        with self.lock:
            self.call_count += 1
            call_id = self.call_count
        
        # Random delay
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)
        
        # Random error
        if random.random() < self.error_rate:
            with self.lock:
                self.error_count += 1
            raise Exception(f"Simulated error in {self.name} (call {call_id})")
        
        return {
            "response": f"Async response from {self.name} (call {call_id}): {input_text[:30]}...",
            "delay": delay,
            "call_id": call_id,
            "async": True
        }
    
    def get_info(self):
        """Get information about the agent."""
        with self.lock:
            return {
                "name": self.name,
                "delay_range": self.delay_range,
                "error_rate": self.error_rate,
                "call_count": self.call_count,
                "error_count": self.error_count
            }


class TestCoordinationStress(unittest.TestCase):
    """Stress tests for the agent coordination framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create agents
        self.num_agents = 20
        self.agents = {}
        
        for i in range(self.num_agents):
            delay_range = (0.001, 0.01)  # 1-10ms
            error_rate = 0.01  # 1% error rate
            self.agents[f"agent{i}"] = StressMockAgent(f"Agent {i}", delay_range, error_rate)
        
        # Create coordinator
        self.coordinator = AgentCoordinator("Stress Coordinator")
        
        # Register agents
        for agent_id, agent in self.agents.items():
            self.coordinator.register_agent(agent_id, agent)
        
        # Create team
        self.team = AgentTeam(
            name="Stress Team",
            description="A team for stress testing",
            coordinator=self.coordinator
        )
        
        # Add roles (10 roles)
        for i in range(10):
            self.team.add_role(
                role_name=f"role{i}",
                agent_id=f"agent{i}",
                description=f"Role {i}"
            )
    
    def test_concurrent_messages(self):
        """Test sending and processing messages concurrently."""
        # Define test parameters
        num_threads = 10
        num_messages_per_thread = 100
        total_messages = num_threads * num_messages_per_thread
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks
            futures = []
            for i in range(num_threads):
                future = executor.submit(self._send_messages, i, num_messages_per_thread)
                futures.append(future)
            
            # Wait for all tasks to complete
            results = [future.result() for future in futures]
        
        # Check results
        total_sent = sum(result["sent"] for result in results)
        total_processed = sum(result["processed"] for result in results)
        total_errors = sum(result["errors"] for result in results)
        
        # Print results
        print(f"\nConcurrent Messages ({num_threads} threads, {num_messages_per_thread} messages each):")
        print(f"Total messages sent: {total_sent}")
        print(f"Total messages processed: {total_processed}")
        print(f"Total errors: {total_errors}")
        print(f"Success rate: {total_processed / total_sent * 100:.2f}%")
        
        # Check agent call counts
        total_calls = sum(agent.call_count for agent in self.agents.values())
        total_errors = sum(agent.error_count for agent in self.agents.values())
        
        print(f"Total agent calls: {total_calls}")
        print(f"Total agent errors: {total_errors}")
        
        # Assert results
        self.assertEqual(total_sent, total_messages)
        self.assertGreaterEqual(total_processed, total_messages * 0.95)  # Allow for some errors
    
    def _send_messages(self, thread_id, num_messages):
        """Send messages in a separate thread."""
        sent = 0
        processed = 0
        errors = 0
        
        for i in range(num_messages):
            try:
                # Select random agents
                from_idx = random.randint(0, self.num_agents - 1)
                to_idx = random.randint(0, self.num_agents - 1)
                while to_idx == from_idx:
                    to_idx = random.randint(0, self.num_agents - 1)
                
                from_agent_id = f"agent{from_idx}"
                to_agent_id = f"agent{to_idx}"
                
                # Send message
                message = self.coordinator.send_message(
                    from_agent_id=from_agent_id,
                    to_agent_id=to_agent_id,
                    message=f"Thread {thread_id}, message {i}"
                )
                
                sent += 1
                
                # Process message
                try:
                    self.coordinator.process_message(message)
                    processed += 1
                except Exception as e:
                    errors += 1
                    logger.debug(f"Error processing message: {e}")
            except Exception as e:
                logger.debug(f"Error sending message: {e}")
        
        return {
            "thread_id": thread_id,
            "sent": sent,
            "processed": processed,
            "errors": errors
        }
    
    def test_concurrent_workflows(self):
        """Test executing workflows concurrently."""
        # Define test parameters
        num_threads = 5
        num_workflows_per_thread = 10
        steps_per_workflow = 5
        total_workflows = num_threads * num_workflows_per_thread
        
        # Create workflows
        workflows = []
        for i in range(total_workflows):
            workflow = Workflow(
                name=f"Workflow {i}",
                description=f"Stress test workflow {i}"
            )
            
            # Add steps
            for j in range(steps_per_workflow):
                role_index = random.randint(0, 9)  # 10 roles
                workflow.add_process_step(
                    role=f"role{role_index}",
                    input=f"Process step {j} of workflow {i}"
                )
            
            workflows.append((f"Task {i}", workflow.to_list()))
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks
            futures = []
            for i in range(num_threads):
                start_idx = i * num_workflows_per_thread
                end_idx = start_idx + num_workflows_per_thread
                thread_workflows = workflows[start_idx:end_idx]
                
                future = executor.submit(self._execute_workflows, i, thread_workflows)
                futures.append(future)
            
            # Wait for all tasks to complete
            results = [future.result() for future in futures]
        
        # Check results
        total_executed = sum(result["executed"] for result in results)
        total_errors = sum(result["errors"] for result in results)
        
        # Print results
        print(f"\nConcurrent Workflows ({num_threads} threads, {num_workflows_per_thread} workflows each, {steps_per_workflow} steps per workflow):")
        print(f"Total workflows executed: {total_executed}")
        print(f"Total errors: {total_errors}")
        print(f"Success rate: {total_executed / total_workflows * 100:.2f}%")
        
        # Check agent call counts
        total_calls = sum(agent.call_count for agent in self.agents.values())
        total_errors = sum(agent.error_count for agent in self.agents.values())
        
        print(f"Total agent calls: {total_calls}")
        print(f"Total agent errors: {total_errors}")
        
        # Assert results
        self.assertGreaterEqual(total_executed, total_workflows * 0.9)  # Allow for some errors
    
    def _execute_workflows(self, thread_id, workflows):
        """Execute workflows in a separate thread."""
        executed = 0
        errors = 0
        
        for task, workflow in workflows:
            try:
                self.team.execute_workflow(task, workflow)
                executed += 1
            except Exception as e:
                errors += 1
                logger.debug(f"Error executing workflow: {e}")
        
        return {
            "thread_id": thread_id,
            "executed": executed,
            "errors": errors
        }
    
    async def _test_async_stress(self, num_tasks, num_steps):
        """Test asynchronous stress."""
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            workflow = Workflow(
                name=f"Async Workflow {i}",
                description=f"Async stress test workflow {i}"
            )
            
            # Add steps
            for j in range(num_steps):
                role_index = random.randint(0, 9)  # 10 roles
                workflow.add_process_step(
                    role=f"role{role_index}",
                    input=f"Process step {j} of async workflow {i}"
                )
            
            tasks.append(self.team.execute_workflow_async(f"Async Task {i}", workflow.to_list()))
        
        # Execute tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful executions
        successful = sum(1 for result in results if not isinstance(result, Exception))
        errors = sum(1 for result in results if isinstance(result, Exception))
        
        return {
            "successful": successful,
            "errors": errors,
            "total": len(results)
        }
    
    def test_async_stress(self):
        """Test asynchronous stress."""
        # Define test parameters
        num_tasks = 50
        num_steps = 5
        
        # Execute async tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(self._test_async_stress(num_tasks, num_steps))
        
        # Print results
        print(f"\nAsync Stress ({num_tasks} tasks, {num_steps} steps each):")
        print(f"Successful executions: {results['successful']}")
        print(f"Errors: {results['errors']}")
        print(f"Success rate: {results['successful'] / results['total'] * 100:.2f}%")
        
        # Check agent call counts
        total_calls = sum(agent.call_count for agent in self.agents.values())
        total_errors = sum(agent.error_count for agent in self.agents.values())
        
        print(f"Total agent calls: {total_calls}")
        print(f"Total agent errors: {total_errors}")
        
        # Assert results
        self.assertGreaterEqual(results['successful'], num_tasks * 0.9)  # Allow for some errors
    
    def test_error_recovery(self):
        """Test recovery from errors."""
        # Create error-prone agents
        error_agents = {}
        for i in range(5):
            error_agents[f"error_agent{i}"] = StressMockAgent(f"Error Agent {i}", (0.001, 0.01), 0.5)  # 50% error rate
        
        # Register error agents
        for agent_id, agent in error_agents.items():
            self.coordinator.register_agent(agent_id, agent)
        
        # Create workflow with error handling
        workflow = Workflow(
            name="Error Recovery Workflow",
            description="Workflow with error handling"
        )
        
        # Add steps with normal and error-prone agents
        for i in range(10):
            if i % 2 == 0:
                # Normal agent
                role_index = random.randint(0, 9)
                agent_id = f"role{role_index}"
            else:
                # Error-prone agent
                error_index = random.randint(0, 4)
                agent_id = f"error_agent{error_index}"
            
            workflow.add_process_step(
                role=agent_id,
                input=f"Process step {i} of error recovery workflow"
            )
        
        # Execute workflow with error handling
        success_count = 0
        error_count = 0
        retry_count = 0
        max_retries = 3
        
        for i in range(10):  # Try 10 workflows
            retries = 0
            while retries <= max_retries:
                try:
                    self.coordinator.coordinate_task(
                        task=f"Error recovery task {i}",
                        primary_agent_id=f"agent{i % self.num_agents}",
                        helper_agent_ids=[f"agent{(i + j + 1) % self.num_agents}" for j in range(3)],
                        max_rounds=3
                    )
                    success_count += 1
                    break
                except Exception as e:
                    retries += 1
                    retry_count += 1
                    if retries > max_retries:
                        error_count += 1
                        logger.debug(f"Failed after {max_retries} retries: {e}")
        
        # Print results
        print(f"\nError Recovery:")
        print(f"Successful executions: {success_count}")
        print(f"Failed executions: {error_count}")
        print(f"Total retries: {retry_count}")
        print(f"Success rate: {success_count / 10 * 100:.2f}%")
        
        # Check agent call counts
        normal_calls = sum(agent.call_count for agent in self.agents.values())
        normal_errors = sum(agent.error_count for agent in self.agents.values())
        
        error_calls = sum(agent.call_count for agent in error_agents.values())
        error_agent_errors = sum(agent.error_count for agent in error_agents.values())
        
        print(f"Normal agent calls: {normal_calls}")
        print(f"Normal agent errors: {normal_errors}")
        print(f"Error-prone agent calls: {error_calls}")
        print(f"Error-prone agent errors: {error_agent_errors}")
        
        # Assert results
        self.assertGreaterEqual(success_count, 5)  # At least 50% success rate
    
    def test_long_running_workflow(self):
        """Test a long-running workflow."""
        # Define test parameters
        num_steps = 50  # Long workflow
        
        # Create workflow
        workflow = Workflow(
            name="Long Workflow",
            description="A long-running workflow"
        )
        
        # Add steps
        for i in range(num_steps):
            role_index = random.randint(0, 9)  # 10 roles
            workflow.add_process_step(
                role=f"role{role_index}",
                input=f"Process step {i} of long workflow"
            )
        
        # Execute workflow
        start_time = time.time()
        
        try:
            result = self.team.execute_workflow("Long task", workflow.to_list())
            success = True
        except Exception as e:
            success = False
            logger.debug(f"Error executing long workflow: {e}")
        
        elapsed_time = time.time() - start_time
        
        # Print results
        print(f"\nLong-Running Workflow ({num_steps} steps):")
        print(f"Success: {success}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Average time per step: {elapsed_time / num_steps:.4f} seconds")
        
        # Check agent call counts
        total_calls = sum(agent.call_count for agent in self.agents.values())
        total_errors = sum(agent.error_count for agent in self.agents.values())
        
        print(f"Total agent calls: {total_calls}")
        print(f"Total agent errors: {total_errors}")
        
        # Assert results
        self.assertTrue(success)
        self.assertGreaterEqual(total_calls, num_steps)
    
    def test_message_flood(self):
        """Test flooding the coordinator with messages."""
        # Define test parameters
        num_messages = 1000  # Large number of messages
        
        # Create message queue
        message_queue = queue.Queue()
        
        # Send messages
        for i in range(num_messages):
            from_idx = random.randint(0, self.num_agents - 1)
            to_idx = random.randint(0, self.num_agents - 1)
            while to_idx == from_idx:
                to_idx = random.randint(0, self.num_agents - 1)
            
            from_agent_id = f"agent{from_idx}"
            to_agent_id = f"agent{to_idx}"
            
            message = self.coordinator.send_message(
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                message=f"Flood message {i}"
            )
            
            message_queue.put(message)
        
        # Process messages
        processed = 0
        errors = 0
        
        start_time = time.time()
        
        while not message_queue.empty():
            message = message_queue.get()
            
            try:
                self.coordinator.process_message(message)
                processed += 1
            except Exception as e:
                errors += 1
                logger.debug(f"Error processing message: {e}")
        
        elapsed_time = time.time() - start_time
        
        # Print results
        print(f"\nMessage Flood ({num_messages} messages):")
        print(f"Processed: {processed}")
        print(f"Errors: {errors}")
        print(f"Success rate: {processed / num_messages * 100:.2f}%")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Messages per second: {processed / elapsed_time:.2f}")
        
        # Check agent call counts
        total_calls = sum(agent.call_count for agent in self.agents.values())
        total_errors = sum(agent.error_count for agent in self.agents.values())
        
        print(f"Total agent calls: {total_calls}")
        print(f"Total agent errors: {total_errors}")
        
        # Assert results
        self.assertGreaterEqual(processed, num_messages * 0.95)  # Allow for some errors
    
    def test_resource_contention(self):
        """Test resource contention with shared agents."""
        # Define test parameters
        num_threads = 10
        num_messages_per_thread = 50
        
        # Create a single shared agent
        shared_agent = StressMockAgent("Shared Agent", (0.005, 0.01), 0.01)
        self.coordinator.register_agent("shared_agent", shared_agent)
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks
            futures = []
            for i in range(num_threads):
                future = executor.submit(self._send_to_shared_agent, i, num_messages_per_thread)
                futures.append(future)
            
            # Wait for all tasks to complete
            results = [future.result() for future in futures]
        
        # Check results
        total_sent = sum(result["sent"] for result in results)
        total_processed = sum(result["processed"] for result in results)
        total_errors = sum(result["errors"] for result in results)
        
        # Print results
        print(f"\nResource Contention ({num_threads} threads, {num_messages_per_thread} messages each):")
        print(f"Total messages sent: {total_sent}")
        print(f"Total messages processed: {total_processed}")
        print(f"Total errors: {total_errors}")
        print(f"Success rate: {total_processed / total_sent * 100:.2f}%")
        
        # Check shared agent call count
        print(f"Shared agent calls: {shared_agent.call_count}")
        print(f"Shared agent errors: {shared_agent.error_count}")
        
        # Assert results
        self.assertEqual(total_sent, num_threads * num_messages_per_thread)
        self.assertGreaterEqual(total_processed, total_sent * 0.95)  # Allow for some errors
        self.assertEqual(shared_agent.call_count, total_processed)
    
    def _send_to_shared_agent(self, thread_id, num_messages):
        """Send messages to the shared agent."""
        sent = 0
        processed = 0
        errors = 0
        
        for i in range(num_messages):
            try:
                # Select random agent as sender
                from_idx = random.randint(0, self.num_agents - 1)
                from_agent_id = f"agent{from_idx}"
                
                # Send message to shared agent
                message = self.coordinator.send_message(
                    from_agent_id=from_agent_id,
                    to_agent_id="shared_agent",
                    message=f"Thread {thread_id}, message {i}"
                )
                
                sent += 1
                
                # Process message
                try:
                    self.coordinator.process_message(message)
                    processed += 1
                except Exception as e:
                    errors += 1
                    logger.debug(f"Error processing message: {e}")
            except Exception as e:
                logger.debug(f"Error sending message: {e}")
        
        return {
            "thread_id": thread_id,
            "sent": sent,
            "processed": processed,
            "errors": errors
        }


if __name__ == '__main__':
    unittest.main()
