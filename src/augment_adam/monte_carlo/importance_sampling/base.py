"""
Base classes for importance sampling.

This module provides the base classes for importance sampling, including
the ImportanceSampler class and distribution interfaces.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')  # Type of sample


@tag("monte_carlo.importance_sampling")
class WeightedSample(Generic[T]):
    """
    Weighted sample for importance sampling.
    
    This class represents a weighted sample in importance sampling, which consists
    of a sample and a weight.
    
    Attributes:
        sample: The sample.
        weight: The weight of the sample.
        metadata: Additional metadata for the sample.
    
    TODO(Issue #9): Add support for sample history
    TODO(Issue #9): Implement sample validation
    """
    
    def __init__(self, sample: T, weight: float = 1.0) -> None:
        """
        Initialize the weighted sample.
        
        Args:
            sample: The sample.
            weight: The weight of the sample.
        """
        self.sample = sample
        self.weight = weight
        self.metadata: Dict[str, Any] = {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the sample.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the sample.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.importance_sampling")
class ProposalDistribution(Generic[T], ABC):
    """
    Proposal distribution for importance sampling.
    
    This class defines the interface for proposal distributions in importance sampling,
    which are used to generate samples.
    
    Attributes:
        name: The name of the proposal distribution.
        metadata: Additional metadata for the proposal distribution.
    
    TODO(Issue #9): Add support for adaptive proposal distributions
    TODO(Issue #9): Implement proposal distribution validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the proposal distribution.
        
        Args:
            name: The name of the proposal distribution.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def sample(self) -> T:
        """
        Sample from the proposal distribution.
        
        Returns:
            A sample from the distribution.
        """
        pass
    
    @abstractmethod
    def pdf(self, x: T) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the proposal distribution.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the proposal distribution.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.importance_sampling")
class TargetDistribution(Generic[T], ABC):
    """
    Target distribution for importance sampling.
    
    This class defines the interface for target distributions in importance sampling,
    which are the distributions we want to sample from.
    
    Attributes:
        name: The name of the target distribution.
        metadata: Additional metadata for the target distribution.
    
    TODO(Issue #9): Add support for unnormalized target distributions
    TODO(Issue #9): Implement target distribution validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the target distribution.
        
        Args:
            name: The name of the target distribution.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def pdf(self, x: T) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the target distribution.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the target distribution.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.importance_sampling")
class ImportanceSampler(Generic[T]):
    """
    Importance sampler for efficient sampling from complex distributions.
    
    This class implements importance sampling, which uses a proposal distribution
    to generate samples and weights them according to the target distribution.
    
    Attributes:
        name: The name of the importance sampler.
        metadata: Additional metadata for the importance sampler.
        proposal_distribution: The proposal distribution.
        target_distribution: The target distribution.
        samples: The weighted samples.
    
    TODO(Issue #9): Add support for importance sampler diagnostics
    TODO(Issue #9): Implement importance sampler validation
    """
    
    def __init__(
        self,
        proposal_distribution: ProposalDistribution[T],
        target_distribution: TargetDistribution[T],
        name: str = "importance_sampler"
    ) -> None:
        """
        Initialize the importance sampler.
        
        Args:
            proposal_distribution: The proposal distribution.
            target_distribution: The target distribution.
            name: The name of the importance sampler.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        
        self.proposal_distribution = proposal_distribution
        self.target_distribution = target_distribution
        self.samples: List[WeightedSample[T]] = []
    
    def sample(self, num_samples: int) -> List[WeightedSample[T]]:
        """
        Generate weighted samples.
        
        Args:
            num_samples: The number of samples to generate.
            
        Returns:
            The weighted samples.
        """
        samples = []
        
        for _ in range(num_samples):
            # Sample from proposal distribution
            x = self.proposal_distribution.sample()
            
            # Compute weight
            proposal_pdf = self.proposal_distribution.pdf(x)
            target_pdf = self.target_distribution.pdf(x)
            
            if proposal_pdf > 0:
                weight = target_pdf / proposal_pdf
            else:
                weight = 0.0
            
            # Create weighted sample
            sample = WeightedSample(x, weight)
            samples.append(sample)
        
        # Store samples
        self.samples = samples
        
        return samples
    
    def get_samples(self) -> List[WeightedSample[T]]:
        """
        Get the weighted samples.
        
        Returns:
            The weighted samples.
        """
        return self.samples
    
    def get_normalized_weights(self) -> List[float]:
        """
        Get the normalized weights of the samples.
        
        Returns:
            The normalized weights.
        """
        weights = [sample.weight for sample in self.samples]
        total_weight = sum(weights)
        
        if total_weight > 0:
            return [weight / total_weight for weight in weights]
        else:
            return [1.0 / len(weights) for _ in weights]
    
    def compute_effective_sample_size(self) -> float:
        """
        Compute the effective sample size of the samples.
        
        Returns:
            The effective sample size.
        """
        weights = [sample.weight for sample in self.samples]
        total_weight = sum(weights)
        
        if total_weight > 0:
            normalized_weights = [weight / total_weight for weight in weights]
            return 1.0 / sum(w ** 2 for w in normalized_weights)
        else:
            return 0.0
    
    def estimate_expectation(self, function: Callable[[T], float]) -> float:
        """
        Estimate the expectation of a function under the target distribution.
        
        Args:
            function: The function to compute the expectation of.
            
        Returns:
            The estimated expectation.
        """
        if not self.samples:
            return 0.0
        
        # Compute weighted sum
        weighted_sum = sum(sample.weight * function(sample.sample) for sample in self.samples)
        total_weight = sum(sample.weight for sample in self.samples)
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.0
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the importance sampler.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the importance sampler.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
