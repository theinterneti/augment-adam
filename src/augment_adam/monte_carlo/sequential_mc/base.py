"""
Base classes for sequential Monte Carlo.

This module provides the base classes for sequential Monte Carlo, including
the SequentialMonteCarlo class and model interfaces.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')  # Type of state
O = TypeVar('O')  # Type of observation


@tag("monte_carlo.sequential_mc")
class SMCState(Generic[T]):
    """
    State for sequential Monte Carlo.
    
    This class represents a state in sequential Monte Carlo, which consists
    of a value and a weight.
    
    Attributes:
        value: The value of the state.
        weight: The weight of the state.
        metadata: Additional metadata for the state.
    
    TODO(Issue #9): Add support for state history
    TODO(Issue #9): Implement state validation
    """
    
    def __init__(self, value: T, weight: float = 1.0) -> None:
        """
        Initialize the state.
        
        Args:
            value: The value of the state.
            weight: The weight of the state.
        """
        self.value = value
        self.weight = weight
        self.metadata: Dict[str, Any] = {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the state.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the state.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.sequential_mc")
class TransitionModel(Generic[T], ABC):
    """
    Transition model for sequential Monte Carlo.
    
    This class defines the interface for transition models in sequential Monte Carlo,
    which describe how the state evolves over time.
    
    Attributes:
        name: The name of the transition model.
        metadata: Additional metadata for the transition model.
    
    TODO(Issue #9): Add support for time-varying transition models
    TODO(Issue #9): Implement transition model validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the transition model.
        
        Args:
            name: The name of the transition model.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def sample(self, state: T) -> T:
        """
        Sample the next state given the current state.
        
        Args:
            state: The current state.
            
        Returns:
            The next state.
        """
        pass
    
    @abstractmethod
    def pdf(self, next_state: T, current_state: T) -> float:
        """
        Compute the probability density function (PDF) of the next state given the current state.
        
        Args:
            next_state: The next state.
            current_state: The current state.
            
        Returns:
            The PDF value.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the transition model.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the transition model.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.sequential_mc")
class LikelihoodModel(Generic[T, O], ABC):
    """
    Likelihood model for sequential Monte Carlo.
    
    This class defines the interface for likelihood models in sequential Monte Carlo,
    which describe the likelihood of observations given the state.
    
    Attributes:
        name: The name of the likelihood model.
        metadata: Additional metadata for the likelihood model.
    
    TODO(Issue #9): Add support for time-varying likelihood models
    TODO(Issue #9): Implement likelihood model validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the likelihood model.
        
        Args:
            name: The name of the likelihood model.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def likelihood(self, observation: O, state: T) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            observation: The observation.
            state: The state.
            
        Returns:
            The likelihood value.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the likelihood model.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the likelihood model.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.sequential_mc")
class SequentialMonteCarlo(Generic[T, O]):
    """
    Sequential Monte Carlo for dynamic systems.
    
    This class implements sequential Monte Carlo for dynamic systems with
    evolving states, using a set of particles to represent the probability
    distribution of the state.
    
    Attributes:
        name: The name of the sequential Monte Carlo.
        metadata: Additional metadata for the sequential Monte Carlo.
        states: The states in the sequential Monte Carlo.
        transition_model: The transition model.
        likelihood_model: The likelihood model.
        resampling_threshold: The threshold for effective sample size.
    
    TODO(Issue #9): Add support for sequential Monte Carlo diagnostics
    TODO(Issue #9): Implement sequential Monte Carlo validation
    """
    
    def __init__(
        self,
        transition_model: TransitionModel[T],
        likelihood_model: LikelihoodModel[T, O],
        num_particles: int = 100,
        resampling_threshold: float = 0.5,
        name: str = "sequential_monte_carlo"
    ) -> None:
        """
        Initialize the sequential Monte Carlo.
        
        Args:
            transition_model: The transition model.
            likelihood_model: The likelihood model.
            num_particles: The number of particles.
            resampling_threshold: The threshold for effective sample size.
            name: The name of the sequential Monte Carlo.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        
        self.states: List[SMCState[T]] = []
        self.transition_model = transition_model
        self.likelihood_model = likelihood_model
        self.resampling_threshold = resampling_threshold
        
        self.metadata["num_particles"] = num_particles
        self.metadata["resampling_threshold"] = resampling_threshold
    
    def initialize(self, initial_states: List[T]) -> None:
        """
        Initialize the sequential Monte Carlo with a set of states.
        
        Args:
            initial_states: The initial states.
        """
        self.states = [SMCState(state, 1.0 / len(initial_states)) for state in initial_states]
    
    def predict(self) -> None:
        """
        Predict the next states.
        """
        # Sample next states
        next_states = []
        for state in self.states:
            next_value = self.transition_model.sample(state.value)
            next_states.append(SMCState(next_value, state.weight))
        
        self.states = next_states
    
    def update(self, observation: O) -> None:
        """
        Update the weights of the states based on an observation.
        
        Args:
            observation: The observation.
        """
        # Compute likelihoods
        likelihoods = [self.likelihood_model.likelihood(observation, state.value) for state in self.states]
        
        # Update weights
        for i, state in enumerate(self.states):
            state.weight *= likelihoods[i]
        
        # Normalize weights
        total_weight = sum(state.weight for state in self.states)
        if total_weight > 0:
            for state in self.states:
                state.weight /= total_weight
        else:
            # If all weights are zero, reset to uniform weights
            for state in self.states:
                state.weight = 1.0 / len(self.states)
        
        # Check if resampling is needed
        if self._compute_effective_sample_size() < self.resampling_threshold * len(self.states):
            self._resample()
    
    def estimate_state(self) -> T:
        """
        Estimate the current state.
        
        Returns:
            The estimated state.
        """
        # Compute weighted average of states
        if isinstance(self.states[0].value, (int, float)):
            # For scalar states
            return sum(state.value * state.weight for state in self.states)
        elif isinstance(self.states[0].value, np.ndarray):
            # For vector states
            return sum(state.value * state.weight for state in self.states)
        else:
            # For other types, return the state with the highest weight
            return max(self.states, key=lambda s: s.weight).value
    
    def get_states(self) -> List[SMCState[T]]:
        """
        Get the states.
        
        Returns:
            The states.
        """
        return self.states
    
    def _compute_effective_sample_size(self) -> float:
        """
        Compute the effective sample size of the states.
        
        Returns:
            The effective sample size.
        """
        return 1.0 / sum(state.weight ** 2 for state in self.states)
    
    def _resample(self) -> None:
        """
        Resample the states based on their weights.
        """
        # Get weights
        weights = [state.weight for state in self.states]
        
        # Sample indices
        indices = np.random.choice(
            len(self.states),
            size=len(self.states),
            replace=True,
            p=weights
        )
        
        # Create new states
        resampled_states = []
        for index in indices:
            # Create a new state with the same value but uniform weight
            resampled_states.append(SMCState(
                value=self.states[index].value,
                weight=1.0 / len(self.states)
            ))
        
        self.states = resampled_states
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the sequential Monte Carlo.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the sequential Monte Carlo.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
