"""
Unit test for the ResultAggregator classes.

This module contains tests for the ResultAggregator classes, which are core components
of the agent coordination system.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry
from augment_adam.ai_agent.coordination.task import Task, TaskStatus, TaskResult
from augment_adam.ai_agent.coordination.aggregation import (
    ResultAggregator, SimpleAggregator, WeightedAggregator, VotingAggregator
)


@safe_tag("testing.unit.ai_agent.coordination.result_aggregator")
class TestResultAggregator(unittest.TestCase):
    """
    Tests for the ResultAggregator classes.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create test results
        self.result1 = TaskResult(
            task_id="task1",
            agent_id="agent1",
            output="Result from agent 1",
            status=TaskStatus.COMPLETED
        )
        
        self.result2 = TaskResult(
            task_id="task1",
            agent_id="agent2",
            output="Result from agent 2",
            status=TaskStatus.COMPLETED
        )
        
        self.result3 = TaskResult(
            task_id="task1",
            agent_id="agent3",
            output="Result from agent 3",
            status=TaskStatus.FAILED,
            error="Error from agent 3"
        )
        
        self.numeric_result1 = TaskResult(
            task_id="task2",
            agent_id="agent1",
            output=10,
            status=TaskStatus.COMPLETED
        )
        
        self.numeric_result2 = TaskResult(
            task_id="task2",
            agent_id="agent2",
            output=20,
            status=TaskStatus.COMPLETED
        )
        
        self.list_result1 = TaskResult(
            task_id="task3",
            agent_id="agent1",
            output=["item1", "item2"],
            status=TaskStatus.COMPLETED
        )
        
        self.list_result2 = TaskResult(
            task_id="task3",
            agent_id="agent2",
            output=["item3", "item4"],
            status=TaskStatus.COMPLETED
        )
        
        # Create aggregators
        self.simple_first = SimpleAggregator(strategy="first_success")
        self.simple_last = SimpleAggregator(strategy="last_success")
        self.simple_concat = SimpleAggregator(strategy="concatenate")
        
        self.weighted = WeightedAggregator(
            weights={"agent1": 0.7, "agent2": 0.3}
        )
        
        self.voting_majority = VotingAggregator(voting_method="majority")
        self.voting_plurality = VotingAggregator(voting_method="plurality")
    
    def test_simple_aggregator_first_success(self):
        """Test the SimpleAggregator with first_success strategy."""
        # Aggregate results
        result = self.simple_first.aggregate([self.result1, self.result2, self.result3])
        
        # Verify the result
        self.assertEqual(result.output, "Result from agent 1")
        self.assertEqual(result.agent_id, "agent1")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Test with only failed results
        result = self.simple_first.aggregate([self.result3])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "Error from agent 3")
        
        # Test with no results
        result = self.simple_first.aggregate([])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "No results to aggregate")
    
    def test_simple_aggregator_last_success(self):
        """Test the SimpleAggregator with last_success strategy."""
        # Aggregate results
        result = self.simple_last.aggregate([self.result1, self.result2, self.result3])
        
        # Verify the result
        self.assertEqual(result.output, "Result from agent 2")
        self.assertEqual(result.agent_id, "agent2")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Test with only failed results
        result = self.simple_last.aggregate([self.result3])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "Error from agent 3")
        
        # Test with no results
        result = self.simple_last.aggregate([])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "No results to aggregate")
    
    def test_simple_aggregator_concatenate(self):
        """Test the SimpleAggregator with concatenate strategy."""
        # Aggregate results
        result = self.simple_concat.aggregate([self.result1, self.result2, self.result3])
        
        # Verify the result
        self.assertIn("Result from agent 1", result.output)
        self.assertIn("Result from agent 2", result.output)
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Test with only failed results
        result = self.simple_concat.aggregate([self.result3])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "Error from agent 3")
        
        # Test with no results
        result = self.simple_concat.aggregate([])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "No results to aggregate")
        
        # Test with list results
        result = self.simple_concat.aggregate([self.list_result1, self.list_result2])
        
        # Verify the result
        self.assertEqual(len(result.output), 4)
        self.assertIn("item1", result.output)
        self.assertIn("item2", result.output)
        self.assertIn("item3", result.output)
        self.assertIn("item4", result.output)
    
    def test_weighted_aggregator_numeric(self):
        """Test the WeightedAggregator with numeric outputs."""
        # Aggregate numeric results
        result = self.weighted.aggregate([self.numeric_result1, self.numeric_result2])
        
        # Verify the result
        # Expected: (10 * 0.7 + 20 * 0.3) = 7 + 6 = 13
        self.assertEqual(result.output, 13)
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("aggregated_from", result.metadata)
        self.assertIn("weights", result.metadata)
        self.assertEqual(len(result.metadata["aggregated_from"]), 2)
        self.assertEqual(len(result.metadata["weights"]), 2)
        
        # Test with only one result
        result = self.weighted.aggregate([self.numeric_result1])
        
        # Verify the result
        self.assertEqual(result.output, 10)
        self.assertEqual(result.agent_id, "agent1")
        
        # Test with no results
        result = self.weighted.aggregate([])
        
        # Verify the result
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertEqual(result.error, "No results to aggregate")
    
    def test_weighted_aggregator_string(self):
        """Test the WeightedAggregator with string outputs."""
        # Aggregate string results
        result = self.weighted.aggregate([self.result1, self.result2])
        
        # Verify the result
        self.assertIn("[Weight: 0.70] Result from agent 1", result.output)
        self.assertIn("[Weight: 0.30] Result from agent 2", result.output)
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("aggregated_from", result.metadata)
        self.assertIn("weights", result.metadata)
        self.assertEqual(len(result.metadata["aggregated_from"]), 2)
        self.assertEqual(len(result.metadata["weights"]), 2)
    
    def test_weighted_aggregator_list(self):
        """Test the WeightedAggregator with list outputs."""
        # Aggregate list results
        result = self.weighted.aggregate([self.list_result1, self.list_result2])
        
        # Verify the result
        self.assertEqual(len(result.output), 4)
        
        # Check that each item has the expected structure
        for item in result.output:
            self.assertIn("item", item)
            self.assertIn("weight", item)
            self.assertIn("agent_id", item)
            
            if item["agent_id"] == "agent1":
                self.assertEqual(item["weight"], 0.7)
                self.assertIn(item["item"], ["item1", "item2"])
            elif item["agent_id"] == "agent2":
                self.assertEqual(item["weight"], 0.3)
                self.assertIn(item["item"], ["item3", "item4"])
    
    def test_weighted_aggregator_mixed(self):
        """Test the WeightedAggregator with mixed output types."""
        # Create results with different output types
        mixed_result1 = TaskResult(
            task_id="task4",
            agent_id="agent1",
            output=10,
            status=TaskStatus.COMPLETED
        )
        
        mixed_result2 = TaskResult(
            task_id="task4",
            agent_id="agent2",
            output="string output",
            status=TaskStatus.COMPLETED
        )
        
        # Aggregate mixed results
        result = self.weighted.aggregate([mixed_result1, mixed_result2])
        
        # Verify the result (should select the highest weighted result)
        self.assertEqual(result.output, 10)
        self.assertEqual(result.agent_id, "agent1")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("aggregated_from", result.metadata)
        self.assertIn("weights", result.metadata)
        self.assertIn("selected_agent", result.metadata)
        self.assertEqual(result.metadata["selected_agent"], "agent1")
    
    def test_voting_aggregator_majority(self):
        """Test the VotingAggregator with majority voting."""
        # Create identical results to get a majority
        result1a = TaskResult(
            task_id="task5",
            agent_id="agent1",
            output="Majority output",
            status=TaskStatus.COMPLETED
        )
        
        result2a = TaskResult(
            task_id="task5",
            agent_id="agent2",
            output="Majority output",
            status=TaskStatus.COMPLETED
        )
        
        result3a = TaskResult(
            task_id="task5",
            agent_id="agent3",
            output="Minority output",
            status=TaskStatus.COMPLETED
        )
        
        # Aggregate results
        result = self.voting_majority.aggregate([result1a, result2a, result3a])
        
        # Verify the result
        self.assertEqual(result.output, "Majority output")
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("aggregated_from", result.metadata)
        self.assertIn("vote_count", result.metadata)
        self.assertIn("total_votes", result.metadata)
        self.assertEqual(result.metadata["vote_count"], 2)
        self.assertEqual(result.metadata["total_votes"], 3)
        
        # Test with no majority
        result1b = TaskResult(
            task_id="task6",
            agent_id="agent1",
            output="Output 1",
            status=TaskStatus.COMPLETED
        )
        
        result2b = TaskResult(
            task_id="task6",
            agent_id="agent2",
            output="Output 2",
            status=TaskStatus.COMPLETED
        )
        
        result3b = TaskResult(
            task_id="task6",
            agent_id="agent3",
            output="Output 3",
            status=TaskStatus.COMPLETED
        )
        
        # Aggregate results
        result = self.voting_majority.aggregate([result1b, result2b, result3b])
        
        # Verify the result (should fall back to plurality)
        self.assertIn(result.output, ["Output 1", "Output 2", "Output 3"])
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("voting_method", result.metadata)
        self.assertEqual(result.metadata["voting_method"], "plurality")
    
    def test_voting_aggregator_plurality(self):
        """Test the VotingAggregator with plurality voting."""
        # Create results with a plurality
        result1a = TaskResult(
            task_id="task7",
            agent_id="agent1",
            output="Plurality output",
            status=TaskStatus.COMPLETED
        )
        
        result2a = TaskResult(
            task_id="task7",
            agent_id="agent2",
            output="Plurality output",
            status=TaskStatus.COMPLETED
        )
        
        result3a = TaskResult(
            task_id="task7",
            agent_id="agent3",
            output="Output 1",
            status=TaskStatus.COMPLETED
        )
        
        result4a = TaskResult(
            task_id="task7",
            agent_id="agent4",
            output="Output 2",
            status=TaskStatus.COMPLETED
        )
        
        # Aggregate results
        result = self.voting_plurality.aggregate([result1a, result2a, result3a, result4a])
        
        # Verify the result
        self.assertEqual(result.output, "Plurality output")
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertIn("aggregated_from", result.metadata)
        self.assertIn("vote_count", result.metadata)
        self.assertIn("total_votes", result.metadata)
        self.assertEqual(result.metadata["vote_count"], 2)
        self.assertEqual(result.metadata["total_votes"], 4)
        
        # Test with a tie
        result1b = TaskResult(
            task_id="task8",
            agent_id="agent1",
            output="Output A",
            status=TaskStatus.COMPLETED
        )
        
        result2b = TaskResult(
            task_id="task8",
            agent_id="agent2",
            output="Output A",
            status=TaskStatus.COMPLETED
        )
        
        result3b = TaskResult(
            task_id="task8",
            agent_id="agent3",
            output="Output B",
            status=TaskStatus.COMPLETED
        )
        
        result4b = TaskResult(
            task_id="task8",
            agent_id="agent4",
            output="Output B",
            status=TaskStatus.COMPLETED
        )
        
        # Aggregate results
        result = self.voting_plurality.aggregate([result1b, result2b, result3b, result4b])
        
        # Verify the result (should be either Output A or Output B)
        self.assertIn(result.output, ["Output A", "Output B"])
        self.assertEqual(result.agent_id, "aggregated")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Check metadata
        self.assertEqual(result.metadata["vote_count"], 2)
        self.assertEqual(result.metadata["total_votes"], 4)
    
    def test_custom_aggregator(self):
        """Test creating a custom ResultAggregator."""
        # Create a custom aggregator
        class CustomAggregator(ResultAggregator):
            def aggregate(self, results):
                # Return a result with all agent IDs concatenated
                agent_ids = [result.agent_id for result in results if result.is_successful()]
                return TaskResult(
                    task_id="custom",
                    agent_id="custom",
                    output=",".join(agent_ids),
                    status=TaskStatus.COMPLETED
                )
        
        # Create an instance of the custom aggregator
        custom = CustomAggregator(name="custom-aggregator")
        
        # Verify the aggregator was initialized correctly
        self.assertEqual(custom.name, "custom-aggregator")
        
        # Aggregate results
        result = custom.aggregate([self.result1, self.result2, self.result3])
        
        # Verify the result
        self.assertEqual(result.output, "agent1,agent2")
        self.assertEqual(result.agent_id, "custom")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
    
if __name__ == "__main__":
    unittest.main()
