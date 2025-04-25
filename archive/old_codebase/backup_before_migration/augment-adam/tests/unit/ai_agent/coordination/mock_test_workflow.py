"""Unit tests for the Workflow and WorkflowStep classes using mocks."""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the classes directly from the files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../augment_adam/ai_agent/coordination')))

# Mock the imports
sys.modules['augment_adam.ai_agent.base_agent'] = MagicMock()
sys.modules['augment_adam.ai_agent.memory_integration'] = MagicMock()
sys.modules['augment_adam.ai_agent.memory_integration.memory_manager'] = MagicMock()
sys.modules['augment_adam.ai_agent.memory_integration.context_memory'] = MagicMock()
sys.modules['augment_adam.context_engine'] = MagicMock()
sys.modules['augment_adam.memory'] = MagicMock()
sys.modules['augment_adam.models'] = MagicMock()

# Now import the workflow module
from workflow import Workflow, WorkflowStep


class TestWorkflowStep(unittest.TestCase):
    """Tests for the WorkflowStep class."""

    def test_initialization(self):
        """Test step initialization."""
        # Create a process step
        step = WorkflowStep(
            role="role1",
            action="process",
            input="Input",
            description="Process step"
        )
        
        # Check the step
        self.assertEqual(step.role, "role1")
        self.assertEqual(step.action, "process")
        self.assertEqual(step.input, "Input")
        self.assertIsNone(step.recipient)
        self.assertEqual(step.description, "Process step")
        
        # Create a send_message step
        step = WorkflowStep(
            role="role1",
            action="send_message",
            input="Message",
            recipient="role2",
            description="Send message step"
        )
        
        # Check the step
        self.assertEqual(step.role, "role1")
        self.assertEqual(step.action, "send_message")
        self.assertEqual(step.input, "Message")
        self.assertEqual(step.recipient, "role2")
        self.assertEqual(step.description, "Send message step")
        
        # Try to create a step with an unknown action
        with self.assertRaises(ValueError):
            WorkflowStep(
                role="role1",
                action="unknown",
                input="Input"
            )
        
        # Try to create a send_message step without a recipient
        with self.assertRaises(ValueError):
            WorkflowStep(
                role="role1",
                action="send_message",
                input="Message"
            )
    
    def test_to_dict(self):
        """Test converting a step to a dictionary."""
        # Create a process step
        step = WorkflowStep(
            role="role1",
            action="process",
            input="Input",
            description="Process step"
        )
        
        # Convert to dictionary
        step_dict = step.to_dict()
        
        # Check the dictionary
        self.assertEqual(step_dict["role"], "role1")
        self.assertEqual(step_dict["action"], "process")
        self.assertEqual(step_dict["input"], "Input")
        self.assertEqual(step_dict["description"], "Process step")
        self.assertNotIn("recipient", step_dict)


class TestWorkflow(unittest.TestCase):
    """Tests for the Workflow class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a workflow
        self.workflow = Workflow(
            name="Test Workflow",
            description="A test workflow"
        )
    
    def test_initialization(self):
        """Test workflow initialization."""
        self.assertEqual(self.workflow.name, "Test Workflow")
        self.assertEqual(self.workflow.description, "A test workflow")
        self.assertEqual(len(self.workflow.steps), 0)
    
    def test_add_step(self):
        """Test adding a step to the workflow."""
        # Create a step
        step = WorkflowStep(
            role="role1",
            action="process",
            input="Input",
            description="Process step"
        )
        
        # Add the step
        self.workflow.add_step(step)
        
        # Check that the step was added
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertEqual(self.workflow.steps[0], step)
    
    def test_add_process_step(self):
        """Test adding a process step to the workflow."""
        # Add a process step
        self.workflow.add_process_step(
            role="role1",
            input="Input",
            description="Process step"
        )
        
        # Check that the step was added
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertEqual(self.workflow.steps[0].role, "role1")
        self.assertEqual(self.workflow.steps[0].action, "process")
        self.assertEqual(self.workflow.steps[0].input, "Input")
        self.assertEqual(self.workflow.steps[0].description, "Process step")


if __name__ == '__main__':
    unittest.main()
