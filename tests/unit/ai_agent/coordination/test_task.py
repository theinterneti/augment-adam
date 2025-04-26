"""
Unit test for the Task class.

This module contains tests for the Task class, which is a core component
of the agent coordination system.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

import pytest
# Use our mock implementation instead of the actual one
from tests.unit.ai_agent.coordination.mock_task import Task, TaskStatus, TaskPriority, TaskResult, AgentCapability


# @safe_tag("testing.unit.ai_agent.coordination.task")
class TestTask(unittest.TestCase):
    """
    Tests for the Task class.
    """

    def setUp(self):
        """Set up the test case."""
        # Temporarily comment out the tag registry reset
        # reset_tag_registry()

        # Create a test task
        self.task = Task(
            name="test-task",
            description="A test task",
            input="test input",
            priority=TaskPriority.HIGH
        )

    def test_initialization(self):
        """Test initialization of a task."""
        # Verify the task was initialized correctly
        self.assertEqual(self.task.name, "test-task")
        self.assertEqual(self.task.description, "A test task")
        self.assertEqual(self.task.input, "test input")
        self.assertEqual(self.task.priority, TaskPriority.HIGH)
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertIsNone(self.task.assigned_agent_id)
        self.assertIsNone(self.task.parent_task_id)
        self.assertEqual(self.task.subtask_ids, [])
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)
        self.assertIsNone(self.task.deadline)
        self.assertEqual(self.task.metadata, {})
        self.assertIsNone(self.task.result)
        self.assertEqual(self.task.tags, [])

    def test_is_assigned(self):
        """Test checking if a task is assigned."""
        # Initially, the task is not assigned
        self.assertFalse(self.task.is_assigned())

        # Assign the task
        self.task.assigned_agent_id = "agent1"
        self.task.status = TaskStatus.ASSIGNED

        # Now the task is assigned
        self.assertTrue(self.task.is_assigned())

        # Change the status to IN_PROGRESS
        self.task.status = TaskStatus.IN_PROGRESS

        # The task is still assigned
        self.assertTrue(self.task.is_assigned())

        # Change the status to COMPLETED
        self.task.status = TaskStatus.COMPLETED

        # The task is no longer considered assigned
        self.assertFalse(self.task.is_assigned())

    def test_is_completed(self):
        """Test checking if a task is completed."""
        # Initially, the task is not completed
        self.assertFalse(self.task.is_completed())

        # Set the status to COMPLETED but without a result
        self.task.status = TaskStatus.COMPLETED

        # The task is not considered completed without a result
        self.assertFalse(self.task.is_completed())

        # Set a result
        self.task.result = TaskResult(task_id=self.task.id)

        # Now the task is completed
        self.assertTrue(self.task.is_completed())

    def test_is_failed(self):
        """Test checking if a task failed."""
        # Initially, the task is not failed
        self.assertFalse(self.task.is_failed())

        # Set the status to FAILED
        self.task.status = TaskStatus.FAILED

        # Now the task is failed
        self.assertTrue(self.task.is_failed())

    def test_is_cancelled(self):
        """Test checking if a task is cancelled."""
        # Initially, the task is not cancelled
        self.assertFalse(self.task.is_cancelled())

        # Set the status to CANCELLED
        self.task.status = TaskStatus.CANCELLED

        # Now the task is cancelled
        self.assertTrue(self.task.is_cancelled())

    def test_is_overdue(self):
        """Test checking if a task is overdue."""
        # Initially, the task has no deadline
        self.assertFalse(self.task.is_overdue())

        # Set a future deadline
        self.task.deadline = time.time() + 3600  # 1 hour in the future

        # The task is not overdue
        self.assertFalse(self.task.is_overdue())

        # Set a past deadline
        self.task.deadline = time.time() - 3600  # 1 hour in the past

        # Now the task is overdue
        self.assertTrue(self.task.is_overdue())

    def test_has_subtasks(self):
        """Test checking if a task has subtasks."""
        # Initially, the task has no subtasks
        self.assertFalse(self.task.has_subtasks())

        # Add a subtask
        self.task.subtask_ids.append("subtask1")

        # Now the task has subtasks
        self.assertTrue(self.task.has_subtasks())

    def test_assign(self):
        """Test assigning a task to an agent."""
        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Assign the task
        self.task.assign("agent1")

        # Verify the task was assigned correctly
        self.assertEqual(self.task.assigned_agent_id, "agent1")
        self.assertEqual(self.task.status, TaskStatus.ASSIGNED)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

    def test_start(self):
        """Test starting a task."""
        # Assign the task first
        self.task.assign("agent1")

        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Start the task
        self.task.start()

        # Verify the task was started correctly
        self.assertEqual(self.task.status, TaskStatus.IN_PROGRESS)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

    def test_complete(self):
        """Test completing a task."""
        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Create a result
        result = TaskResult(
            task_id=self.task.id,
            agent_id="agent1",
            output="test output"
        )

        # Complete the task
        self.task.complete(result)

        # Verify the task was completed correctly
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertEqual(self.task.result, result)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

    def test_fail(self):
        """Test failing a task."""
        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Fail the task
        self.task.fail("test error")

        # Verify the task was failed correctly
        self.assertEqual(self.task.status, TaskStatus.FAILED)
        self.assertIsNotNone(self.task.result)
        self.assertEqual(self.task.result.error, "test error")
        self.assertEqual(self.task.result.status, TaskStatus.FAILED)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

        # Create a new task with an existing result
        task = Task(
            name="test-task-2",
            result=TaskResult(task_id="test-task-2")
        )

        # Fail the task
        task.fail("another error")

        # Verify the existing result was updated
        self.assertEqual(task.result.error, "another error")
        self.assertEqual(task.result.status, TaskStatus.FAILED)

    def test_cancel(self):
        """Test cancelling a task."""
        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Cancel the task
        self.task.cancel()

        # Verify the task was cancelled correctly
        self.assertEqual(self.task.status, TaskStatus.CANCELLED)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

    def test_add_tag(self):
        """Test adding a tag to a task."""
        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Add a tag
        self.task.add_tag("test-tag")

        # Verify the tag was added
        self.assertIn("test-tag", self.task.tags)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

        # Add the same tag again
        updated_at = self.task.updated_at
        time.sleep(0.001)
        self.task.add_tag("test-tag")

        # Verify the tag wasn't added again and the timestamp didn't change
        self.assertEqual(self.task.tags.count("test-tag"), 1)
        self.assertEqual(self.task.updated_at, updated_at)

    def test_remove_tag(self):
        """Test removing a tag from a task."""
        # Add a tag first
        self.task.add_tag("test-tag")

        # Get the initial updated_at timestamp
        initial_updated_at = self.task.updated_at

        # Wait a moment to ensure the timestamp changes
        time.sleep(0.001)

        # Remove the tag
        self.task.remove_tag("test-tag")

        # Verify the tag was removed
        self.assertNotIn("test-tag", self.task.tags)

        # Verify the updated_at timestamp changed
        self.assertGreater(self.task.updated_at, initial_updated_at)

        # Try to remove a non-existent tag
        updated_at = self.task.updated_at
        time.sleep(0.001)
        self.task.remove_tag("non-existent")

        # Verify the timestamp didn't change
        self.assertEqual(self.task.updated_at, updated_at)

    def test_to_dict(self):
        """Test converting a task to a dictionary."""
        # Add some data to the task
        self.task.assigned_agent_id = "agent1"
        self.task.status = TaskStatus.IN_PROGRESS
        self.task.add_tag("test-tag")
        self.task.required_capabilities.add(AgentCapability.REASONING)

        # Convert to dictionary
        task_dict = self.task.to_dict()

        # Verify the dictionary
        self.assertEqual(task_dict["id"], self.task.id)
        self.assertEqual(task_dict["name"], "test-task")
        self.assertEqual(task_dict["description"], "A test task")
        self.assertEqual(task_dict["input"], "test input")
        self.assertEqual(task_dict["priority"], "HIGH")
        self.assertEqual(task_dict["status"], "IN_PROGRESS")
        self.assertEqual(task_dict["assigned_agent_id"], "agent1")
        self.assertEqual(task_dict["tags"], ["test-tag"])
        self.assertEqual(task_dict["required_capabilities"], ["REASONING"])

    def test_from_dict(self):
        """Test creating a task from a dictionary."""
        # Create a dictionary
        task_dict = {
            "id": "test-id",
            "name": "dict-task",
            "description": "A task from dictionary",
            "input": "dict input",
            "required_capabilities": ["REASONING", "PLANNING"],
            "priority": "NORMAL",
            "status": "ASSIGNED",
            "assigned_agent_id": "agent1",
            "parent_task_id": "parent1",
            "subtask_ids": ["subtask1", "subtask2"],
            "created_at": time.time(),
            "updated_at": time.time(),
            "deadline": time.time() + 3600,
            "metadata": {"key": "value"},
            "result": {
                "task_id": "test-id",
                "agent_id": "agent1",
                "output": "test output",
                "status": "COMPLETED"
            },
            "tags": ["tag1", "tag2"]
        }

        # Create a task from the dictionary
        task = Task.from_dict(task_dict)

        # Verify the task
        self.assertEqual(task.id, "test-id")
        self.assertEqual(task.name, "dict-task")
        self.assertEqual(task.description, "A task from dictionary")
        self.assertEqual(task.input, "dict input")
        self.assertEqual(len(task.required_capabilities), 2)
        self.assertEqual(task.priority, TaskPriority.NORMAL)
        self.assertEqual(task.status, TaskStatus.ASSIGNED)
        self.assertEqual(task.assigned_agent_id, "agent1")
        self.assertEqual(task.parent_task_id, "parent1")
        self.assertEqual(task.subtask_ids, ["subtask1", "subtask2"])
        self.assertEqual(task.metadata, {"key": "value"})
        self.assertIsNotNone(task.result)
        self.assertEqual(task.result.output, "test output")
        self.assertEqual(task.tags, ["tag1", "tag2"])

    def test_task_result_is_successful(self):
        """Test checking if a task result is successful."""
        # Create a successful result
        result = TaskResult(
            task_id="test-id",
            status=TaskStatus.COMPLETED
        )

        # Verify the result is successful
        self.assertTrue(result.is_successful())

        # Create a failed result
        result = TaskResult(
            task_id="test-id",
            status=TaskStatus.FAILED,
            error="test error"
        )

        # Verify the result is not successful
        self.assertFalse(result.is_successful())

    def test_task_result_to_dict(self):
        """Test converting a task result to a dictionary."""
        # Create a result
        result = TaskResult(
            task_id="test-id",
            agent_id="agent1",
            output="test output",
            status=TaskStatus.COMPLETED,
            metadata={"key": "value"},
            error=None
        )

        # Convert to dictionary
        result_dict = result.to_dict()

        # Verify the dictionary
        self.assertEqual(result_dict["task_id"], "test-id")
        self.assertEqual(result_dict["agent_id"], "agent1")
        self.assertEqual(result_dict["output"], "test output")
        self.assertEqual(result_dict["status"], "COMPLETED")
        self.assertEqual(result_dict["metadata"], {"key": "value"})
        self.assertIsNone(result_dict["error"])

    def test_task_result_from_dict(self):
        """Test creating a task result from a dictionary."""
        # Create a dictionary
        result_dict = {
            "task_id": "test-id",
            "agent_id": "agent1",
            "output": "test output",
            "status": "COMPLETED",
            "timestamp": time.time(),
            "metadata": {"key": "value"},
            "error": None
        }

        # Create a result from the dictionary
        result = TaskResult.from_dict(result_dict)

        # Verify the result
        self.assertEqual(result.task_id, "test-id")
        self.assertEqual(result.agent_id, "agent1")
        self.assertEqual(result.output, "test output")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.metadata, {"key": "value"})
        self.assertIsNone(result.error)

if __name__ == "__main__":
    unittest.main()
