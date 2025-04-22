"""Tests for the progress tracking system.

This module contains tests for the progress tracking system.

Version: 0.1.0
Created: 2025-04-26
"""

import time
import unittest
from unittest.mock import MagicMock, patch

import pytest

from dukat.core.progress import (
    ProgressTracker, ProgressState,
    register_progress_tracker, get_progress_tracker,
    remove_progress_tracker, get_all_progress_trackers,
    get_progress_tracker_stats, create_progress_tracker
)
from dukat.core.errors import ValidationError


class TestProgressTracker(unittest.TestCase):
    """Test cases for the ProgressTracker class."""

    def setUp(self):
        """Set up the test case."""
        # Clear all progress trackers before each test
        for tracker in get_all_progress_trackers():
            remove_progress_tracker(tracker.task_id)

    def test_init(self):
        """Test initialization of the progress tracker."""
        tracker = ProgressTracker(task_id="test")
        self.assertEqual(tracker.task_id, "test")
        self.assertEqual(tracker.state, ProgressState.NOT_STARTED)
        self.assertEqual(tracker.current_step, 0)
        self.assertEqual(tracker.current_percentage, 0.0)
        self.assertEqual(tracker.total_percentage, 100.0)
        self.assertEqual(tracker.start_time, 0.0)
        self.assertEqual(tracker.end_time, 0.0)
        self.assertEqual(tracker.message, "")
        self.assertEqual(tracker.details, {})
        self.assertEqual(tracker.children, {})
        self.assertEqual(tracker.callbacks, [])

    def test_init_with_steps(self):
        """Test initialization with steps."""
        tracker = ProgressTracker(task_id="test", total_steps=10)
        self.assertEqual(tracker.task_id, "test")
        self.assertEqual(tracker.total_steps, 10)
        self.assertEqual(tracker.current_step, 0)
        self.assertEqual(tracker.current_percentage, 0.0)

    def test_start(self):
        """Test starting progress tracking."""
        tracker = ProgressTracker(task_id="test")
        tracker.start(message="Starting")
        self.assertEqual(tracker.state, ProgressState.IN_PROGRESS)
        self.assertGreater(tracker.start_time, 0.0)
        self.assertEqual(tracker.message, "Starting")

    def test_complete(self):
        """Test completing progress tracking."""
        tracker = ProgressTracker(task_id="test", total_steps=10)
        tracker.start()
        tracker.complete(message="Completed")
        self.assertEqual(tracker.state, ProgressState.COMPLETED)
        self.assertGreater(tracker.end_time, 0.0)
        self.assertEqual(tracker.message, "Completed")
        self.assertEqual(tracker.current_step, 10)
        self.assertEqual(tracker.current_percentage, 100.0)

    def test_fail(self):
        """Test failing progress tracking."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        tracker.fail(message="Failed")
        self.assertEqual(tracker.state, ProgressState.FAILED)
        self.assertGreater(tracker.end_time, 0.0)
        self.assertEqual(tracker.message, "Failed")

    def test_cancel(self):
        """Test cancelling progress tracking."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        tracker.cancel(message="Cancelled")
        self.assertEqual(tracker.state, ProgressState.CANCELLED)
        self.assertGreater(tracker.end_time, 0.0)
        self.assertEqual(tracker.message, "Cancelled")

    def test_update_step(self):
        """Test updating progress by step."""
        tracker = ProgressTracker(task_id="test", total_steps=10)
        tracker.start()
        tracker.update_step(5, message="Halfway")
        self.assertEqual(tracker.current_step, 5)
        self.assertEqual(tracker.current_percentage, 50.0)
        self.assertEqual(tracker.message, "Halfway")

    def test_update_step_validation(self):
        """Test validation when updating by step."""
        # Test with percentage-based tracker
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        with self.assertRaises(ValidationError):
            tracker.update_step(5)

        # Test with step out of range
        tracker = ProgressTracker(task_id="test", total_steps=10)
        tracker.start()
        with self.assertRaises(ValidationError):
            tracker.update_step(11)

    def test_update_percentage(self):
        """Test updating progress by percentage."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        tracker.update_percentage(50.0, message="Halfway")
        self.assertEqual(tracker.current_percentage, 50.0)
        self.assertEqual(tracker.message, "Halfway")

    def test_update_percentage_with_steps(self):
        """Test updating percentage with steps."""
        tracker = ProgressTracker(task_id="test", total_steps=10)
        tracker.start()
        tracker.update_percentage(50.0)
        self.assertEqual(tracker.current_step, 5)
        self.assertEqual(tracker.current_percentage, 50.0)

    def test_update_percentage_validation(self):
        """Test validation when updating by percentage."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        with self.assertRaises(ValidationError):
            tracker.update_percentage(101.0)

    def test_increment_step(self):
        """Test incrementing progress by step."""
        tracker = ProgressTracker(task_id="test", total_steps=10)
        tracker.start()
        tracker.increment_step(3)
        self.assertEqual(tracker.current_step, 3)
        self.assertEqual(tracker.current_percentage, 30.0)

    def test_increment_step_validation(self):
        """Test validation when incrementing by step."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        with self.assertRaises(ValidationError):
            tracker.increment_step(1)

    def test_increment_percentage(self):
        """Test incrementing progress by percentage."""
        tracker = ProgressTracker(task_id="test")
        tracker.start()
        tracker.increment_percentage(30.0)
        self.assertEqual(tracker.current_percentage, 30.0)

    def test_add_child(self):
        """Test adding a child progress tracker."""
        parent = ProgressTracker(task_id="parent")
        child = parent.add_child(
            child_id="child",
            weight=0.5,
            total_steps=10,
            description="Child task",
        )
        self.assertEqual(child.task_id, "parent.child")
        self.assertEqual(child.total_steps, 10)
        self.assertEqual(child.total_percentage,
                         100.0)  # Children always use 100%
        self.assertEqual(child.weight, 0.5)  # Weight is stored as a property
        self.assertEqual(child.description, "Child task")
        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children["child"], child)

    def test_get_child(self):
        """Test getting a child progress tracker."""
        parent = ProgressTracker(task_id="parent")
        child = parent.add_child(child_id="child")
        self.assertEqual(parent.get_child("child"), child)
        self.assertIsNone(parent.get_child("nonexistent"))

    def test_remove_child(self):
        """Test removing a child progress tracker."""
        parent = ProgressTracker(task_id="parent")
        parent.add_child(child_id="child")
        parent.remove_child("child")
        self.assertNotIn("child", parent.children)

    def test_child_updates_parent(self):
        """Test that child updates propagate to parent."""
        parent = ProgressTracker(task_id="parent")
        child1 = parent.add_child(child_id="child1", weight=0.6)
        child2 = parent.add_child(child_id="child2", weight=0.4)

        parent.start()
        child1.start()
        child2.start()

        # When child1 is at 50%, it contributes 50% of its 60% weight = 30%
        child1.update_percentage(50.0)
        self.assertAlmostEqual(parent.current_percentage, 30.0, delta=0.1)

        # When child2 is at 25%, it contributes 25% of its 40% weight = 10%
        # Total should be 30% + 10% = 40%
        child2.update_percentage(25.0)
        self.assertAlmostEqual(parent.current_percentage, 40.0, delta=0.1)

        # When child1 is complete (100%), it contributes 100% of its 60% weight = 60%
        # Total should be 60% + 10% = 70%
        child1.complete()
        self.assertAlmostEqual(parent.current_percentage, 70.0, delta=0.1)

        # When child2 is complete (100%), it contributes 100% of its 40% weight = 40%
        # Total should be 60% + 40% = 100%
        child2.complete()
        self.assertAlmostEqual(parent.current_percentage, 100.0, delta=0.1)

    def test_callbacks(self):
        """Test progress callbacks."""
        tracker = ProgressTracker(task_id="test")
        callback = MagicMock()
        tracker.add_callback(callback)

        tracker.start()
        callback.assert_called_once_with(tracker)
        callback.reset_mock()

        tracker.update_percentage(50.0)
        callback.assert_called_once_with(tracker)
        callback.reset_mock()

        tracker.remove_callback(callback)
        tracker.update_percentage(75.0)
        callback.assert_not_called()

    def test_get_progress(self):
        """Test getting progress information."""
        tracker = ProgressTracker(
            task_id="test", total_steps=10, description="Test task")
        tracker.start(message="Starting")
        tracker.update_step(5, details={"key": "value"})

        progress = tracker.get_progress()
        self.assertEqual(progress["task_id"], "test")
        self.assertEqual(progress["state"], "in_progress")
        self.assertEqual(progress["description"], "Test task")
        self.assertEqual(progress["current_step"], 5)
        self.assertEqual(progress["total_steps"], 10)
        self.assertEqual(progress["current_percentage"], 50.0)
        self.assertEqual(progress["total_percentage"], 100.0)
        self.assertEqual(progress["message"], "Starting")
        self.assertEqual(progress["details"], {"key": "value"})
        self.assertGreater(progress["start_time"], 0.0)
        self.assertEqual(progress["end_time"], 0.0)
        self.assertGreater(progress["elapsed_time"], 0.0)

    def test_get_elapsed_time(self):
        """Test getting elapsed time."""
        tracker = ProgressTracker(task_id="test")
        self.assertEqual(tracker.get_elapsed_time(), 0.0)

        tracker.start()
        time.sleep(0.1)
        elapsed = tracker.get_elapsed_time()
        self.assertGreater(elapsed, 0.0)

        tracker.complete()
        final_elapsed = tracker.get_elapsed_time()
        self.assertGreaterEqual(final_elapsed, elapsed)

    def test_get_estimated_time_remaining(self):
        """Test getting estimated time remaining."""
        tracker = ProgressTracker(task_id="test")
        self.assertIsNone(tracker.get_estimated_time_remaining())

        tracker.start()
        self.assertIsNone(tracker.get_estimated_time_remaining())

        # Simulate some progress
        time.sleep(0.1)
        tracker.update_percentage(25.0)

        # Check that the estimated time is reasonable
        estimated = tracker.get_estimated_time_remaining()
        self.assertIsNotNone(estimated)
        self.assertGreater(estimated, 0.0)

        # Complete the task
        tracker.complete()
        self.assertIsNone(tracker.get_estimated_time_remaining())


class TestProgressRegistry:
    """Test cases for the progress tracker registry."""

    def setup_method(self):
        """Set up the test case."""
        # Clear all progress trackers before each test
        for tracker in get_all_progress_trackers():
            remove_progress_tracker(tracker.task_id)

    def test_register_progress_tracker(self):
        """Test registering a progress tracker."""
        tracker = ProgressTracker(task_id="test_register")
        register_progress_tracker(tracker)

        # Get the progress tracker
        retrieved = get_progress_tracker("test_register")

        # Check that the retrieved tracker is the same
        assert retrieved is tracker

    def test_get_progress_tracker(self):
        """Test getting a progress tracker."""
        tracker = ProgressTracker(task_id="test_get")
        register_progress_tracker(tracker)

        # Get the progress tracker
        retrieved = get_progress_tracker("test_get")

        # Check that the retrieved tracker is the same
        assert retrieved is tracker

        # Try to get a non-existent progress tracker
        non_existent = get_progress_tracker("non_existent")

        # Check that the result is None
        assert non_existent is None

    def test_remove_progress_tracker(self):
        """Test removing a progress tracker."""
        tracker = ProgressTracker(task_id="test_remove")
        register_progress_tracker(tracker)

        # Remove the progress tracker
        remove_progress_tracker("test_remove")

        # Check that the tracker is no longer in the registry
        assert get_progress_tracker("test_remove") is None

    def test_get_all_progress_trackers(self):
        """Test getting all progress trackers."""
        # Create and register some progress trackers
        tracker1 = ProgressTracker(task_id="test1")
        tracker2 = ProgressTracker(task_id="test2")
        tracker3 = ProgressTracker(task_id="test3")

        register_progress_tracker(tracker1)
        register_progress_tracker(tracker2)
        register_progress_tracker(tracker3)

        # Get all progress trackers
        all_trackers = get_all_progress_trackers()

        # Check that all trackers are in the list
        assert len(all_trackers) == 3
        assert tracker1 in all_trackers
        assert tracker2 in all_trackers
        assert tracker3 in all_trackers

    def test_get_progress_tracker_stats(self):
        """Test getting statistics for all progress trackers."""
        # Create and register some progress trackers
        tracker1 = ProgressTracker(task_id="test_stats1")
        tracker2 = ProgressTracker(task_id="test_stats2")

        register_progress_tracker(tracker1)
        register_progress_tracker(tracker2)

        # Start the trackers
        tracker1.start(message="Tracker 1")
        tracker2.start(message="Tracker 2")

        # Update progress
        tracker1.update_percentage(50.0)

        # Get the stats
        stats = get_progress_tracker_stats()

        # Check the stats
        assert "test_stats1" in stats
        assert "test_stats2" in stats

        assert stats["test_stats1"]["state"] == "in_progress"
        assert stats["test_stats1"]["current_percentage"] == 50.0
        assert stats["test_stats1"]["message"] == "Tracker 1"

        assert stats["test_stats2"]["state"] == "in_progress"
        assert stats["test_stats2"]["current_percentage"] == 0.0
        assert stats["test_stats2"]["message"] == "Tracker 2"

    def test_create_progress_tracker(self):
        """Test creating a progress tracker."""
        # Create a progress tracker
        tracker = create_progress_tracker(
            task_id="test_create",
            total_steps=10,
            description="Test creation",
        )

        # Check that the tracker was created correctly
        assert tracker.task_id == "test_create"
        assert tracker.total_steps == 10
        assert tracker.description == "Test creation"

        # Check that the tracker was registered
        assert get_progress_tracker("test_create") is tracker

    def test_create_progress_tracker_with_parent(self):
        """Test creating a progress tracker with a parent."""
        # Create a parent tracker
        parent = create_progress_tracker(task_id="parent")

        # Create a child tracker
        child = create_progress_tracker(
            task_id="child",
            parent_id="parent",
        )

        # Check that the child has the correct parent
        assert child.parent is parent
