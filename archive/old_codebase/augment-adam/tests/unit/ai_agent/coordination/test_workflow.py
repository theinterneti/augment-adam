"""Unit tests for the Workflow and WorkflowStep classes."""

import unittest
from unittest.mock import MagicMock

from augment_adam.ai_agent.coordination.workflow import Workflow, WorkflowStep


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
        
        # Create a send_message step
        step = WorkflowStep(
            role="role1",
            action="send_message",
            input="Message",
            recipient="role2",
            description="Send message step"
        )
        
        # Convert to dictionary
        step_dict = step.to_dict()
        
        # Check the dictionary
        self.assertEqual(step_dict["role"], "role1")
        self.assertEqual(step_dict["action"], "send_message")
        self.assertEqual(step_dict["input"], "Message")
        self.assertEqual(step_dict["recipient"], "role2")
        self.assertEqual(step_dict["description"], "Send message step")
        
        # Create a step without optional fields
        step = WorkflowStep(
            role="role1",
            action="process"
        )
        
        # Convert to dictionary
        step_dict = step.to_dict()
        
        # Check the dictionary
        self.assertEqual(step_dict["role"], "role1")
        self.assertEqual(step_dict["action"], "process")
        self.assertNotIn("input", step_dict)
        self.assertNotIn("recipient", step_dict)
        self.assertNotIn("description", step_dict)


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
    
    def test_add_message_step(self):
        """Test adding a message step to the workflow."""
        # Add a message step
        self.workflow.add_message_step(
            from_role="role1",
            to_role="role2",
            message="Message",
            description="Send message step"
        )
        
        # Check that the step was added
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertEqual(self.workflow.steps[0].role, "role1")
        self.assertEqual(self.workflow.steps[0].action, "send_message")
        self.assertEqual(self.workflow.steps[0].input, "Message")
        self.assertEqual(self.workflow.steps[0].recipient, "role2")
        self.assertEqual(self.workflow.steps[0].description, "Send message step")
    
    def test_to_list(self):
        """Test converting the workflow to a list of dictionaries."""
        # Add some steps
        self.workflow.add_process_step(
            role="role1",
            input="Input 1",
            description="Process step 1"
        )
        
        self.workflow.add_message_step(
            from_role="role1",
            to_role="role2",
            message="Message",
            description="Send message step"
        )
        
        self.workflow.add_process_step(
            role="role2",
            input="Input 2",
            description="Process step 2"
        )
        
        # Convert to list
        workflow_list = self.workflow.to_list()
        
        # Check the list
        self.assertEqual(len(workflow_list), 3)
        self.assertEqual(workflow_list[0]["role"], "role1")
        self.assertEqual(workflow_list[0]["action"], "process")
        self.assertEqual(workflow_list[0]["input"], "Input 1")
        self.assertEqual(workflow_list[0]["description"], "Process step 1")
        self.assertEqual(workflow_list[1]["role"], "role1")
        self.assertEqual(workflow_list[1]["action"], "send_message")
        self.assertEqual(workflow_list[1]["input"], "Message")
        self.assertEqual(workflow_list[1]["recipient"], "role2")
        self.assertEqual(workflow_list[1]["description"], "Send message step")
        self.assertEqual(workflow_list[2]["role"], "role2")
        self.assertEqual(workflow_list[2]["action"], "process")
        self.assertEqual(workflow_list[2]["input"], "Input 2")
        self.assertEqual(workflow_list[2]["description"], "Process step 2")
    
    def test_from_list(self):
        """Test creating a workflow from a list of dictionaries."""
        # Create a list of step dictionaries
        steps = [
            {
                "role": "role1",
                "action": "process",
                "input": "Input 1",
                "description": "Process step 1"
            },
            {
                "role": "role1",
                "action": "send_message",
                "input": "Message",
                "recipient": "role2",
                "description": "Send message step"
            },
            {
                "role": "role2",
                "action": "process",
                "input": "Input 2",
                "description": "Process step 2"
            }
        ]
        
        # Create a workflow from the list
        workflow = Workflow.from_list(
            name="Test Workflow",
            description="A test workflow",
            steps=steps
        )
        
        # Check the workflow
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.description, "A test workflow")
        self.assertEqual(len(workflow.steps), 3)
        self.assertEqual(workflow.steps[0].role, "role1")
        self.assertEqual(workflow.steps[0].action, "process")
        self.assertEqual(workflow.steps[0].input, "Input 1")
        self.assertEqual(workflow.steps[0].description, "Process step 1")
        self.assertEqual(workflow.steps[1].role, "role1")
        self.assertEqual(workflow.steps[1].action, "send_message")
        self.assertEqual(workflow.steps[1].input, "Message")
        self.assertEqual(workflow.steps[1].recipient, "role2")
        self.assertEqual(workflow.steps[1].description, "Send message step")
        self.assertEqual(workflow.steps[2].role, "role2")
        self.assertEqual(workflow.steps[2].action, "process")
        self.assertEqual(workflow.steps[2].input, "Input 2")
        self.assertEqual(workflow.steps[2].description, "Process step 2")


if __name__ == '__main__':
    unittest.main()
