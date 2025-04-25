"""End-to-end tests for the agent coordination framework."""

import unittest
import os
import sys
import time
import asyncio
import logging
from unittest.mock import patch

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Skip tests if required dependencies are not available
def check_dependencies():
    """Check if required dependencies are available."""
    try:
        # Try to import required modules
        import transformers
        import torch
        
        # Check if models are available
        if not os.path.exists(os.path.expanduser("~/.cache/huggingface")):
            return False
        
        return True
    except ImportError:
        return False


@unittest.skipIf(not check_dependencies(), "Required dependencies not available")
class TestE2ECoordination(unittest.TestCase):
    """End-to-end tests for the agent coordination framework."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the class."""
        # Get optimal settings
        settings = get_optimal_model_settings("huggingface", "small_context")
        
        # Create model
        cls.model = create_model(
            model_type="huggingface",
            model_size="small_context",
            **settings
        )
        
        # Create specialized agents
        cls.research_agent = create_agent(
            agent_type="conversational",
            name="Research Agent",
            description="An agent specialized in research and information gathering",
            model=cls.model,
            system_prompt="""You are a Research Agent specialized in gathering and analyzing information.

Your goal is to provide accurate, well-researched information on any topic.
Focus on facts and cite sources when possible.
Be thorough and comprehensive in your research.

When you don't know something, admit it rather than making up information.
Always be objective and avoid personal opinions or biases.
""",
            output_format="text"
        )
        
        cls.coding_agent = create_agent(
            agent_type="conversational",
            name="Coding Agent",
            description="An agent specialized in writing and reviewing code",
            model=cls.model,
            system_prompt="""You are a Coding Agent specialized in writing and reviewing code.

Your goal is to write clean, efficient, and well-documented code.
Focus on best practices, readability, and maintainability.
Consider performance, security, and edge cases.

When writing code, include comments to explain complex logic.
When reviewing code, look for bugs, inefficiencies, and improvements.
""",
            output_format="text"
        )
        
        cls.writing_agent = create_agent(
            agent_type="conversational",
            name="Writing Agent",
            description="An agent specialized in writing and content creation",
            model=cls.model,
            system_prompt="""You are a Writing Agent specialized in creating high-quality content.

Your goal is to write clear, engaging, and well-structured content.
Focus on clarity, coherence, and proper grammar.
Adapt your writing style to the specific needs of the task.

When writing, consider the audience and purpose of the content.
Use appropriate tone, vocabulary, and structure for the context.
""",
            output_format="text"
        )
        
        # Create coordinator
        cls.coordinator = AgentCoordinator("E2E Coordinator")
        
        # Register agents
        cls.coordinator.register_agent("research", cls.research_agent)
        cls.coordinator.register_agent("coding", cls.coding_agent)
        cls.coordinator.register_agent("writing", cls.writing_agent)
        
        # Create team
        cls.team = AgentTeam(
            name="E2E Team",
            description="A team for end-to-end testing",
            coordinator=cls.coordinator
        )
        
        # Add roles
        cls.team.add_role(
            role_name="researcher",
            agent_id="research",
            description="Researches topics"
        )
        
        cls.team.add_role(
            role_name="developer",
            agent_id="coding",
            description="Writes code"
        )
        
        cls.team.add_role(
            role_name="technical_writer",
            agent_id="writing",
            description="Creates documentation"
        )
    
    def test_e2e_sequential_coordination(self):
        """Test end-to-end sequential coordination."""
        # Define a task
        task = "Create a Python function to calculate the factorial of a number"
        
        # Step 1: Research Agent researches the topic
        research_message = self.coordinator.send_message(
            from_agent_id="coordinator",
            to_agent_id="research",
            message=f"Please research: {task}"
        )
        
        research_response = self.coordinator.process_message(research_message)
        
        # Check the research response
        self.assertIn("factorial", research_response["message"].lower())
        
        # Step 2: Coding Agent implements based on research
        coding_message = self.coordinator.send_message(
            from_agent_id="research",
            to_agent_id="coding",
            message=f"Based on this research, please implement: {research_response['message']}"
        )
        
        coding_response = self.coordinator.process_message(coding_message)
        
        # Check the coding response
        self.assertIn("def factorial", coding_response["message"].lower())
        
        # Step 3: Writing Agent creates documentation
        writing_message = self.coordinator.send_message(
            from_agent_id="coding",
            to_agent_id="writing",
            message=f"Please write documentation for: {coding_response['message']}"
        )
        
        writing_response = self.coordinator.process_message(writing_message)
        
        # Check the writing response
        self.assertIn("factorial", writing_response["message"].lower())
        self.assertIn("function", writing_response["message"].lower())
        
        # Print results
        print("\nE2E Sequential Coordination:")
        print(f"Research: {research_response['message'][:100]}...")
        print(f"Coding: {coding_response['message'][:100]}...")
        print(f"Writing: {writing_response['message'][:100]}...")
    
    def test_e2e_workflow(self):
        """Test end-to-end workflow execution."""
        # Define a task
        task = "Create a Python function to check if a string is a palindrome"
        
        # Create workflow
        workflow = Workflow(
            name="E2E Workflow",
            description="End-to-end workflow for creating a software component"
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
            to_role="technical_writer",
            message="Please write documentation for: {developer_response}",
            description="Send implementation to technical writer"
        )
        
        # Execute workflow
        result = self.team.execute_workflow(task, workflow.to_list())
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["results"]), 3)
        
        # Check the research step
        self.assertEqual(result["results"][0]["role"], "researcher")
        self.assertEqual(result["results"][0]["action"], "process")
        self.assertIn("palindrome", result["results"][0]["output"].lower())
        
        # Check the coding step
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("def", result["results"][1]["output"].lower())
        self.assertIn("palindrome", result["results"][1]["output"].lower())
        
        # Check the writing step
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "send_message")
        self.assertEqual(result["results"][2]["recipient"], "technical_writer")
        self.assertIn("palindrome", result["results"][2]["output"].lower())
        self.assertIn("function", result["results"][2]["output"].lower())
        
        # Print results
        print("\nE2E Workflow:")
        print(f"Research: {result['results'][0]['output'][:100]}...")
        print(f"Coding: {result['results'][1]['output'][:100]}...")
        print(f"Writing: {result['results'][2]['output'][:100]}...")
    
    def test_e2e_coordinate_task(self):
        """Test end-to-end task coordination."""
        # Define a task
        task = "Create a Python function to find the greatest common divisor (GCD) of two numbers"
        
        # Coordinate the task
        result = self.coordinator.coordinate_task(
            task=task,
            primary_agent_id="coding",
            helper_agent_ids=["research", "writing"],
            max_rounds=2
        )
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(result["primary_agent"], "coding")
        self.assertEqual(result["helper_agents"], ["research", "writing"])
        self.assertLessEqual(result["rounds"], 2)
        
        # Check the response
        self.assertIn("def", result["response"].lower())
        self.assertIn("gcd", result["response"].lower())
        
        # Print results
        print("\nE2E Task Coordination:")
        print(f"Response: {result['response'][:100]}...")
    
    async def test_e2e_async_coordination(self):
        """Test end-to-end asynchronous coordination."""
        # Define tasks
        tasks = [
            "Create a Python function to calculate the Fibonacci sequence",
            "Create a Python function to check if a number is prime",
            "Create a Python function to find the greatest common divisor (GCD) of two numbers"
        ]
        
        # Process tasks in parallel
        async def process_task(task_index, task):
            message = {
                "id": f"task_{task_index}",
                "from": "coordinator",
                "to": "coding",
                "message": task,
                "metadata": {"task_index": task_index},
                "timestamp": time.time()
            }
            
            response = await self.coordinator.process_message_async(message)
            return {
                "task_index": task_index,
                "task": task,
                "response": response["message"]
            }
        
        # Create tasks
        task_futures = [process_task(i, task) for i, task in enumerate(tasks)]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*task_futures)
        
        # Check the results
        self.assertEqual(len(results), 3)
        
        # Check each result
        for i, result in enumerate(results):
            self.assertEqual(result["task_index"], i)
            self.assertEqual(result["task"], tasks[i])
            self.assertIn("def", result["response"].lower())
            
            # Check specific keywords
            if i == 0:
                self.assertIn("fibonacci", result["response"].lower())
            elif i == 1:
                self.assertIn("prime", result["response"].lower())
            elif i == 2:
                self.assertIn("gcd", result["response"].lower())
        
        # Print results
        print("\nE2E Async Coordination:")
        for i, result in enumerate(results):
            print(f"Task {i}: {result['response'][:100]}...")
    
    async def test_e2e_async_workflow(self):
        """Test end-to-end asynchronous workflow execution."""
        # Define a task
        task = "Create a Python function to find the least common multiple (LCM) of two numbers"
        
        # Create workflow
        workflow = Workflow(
            name="E2E Async Workflow",
            description="End-to-end asynchronous workflow"
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
            to_role="technical_writer",
            message="Please write documentation for: {developer_response}",
            description="Send implementation to technical writer"
        )
        
        # Execute workflow asynchronously
        result = await self.team.execute_workflow_async(task, workflow.to_list())
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["results"]), 3)
        
        # Check the research step
        self.assertEqual(result["results"][0]["role"], "researcher")
        self.assertEqual(result["results"][0]["action"], "process")
        self.assertIn("lcm", result["results"][0]["output"].lower())
        
        # Check the coding step
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("def", result["results"][1]["output"].lower())
        self.assertIn("lcm", result["results"][1]["output"].lower())
        
        # Check the writing step
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "send_message")
        self.assertEqual(result["results"][2]["recipient"], "technical_writer")
        self.assertIn("lcm", result["results"][2]["output"].lower())
        self.assertIn("function", result["results"][2]["output"].lower())
        
        # Print results
        print("\nE2E Async Workflow:")
        print(f"Research: {result['results'][0]['output'][:100]}...")
        print(f"Coding: {result['results'][1]['output'][:100]}...")
        print(f"Writing: {result['results'][2]['output'][:100]}...")
    
    def test_e2e_complex_workflow(self):
        """Test end-to-end complex workflow."""
        # Define a task
        task = "Create a Python class for a simple calculator with basic operations"
        
        # Create workflow
        workflow = Workflow(
            name="E2E Complex Workflow",
            description="End-to-end complex workflow"
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
        
        workflow.add_process_step(
            role="developer",
            input="Add more features to your implementation: {developer_response}",
            description="Add more features"
        )
        
        workflow.add_message_step(
            from_role="developer",
            to_role="technical_writer",
            message="Please write documentation for: {developer_result}",
            description="Send implementation to technical writer"
        )
        
        workflow.add_process_step(
            role="technical_writer",
            input="Add usage examples to your documentation: {technical_writer_response}",
            description="Add usage examples"
        )
        
        # Execute workflow
        result = self.team.execute_workflow(task, workflow.to_list())
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["results"]), 5)
        
        # Check specific steps
        self.assertEqual(result["results"][0]["role"], "researcher")
        self.assertEqual(result["results"][0]["action"], "process")
        
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "process")
        
        self.assertEqual(result["results"][3]["role"], "developer")
        self.assertEqual(result["results"][3]["action"], "send_message")
        self.assertEqual(result["results"][3]["recipient"], "technical_writer")
        
        self.assertEqual(result["results"][4]["role"], "technical_writer")
        self.assertEqual(result["results"][4]["action"], "process")
        
        # Check content
        self.assertIn("calculator", result["results"][0]["output"].lower())
        self.assertIn("class", result["results"][1]["output"].lower())
        self.assertIn("calculator", result["results"][1]["output"].lower())
        self.assertIn("def", result["results"][2]["output"].lower())
        self.assertIn("calculator", result["results"][3]["output"].lower())
        self.assertIn("example", result["results"][4]["output"].lower())
        
        # Print results
        print("\nE2E Complex Workflow:")
        print(f"Research: {result['results'][0]['output'][:100]}...")
        print(f"Initial Code: {result['results'][1]['output'][:100]}...")
        print(f"Enhanced Code: {result['results'][2]['output'][:100]}...")
        print(f"Documentation: {result['results'][3]['output'][:100]}...")
        print(f"Examples: {result['results'][4]['output'][:100]}...")


if __name__ == '__main__':
    unittest.main()
