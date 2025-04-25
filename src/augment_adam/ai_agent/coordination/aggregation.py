"""
Result Aggregation module.

This module provides aggregators for combining results from multiple agents.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from abc import ABC, abstractmethod

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.task import Task, TaskResult, TaskStatus


@tag("ai_agent.coordination")
class ResultAggregator(ABC):
    """
    Base class for result aggregators.
    
    This class defines the interface for result aggregators, which combine
    results from multiple agents into a single result.
    
    Attributes:
        name: The name of the aggregator.
        metadata: Additional metadata for the aggregator.
    
    TODO(Issue #8): Add support for aggregator validation
    TODO(Issue #8): Implement aggregator analytics
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the result aggregator.
        
        Args:
            name: The name of the aggregator.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate multiple task results into a single result.
        
        Args:
            results: The task results to aggregate.
            
        Returns:
            The aggregated result.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the aggregator.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the aggregator.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("ai_agent.coordination")
class SimpleAggregator(ResultAggregator):
    """
    Simple result aggregator that combines results using a specified strategy.
    
    This class implements a result aggregator that combines results using
    a simple strategy, such as taking the first successful result or concatenating all results.
    
    Attributes:
        name: The name of the aggregator.
        metadata: Additional metadata for the aggregator.
        strategy: The aggregation strategy to use.
    
    TODO(Issue #8): Add support for more aggregation strategies
    TODO(Issue #8): Implement aggregator validation
    """
    
    def __init__(self, name: str = "simple_aggregator", strategy: str = "first_success") -> None:
        """
        Initialize the simple result aggregator.
        
        Args:
            name: The name of the aggregator.
            strategy: The aggregation strategy to use ("first_success", "last_success", "concatenate").
        """
        super().__init__(name)
        self.strategy = strategy
        self.metadata["strategy"] = strategy
    
    def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate multiple task results into a single result.
        
        Args:
            results: The task results to aggregate.
            
        Returns:
            The aggregated result.
        """
        # If there are no results, return a failed result
        if not results:
            return TaskResult(
                task_id="",
                agent_id="",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # If there's only one result, return it
        if len(results) == 1:
            return results[0]
        
        # Apply the aggregation strategy
        if self.strategy == "first_success":
            # Return the first successful result
            for result in results:
                if result.is_successful():
                    return result
            
            # If there are no successful results, return the first result
            return results[0]
        
        elif self.strategy == "last_success":
            # Return the last successful result
            for result in reversed(results):
                if result.is_successful():
                    return result
            
            # If there are no successful results, return the last result
            return results[-1]
        
        elif self.strategy == "concatenate":
            # Concatenate all successful results
            successful_results = [result for result in results if result.is_successful()]
            
            # If there are no successful results, return the first result
            if not successful_results:
                return results[0]
            
            # Concatenate the outputs
            concatenated_output = []
            for result in successful_results:
                if isinstance(result.output, str):
                    concatenated_output.append(result.output)
                elif isinstance(result.output, list):
                    concatenated_output.extend(result.output)
                else:
                    concatenated_output.append(result.output)
            
            # Create a new result with the concatenated output
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=concatenated_output,
                status=TaskStatus.COMPLETED,
                metadata={"aggregated_from": [result.agent_id for result in successful_results]}
            )
        
        else:
            # Unknown strategy, return the first result
            return results[0]


@tag("ai_agent.coordination")
class WeightedAggregator(ResultAggregator):
    """
    Weighted result aggregator that combines results using weights.
    
    This class implements a result aggregator that combines results using
    weights assigned to each agent or result.
    
    Attributes:
        name: The name of the aggregator.
        metadata: Additional metadata for the aggregator.
        weights: Dictionary of weights, keyed by agent ID.
        default_weight: Default weight for agents without a specific weight.
    
    TODO(Issue #8): Add support for more weighting strategies
    TODO(Issue #8): Implement aggregator validation
    """
    
    def __init__(
        self,
        name: str = "weighted_aggregator",
        weights: Optional[Dict[str, float]] = None,
        default_weight: float = 1.0
    ) -> None:
        """
        Initialize the weighted result aggregator.
        
        Args:
            name: The name of the aggregator.
            weights: Dictionary of weights, keyed by agent ID.
            default_weight: Default weight for agents without a specific weight.
        """
        super().__init__(name)
        self.weights = weights or {}
        self.default_weight = default_weight
        self.metadata["weights"] = self.weights
        self.metadata["default_weight"] = default_weight
    
    def set_weight(self, agent_id: str, weight: float) -> None:
        """
        Set the weight for an agent.
        
        Args:
            agent_id: The ID of the agent.
            weight: The weight to assign to the agent.
        """
        self.weights[agent_id] = weight
        self.metadata["weights"] = self.weights
    
    def get_weight(self, agent_id: str) -> float:
        """
        Get the weight for an agent.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The weight assigned to the agent, or the default weight if none is assigned.
        """
        return self.weights.get(agent_id, self.default_weight)
    
    def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate multiple task results into a single result using weights.
        
        Args:
            results: The task results to aggregate.
            
        Returns:
            The aggregated result.
        """
        # If there are no results, return a failed result
        if not results:
            return TaskResult(
                task_id="",
                agent_id="",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # If there's only one result, return it
        if len(results) == 1:
            return results[0]
        
        # Filter successful results
        successful_results = [result for result in results if result.is_successful()]
        
        # If there are no successful results, return the first result
        if not successful_results:
            return results[0]
        
        # Calculate weights for each result
        weighted_results = [(result, self.get_weight(result.agent_id)) for result in successful_results]
        total_weight = sum(weight for _, weight in weighted_results)
        
        # If all weights are zero, use equal weights
        if total_weight == 0:
            total_weight = len(weighted_results)
            weighted_results = [(result, 1.0) for result in successful_results]
        
        # Normalize weights
        normalized_weights = [(result, weight / total_weight) for result, weight in weighted_results]
        
        # Combine outputs based on weights
        if all(isinstance(result.output, (int, float)) for result, _ in normalized_weights):
            # For numeric outputs, calculate weighted average
            weighted_output = sum(result.output * weight for result, weight in normalized_weights)
            
            # Create a new result with the weighted output
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=weighted_output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [result.agent_id for result in successful_results],
                    "weights": {result.agent_id: weight for result, weight in normalized_weights}
                }
            )
        
        elif all(isinstance(result.output, str) for result, _ in normalized_weights):
            # For string outputs, concatenate with weights as prefixes
            weighted_output = "\n\n".join(
                f"[Weight: {weight:.2f}] {result.output}"
                for result, weight in normalized_weights
            )
            
            # Create a new result with the weighted output
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=weighted_output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [result.agent_id for result in successful_results],
                    "weights": {result.agent_id: weight for result, weight in normalized_weights}
                }
            )
        
        elif all(isinstance(result.output, list) for result, _ in normalized_weights):
            # For list outputs, create a weighted list of items
            weighted_output = []
            for result, weight in normalized_weights:
                for item in result.output:
                    weighted_output.append({
                        "item": item,
                        "weight": weight,
                        "agent_id": result.agent_id
                    })
            
            # Create a new result with the weighted output
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=weighted_output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [result.agent_id for result in successful_results],
                    "weights": {result.agent_id: weight for result, weight in normalized_weights}
                }
            )
        
        else:
            # For mixed or unsupported output types, return the result with the highest weight
            best_result, _ = max(weighted_results, key=lambda x: x[1])
            
            # Create a new result with the best output
            return TaskResult(
                task_id=best_result.task_id,
                agent_id=best_result.agent_id,
                output=best_result.output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [result.agent_id for result in successful_results],
                    "weights": {result.agent_id: weight for result, weight in normalized_weights},
                    "selected_agent": best_result.agent_id
                }
            )


