"""
Result aggregation for parallel processing.

This module provides result aggregation for parallel processing, including
combining and summarizing results from parallel tasks.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.parallel.base import TaskResult, TaskStatus


T = TypeVar('T')  # Type of result value
R = TypeVar('R')  # Type of aggregated result


@tag("parallel.utils")
class ResultAggregator(Generic[T, R]):
    """
    Aggregate results from parallel tasks.
    
    This class aggregates results from parallel tasks, combining them into a
    single result.
    
    Attributes:
        name: The name of the aggregator.
        aggregation_function: The function to use for aggregation.
        metadata: Additional metadata for the aggregator.
    
    TODO(Issue #10): Add support for more aggregation strategies
    TODO(Issue #10): Implement result validation
    """
    
    def __init__(
        self,
        name: str,
        aggregation_function: Callable[[List[T]], R]
    ) -> None:
        """
        Initialize the result aggregator.
        
        Args:
            name: The name of the aggregator.
            aggregation_function: The function to use for aggregation.
        """
        self.name = name
        self.aggregation_function = aggregation_function
        self.metadata: Dict[str, Any] = {}
    
    def aggregate(self, results: List[TaskResult[T]]) -> R:
        """
        Aggregate results.
        
        Args:
            results: The results to aggregate.
            
        Returns:
            The aggregated result.
        """
        # Extract values from successful results
        values = [result.value for result in results if result.is_success() and result.value is not None]
        
        # Aggregate values
        return self.aggregation_function(values)
    
    def aggregate_dict(self, results: Dict[str, TaskResult[T]]) -> R:
        """
        Aggregate results from a dictionary.
        
        Args:
            results: Dictionary mapping task IDs to results.
            
        Returns:
            The aggregated result.
        """
        return self.aggregate(list(results.values()))
    
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


# Common aggregation functions

def sum_aggregator(values: List[Any]) -> Any:
    """
    Aggregate by summing values.
    
    Args:
        values: The values to aggregate.
        
    Returns:
        The sum of the values.
    """
    return sum(values)


def average_aggregator(values: List[Any]) -> Any:
    """
    Aggregate by averaging values.
    
    Args:
        values: The values to aggregate.
        
    Returns:
        The average of the values.
    """
    if not values:
        return 0
    return sum(values) / len(values)


def max_aggregator(values: List[Any]) -> Any:
    """
    Aggregate by taking the maximum value.
    
    Args:
        values: The values to aggregate.
        
    Returns:
        The maximum value.
    """
    if not values:
        return None
    return max(values)


def min_aggregator(values: List[Any]) -> Any:
    """
    Aggregate by taking the minimum value.
    
    Args:
        values: The values to aggregate.
        
    Returns:
        The minimum value.
    """
    if not values:
        return None
    return min(values)


def list_aggregator(values: List[Any]) -> List[Any]:
    """
    Aggregate by returning the list of values.
    
    Args:
        values: The values to aggregate.
        
    Returns:
        The list of values.
    """
    return values


def dict_aggregator(values: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate by merging dictionaries.
    
    Args:
        values: The dictionaries to aggregate.
        
    Returns:
        The merged dictionary.
    """
    result = {}
    for value in values:
        result.update(value)
    return result
