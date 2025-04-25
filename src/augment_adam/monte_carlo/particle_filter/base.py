"""
Base classes for particle filtering.

This module provides the base classes for particle filtering, including
the ParticleFilter class, Particle class, and model interfaces.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')  # Type of state
O = TypeVar('O')  # Type of observation


@tag("monte_carlo.particle_filter")
class Particle(Generic[T]):
    """
    Particle for particle filtering.
    
    This class represents a particle in a particle filter, which consists
    of a state and a weight.
    
    Attributes:
        state: The state of the particle.
        weight: The weight of the particle.
        metadata: Additional metadata for the particle.
    
    TODO(Issue #9): Add support for particle history
    TODO(Issue #9): Implement particle validation
    """
    
    def __init__(self, state: T, weight: float = 1.0) -> None:
        """
        Initialize the particle.
        
        Args:
            state: The state of the particle.
            weight: The weight of the particle.
        """
        self.state = state
        self.weight = weight
        self.metadata: Dict[str, Any] = {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the particle.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the particle.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.particle_filter")
class SystemModel(Generic[T], ABC):
    """
    System model for particle filtering.
    
    This class defines the interface for system models in particle filtering,
    which describe how the state evolves over time.
    
    Attributes:
        name: The name of the system model.
        metadata: Additional metadata for the system model.
    
    TODO(Issue #9): Add support for time-varying system models
    TODO(Issue #9): Implement system model validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the system model.
        
        Args:
            name: The name of the system model.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def propagate(self, state: T, dt: float) -> T:
        """
        Propagate the state forward in time.
        
        Args:
            state: The current state.
            dt: The time step.
            
        Returns:
            The propagated state.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the system model.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the system model.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.particle_filter")
class ObservationModel(Generic[T, O], ABC):
    """
    Observation model for particle filtering.
    
    This class defines the interface for observation models in particle filtering,
    which describe how observations are generated from the state.
    
    Attributes:
        name: The name of the observation model.
        metadata: Additional metadata for the observation model.
    
    TODO(Issue #9): Add support for time-varying observation models
    TODO(Issue #9): Implement observation model validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the observation model.
        
        Args:
            name: The name of the observation model.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def likelihood(self, state: T, observation: O) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            state: The state.
            observation: The observation.
            
        Returns:
            The likelihood of the observation given the state.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the observation model.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the observation model.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.particle_filter")
class ResamplingStrategy(Generic[T], ABC):
    """
    Resampling strategy for particle filtering.
    
    This class defines the interface for resampling strategies in particle filtering,
    which determine how particles are resampled based on their weights.
    
    Attributes:
        name: The name of the resampling strategy.
        metadata: Additional metadata for the resampling strategy.
    
    TODO(Issue #9): Add support for adaptive resampling
    TODO(Issue #9): Implement resampling strategy validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the resampling strategy.
        
        Args:
            name: The name of the resampling strategy.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def resample(self, particles: List[Particle[T]]) -> List[Particle[T]]:
        """
        Resample particles based on their weights.
        
        Args:
            particles: The particles to resample.
            
        Returns:
            The resampled particles.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the resampling strategy.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the resampling strategy.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.particle_filter")
class ParticleFilter(Generic[T, O]):
    """
    Particle filter for state estimation.
    
    This class implements a particle filter for state estimation in noisy
    environments, using a set of particles to represent the probability
    distribution of the state.
    
    Attributes:
        name: The name of the particle filter.
        metadata: Additional metadata for the particle filter.
        particles: The particles in the filter.
        system_model: The system model.
        observation_model: The observation model.
        resampling_strategy: The resampling strategy.
        effective_sample_size_threshold: The threshold for effective sample size.
    
    TODO(Issue #9): Add support for particle filter diagnostics
    TODO(Issue #9): Implement particle filter validation
    """
    
    def __init__(
        self,
        system_model: SystemModel[T],
        observation_model: ObservationModel[T, O],
        resampling_strategy: ResamplingStrategy[T],
        num_particles: int = 100,
        effective_sample_size_threshold: float = 0.5,
        name: str = "particle_filter"
    ) -> None:
        """
        Initialize the particle filter.
        
        Args:
            system_model: The system model.
            observation_model: The observation model.
            resampling_strategy: The resampling strategy.
            num_particles: The number of particles.
            effective_sample_size_threshold: The threshold for effective sample size.
            name: The name of the particle filter.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        
        self.particles: List[Particle[T]] = []
        self.system_model = system_model
        self.observation_model = observation_model
        self.resampling_strategy = resampling_strategy
        self.effective_sample_size_threshold = effective_sample_size_threshold
        
        self.metadata["num_particles"] = num_particles
        self.metadata["effective_sample_size_threshold"] = effective_sample_size_threshold
    
    def initialize(self, initial_states: List[T]) -> None:
        """
        Initialize the particle filter with a set of states.
        
        Args:
            initial_states: The initial states for the particles.
        """
        self.particles = [Particle(state, 1.0 / len(initial_states)) for state in initial_states]
    
    def predict(self, dt: float) -> None:
        """
        Predict the next state of the particles.
        
        Args:
            dt: The time step.
        """
        for particle in self.particles:
            particle.state = self.system_model.propagate(particle.state, dt)
    
    def update(self, observation: O) -> None:
        """
        Update the weights of the particles based on an observation.
        
        Args:
            observation: The observation.
        """
        # Compute likelihoods
        likelihoods = [self.observation_model.likelihood(particle.state, observation) for particle in self.particles]
        
        # Update weights
        for i, particle in enumerate(self.particles):
            particle.weight *= likelihoods[i]
        
        # Normalize weights
        total_weight = sum(particle.weight for particle in self.particles)
        if total_weight > 0:
            for particle in self.particles:
                particle.weight /= total_weight
        else:
            # If all weights are zero, reset to uniform weights
            for particle in self.particles:
                particle.weight = 1.0 / len(self.particles)
        
        # Check if resampling is needed
        if self._compute_effective_sample_size() < self.effective_sample_size_threshold * len(self.particles):
            self._resample()
    
    def estimate_state(self) -> T:
        """
        Estimate the current state based on the particles.
        
        Returns:
            The estimated state.
        """
        # Compute weighted average of states
        if isinstance(self.particles[0].state, (int, float)):
            # For scalar states
            return sum(particle.state * particle.weight for particle in self.particles)
        elif isinstance(self.particles[0].state, np.ndarray):
            # For vector states
            return sum(particle.state * particle.weight for particle in self.particles)
        else:
            # For other types, return the state of the particle with the highest weight
            return max(self.particles, key=lambda p: p.weight).state
    
    def get_particles(self) -> List[Particle[T]]:
        """
        Get the particles in the filter.
        
        Returns:
            The particles.
        """
        return self.particles
    
    def _compute_effective_sample_size(self) -> float:
        """
        Compute the effective sample size of the particles.
        
        Returns:
            The effective sample size.
        """
        return 1.0 / sum(particle.weight ** 2 for particle in self.particles)
    
    def _resample(self) -> None:
        """
        Resample the particles based on their weights.
        """
        self.particles = self.resampling_strategy.resample(self.particles)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the particle filter.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the particle filter.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