@tag("ai_agent.coordination")
class VotingAggregator(ResultAggregator):
    """
    Voting result aggregator that combines results using voting.
    
    This class implements a result aggregator that combines results using
    voting, where each agent's result counts as a vote.
    
    Attributes:
        name: The name of the aggregator.
        metadata: Additional metadata for the aggregator.
        voting_method: The voting method to use.
    
    TODO(Issue #8): Add support for more voting methods
    TODO(Issue #8): Implement aggregator validation
    """
    
    def __init__(self, name: str = "voting_aggregator", voting_method: str = "majority") -> None:
        """
        Initialize the voting result aggregator.
        
        Args:
            name: The name of the aggregator.
            voting_method: The voting method to use ("majority", "plurality").
        """
        super().__init__(name)
        self.voting_method = voting_method
        self.metadata["voting_method"] = voting_method
    
    def aggregate(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate multiple task results into a single result using voting.
        
        Args:
            results: The task results to aggregate.
            
        Returns:
            The aggregated result.
        """
        # If there are no results, return a failed result
        if not results:
            return TaskResult(
                task_id="",
                agent_id="",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # If there's only one result, return it
        if len(results) == 1:
            return results[0]
        
        # Filter successful results
        successful_results = [result for result in results if result.is_successful()]
        
        # If there are no successful results, return the first result
        if not successful_results:
            return results[0]
        
        # Count votes for each output
        votes = {}
        for result in successful_results:
            # Convert the output to a hashable type
            if isinstance(result.output, (list, dict)):
                output_key = str(result.output)
            else:
                output_key = result.output
            
            if output_key not in votes:
                votes[output_key] = {
                    "count": 0,
                    "results": []
                }
            
            votes[output_key]["count"] += 1
            votes[output_key]["results"].append(result)
        
        # Apply the voting method
        if self.voting_method == "majority":
            # Majority voting requires more than 50% of votes
            for output_key, vote_data in votes.items():
                if vote_data["count"] > len(successful_results) / 2:
                    # Majority found
                    result = vote_data["results"][0]
                    return TaskResult(
                        task_id=result.task_id,
                        agent_id="aggregated",
                        output=result.output,
                        status=TaskStatus.COMPLETED,
                        metadata={
                            "aggregated_from": [r.agent_id for r in vote_data["results"]],
                            "vote_count": vote_data["count"],
                            "total_votes": len(successful_results)
                        }
                    )
            
            # No majority found, fall back to plurality
            self.voting_method = "plurality"
        
        if self.voting_method == "plurality":
            # Plurality voting selects the option with the most votes
            best_output_key = max(votes.keys(), key=lambda k: votes[k]["count"])
            vote_data = votes[best_output_key]
            result = vote_data["results"][0]
            
            return TaskResult(
                task_id=result.task_id,
                agent_id="aggregated",
                output=result.output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [r.agent_id for r in vote_data["results"]],
                    "vote_count": vote_data["count"],
                    "total_votes": len(successful_results),
                    "voting_method": "plurality"
                }
            )
        
        # Unknown voting method, return the first result
        return successful_results[0]
