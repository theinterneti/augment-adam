"""Integration tests for the agent coordination framework."""

import unittest
from unittest.mock import MagicMock
import asyncio

from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep
from augment_adam.models.model_interface import ModelInterface


class MockModel(ModelInterface):
    """Mock model for testing."""
    
    def __init__(self, name="mock_model"):
        """Initialize the mock model."""
        self.name = name
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt."""
        # Simple mock responses based on the prompt
        if "research" in prompt.lower():
            return "Research result: The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones."
        elif "code" in prompt.lower() or "implement" in prompt.lower():
            return "```python\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    else:\n        fib = [0, 1]\n        for i in range(2, n):\n            fib.append(fib[i-1] + fib[i-2])\n        return fib\n```"
        elif "document" in prompt.lower() or "documentation" in prompt.lower():
            return "# Fibonacci Function\n\nThis function generates the Fibonacci sequence up to n numbers.\n\n## Parameters\n- n: The number of Fibonacci numbers to generate\n\n## Returns\n- A list containing the Fibonacci sequence"
        else:
            return f"Response to: {prompt}"
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [0.1] * 10
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.name,
            "provider": "Mock",
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, name, role=None):
        """Initialize the mock agent."""
        self.name = name
        self.role = role
        self.model = MockModel()
    
    def process(self, input_text, context=None):
        """Process input and generate a response."""
        if self.role == "researcher":
            return {"response": f"Research: {self.model.generate('research ' + input_text)}"}
        elif self.role == "coder":
            return {"response": f"Code: {self.model.generate('code ' + input_text)}"}
        elif self.role == "writer":
            return {"response": f"Documentation: {self.model.generate('document ' + input_text)}"}
        else:
            return {"response": f"Response from {self.name}: {self.model.generate(input_text)}"}
    
    async def process_async(self, input_text, context=None):
        """Process input asynchronously."""
        return self.process(input_text, context)
    
    def get_info(self):
        """Get information about the agent."""
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model.get_model_info()
        }


class TestCoordinationIntegration(unittest.TestCase):
    """Integration tests for the agent coordination framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock agents
        self.research_agent = MockAgent("Research Agent", "researcher")
        self.coding_agent = MockAgent("Coding Agent", "coder")
        self.writing_agent = MockAgent("Writing Agent", "writer")
        
        # Create coordinator
        self.coordinator = AgentCoordinator("Test Coordinator")
        
        # Register agents
        self.coordinator.register_agent("research", self.research_agent)
        self.coordinator.register_agent("coding", self.coding_agent)
        self.coordinator.register_agent("writing", self.writing_agent)
        
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
    
    def test_sequential_coordination(self):
        """Test sequential coordination of agents."""
        # Define a task
        task = "Create a function to calculate the Fibonacci sequence"
        
        # Step 1: Research Agent researches the topic
        research_message = self.coordinator.send_message(
            from_agent_id="coordinator",
            to_agent_id="research",
            message=f"Please research: {task}"
        )
        
        research_response = self.coordinator.process_message(research_message)
        
        # Check the research response
        self.assertIn("Fibonacci sequence", research_response["message"])
        self.assertIn("Research", research_response["message"])
        
        # Step 2: Coding Agent implements based on research
        coding_message = self.coordinator.send_message(
            from_agent_id="research",
            to_agent_id="coding",
            message=f"Based on this research, please implement: {research_response['message']}"
        )
        
        coding_response = self.coordinator.process_message(coding_message)
        
        # Check the coding response
        self.assertIn("Code", coding_response["message"])
        self.assertIn("fibonacci", coding_response["message"].lower())
        self.assertIn("def", coding_response["message"].lower())
        
        # Step 3: Writing Agent creates documentation
        writing_message = self.coordinator.send_message(
            from_agent_id="coding",
            to_agent_id="writing",
            message=f"Please write documentation for: {coding_response['message']}"
        )
        
        writing_response = self.coordinator.process_message(writing_message)
        
        # Check the writing response
        self.assertIn("Documentation", writing_response["message"])
        self.assertIn("Fibonacci", writing_response["message"])
        self.assertIn("Parameters", writing_response["message"])
        self.assertIn("Returns", writing_response["message"])
        
        # Check the message history
        self.assertEqual(len(self.coordinator.message_history), 3)
    
    def test_team_workflow(self):
        """Test team workflow execution."""
        # Define a task
        task = "Create a function to calculate the Fibonacci sequence"
        
        # Create workflow
        workflow = Workflow(
            name="Development Workflow",
            description="Workflow for creating a software component"
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
        self.assertIn("Research", result["results"][0]["output"])
        self.assertIn("Fibonacci sequence", result["results"][0]["output"])
        
        # Check the coding step
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("Code", result["results"][1]["output"])
        self.assertIn("fibonacci", result["results"][1]["output"].lower())
        
        # Check the writing step
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "send_message")
        self.assertEqual(result["results"][2]["recipient"], "technical_writer")
        self.assertIn("Documentation", result["results"][2]["output"])
        self.assertIn("Fibonacci", result["results"][2]["output"])
    
    def test_coordinate_task(self):
        """Test coordinating a task between multiple agents."""
        # Define a task
        task = "Create a function to calculate the Fibonacci sequence"
        
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
        self.assertIn("Response", result["response"])
    
    async def test_async_coordination(self):
        """Test asynchronous coordination."""
        # Define tasks
        tasks = [
            "Create a function to calculate the Fibonacci sequence",
            "Implement a binary search algorithm",
            "Write a function to check if a string is a palindrome"
        ]
        
        # Process tasks in parallel
        async def process_task(task_index, task):
            message = {
                "id": f"task_{task_index}",
                "from": "coordinator",
                "to": "coding",
                "message": task,
                "metadata": {"task_index": task_index},
                "timestamp": 0
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
        for i, result in enumerate(results):
            self.assertEqual(result["task_index"], i)
            self.assertEqual(result["task"], tasks[i])
            self.assertIn("Response", result["response"])
            self.assertIn("Code", result["response"])
    
    async def test_async_workflow(self):
        """Test asynchronous workflow execution."""
        # Define a task
        task = "Create a function to calculate the Fibonacci sequence"
        
        # Create workflow
        workflow = Workflow(
            name="Development Workflow",
            description="Workflow for creating a software component"
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
        self.assertIn("Research", result["results"][0]["output"])
        self.assertIn("Fibonacci sequence", result["results"][0]["output"])
        
        # Check the coding step
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["action"], "send_message")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("Code", result["results"][1]["output"])
        self.assertIn("fibonacci", result["results"][1]["output"].lower())
        
        # Check the writing step
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["action"], "send_message")
        self.assertEqual(result["results"][2]["recipient"], "technical_writer")
        self.assertIn("Documentation", result["results"][2]["output"])
        self.assertIn("Fibonacci", result["results"][2]["output"])


if __name__ == '__main__':
    unittest.main()
