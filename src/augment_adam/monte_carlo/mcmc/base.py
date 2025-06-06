"""
Base classes for Markov Chain Monte Carlo.

This module provides the base classes for Markov Chain Monte Carlo (MCMC),
including the MarkovChainMonteCarlo class and sample interfaces.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')  # Type of sample


@tag("monte_carlo.mcmc")
class MCMCSample(Generic[T]):
    """
    Sample in a Markov Chain Monte Carlo.
    
    This class represents a sample in a Markov Chain Monte Carlo, which consists
    of a value and associated metadata.
    
    Attributes:
        value: The value of the sample.
        log_probability: The log probability of the sample.
        metadata: Additional metadata for the sample.
    
    TODO(Issue #9): Add support for sample history
    TODO(Issue #9): Implement sample validation
    """
    
    def __init__(self, value: T, log_probability: float = 0.0) -> None:
        """
        Initialize the sample.
        
        Args:
            value: The value of the sample.
            log_probability: The log probability of the sample.
        """
        self.value = value
        self.log_probability = log_probability
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


@tag("monte_carlo.mcmc")
class ProposalDistribution(Generic[T], ABC):
    """
    Proposal distribution for Markov Chain Monte Carlo.
    
    This class defines the interface for proposal distributions in MCMC,
    which are used to propose new samples in the Markov chain.
    
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
    def propose(self, current: T) -> T:
        """
        Propose a new sample given the current sample.
        
        Args:
            current: The current sample.
            
        Returns:
            The proposed sample.
        """
        pass
    
    @abstractmethod
    def log_probability(self, proposed: T, current: T) -> float:
        """
        Compute the log probability of proposing a sample.
        
        Args:
            proposed: The proposed sample.
            current: The current sample.
            
        Returns:
            The log probability of proposing the sample.
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


@tag("monte_carlo.mcmc")
class MarkovChainMonteCarlo(Generic[T], ABC):
    """
    Base class for Markov Chain Monte Carlo methods.
    
    This class defines the interface for Markov Chain Monte Carlo methods,
    which are used to sample from complex distributions.
    
    Attributes:
        name: The name of the MCMC method.
        metadata: Additional metadata for the MCMC method.
        samples: The samples generated by the MCMC method.
        target_log_prob_fn: The target log probability function.
    
    TODO(Issue #9): Add support for MCMC diagnostics
    TODO(Issue #9): Implement MCMC validation
    """
    
    def __init__(
        self,
        target_log_prob_fn: Callable[[T], float],
        name: str
    ) -> None:
        """
        Initialize the MCMC method.
        
        Args:
            target_log_prob_fn: The target log probability function.
            name: The name of the MCMC method.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        
        self.samples: List[MCMCSample[T]] = []
        self.target_log_prob_fn = target_log_prob_fn
    
    @abstractmethod
    def sample(
        self,
        initial_state: T,
        num_samples: int,
        num_burnin: int = 0,
        thin: int = 1
    ) -> List[MCMCSample[T]]:
        """
        Generate samples using the MCMC method.
        
        Args:
            initial_state: The initial state of the Markov chain.
            num_samples: The number of samples to generate.
            num_burnin: The number of burn-in samples to discard.
            thin: The thinning factor.
            
        Returns:
            The generated samples.
        """
        pass
    
    def get_samples(self) -> List[MCMCSample[T]]:
        """
        Get the samples generated by the MCMC method.
        
        Returns:
            The samples.
        """
        return self.samples
    
    def get_sample_values(self) -> List[T]:
        """
        Get the values of the samples generated by the MCMC method.
        
        Returns:
            The sample values.
        """
        return [sample.value for sample in self.samples]
    
    def compute_acceptance_rate(self) -> float:
        """
        Compute the acceptance rate of the MCMC method.
        
        Returns:
            The acceptance rate.
        """
        if not self.samples:
            return 0.0
        
        accepted = sum(1 for sample in self.samples if sample.get_metadata("accepted", False))
        return accepted / len(self.samples)
    
    def compute_effective_sample_size(self) -> float:
        """
        Compute the effective sample size of the MCMC method.
        
        Returns:
            The effective sample size.
        """
        if not self.samples:
            return 0.0
        
        # Compute autocorrelation
        values = self.get_sample_values()
        if isinstance(values[0], np.ndarray):
            # For vector samples, compute autocorrelation for each dimension
            autocorr = np.zeros(min(50, len(values) // 2))
            for i in range(len(autocorr)):
                autocorr[i] = np.mean([
                    np.corrcoef(
                        [values[j][dim] for j in range(len(values) - i)],
                        [values[j + i][dim] for j in range(len(values) - i)]
                    )[0, 1]
                    for dim in range(len(values[0]))
                ])
        else:
            # For scalar samples, compute autocorrelation directly
            autocorr = np.zeros(min(50, len(values) // 2))
            for i in range(len(autocorr)):
                autocorr[i] = np.corrcoef(
                    values[:-i] if i > 0 else values,
                    values[i:] if i > 0 else values
                )[0, 1]
        
        # Compute effective sample size
        if autocorr[1:].sum() == 0:
            return len(values)
        
        ess = len(values) / (1 + 2 * autocorr[1:].sum())
        return ess
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the MCMC method.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the MCMC method.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
