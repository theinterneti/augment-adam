"""
Resampling strategies for particle filtering.

This module provides resampling strategies for particle filtering, including
multinomial, systematic, stratified, and residual resampling.
"""

import random
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.particle_filter.base import Particle, ResamplingStrategy


T = TypeVar('T')  # Type of state


@tag("monte_carlo.particle_filter")
class MultinomialResampling(ResamplingStrategy[T]):
    """
    Multinomial resampling strategy.
    
    This class implements multinomial resampling, which samples particles
    with replacement according to their weights.
    
    Attributes:
        name: The name of the resampling strategy.
        metadata: Additional metadata for the resampling strategy.
    
    TODO(Issue #9): Add support for parallel resampling
    TODO(Issue #9): Implement resampling strategy validation
    """
    
    def __init__(self, name: str = "multinomial_resampling") -> None:
        """
        Initialize the multinomial resampling strategy.
        
        Args:
            name: The name of the resampling strategy.
        """
        super().__init__(name)
    
    def resample(self, particles: List[Particle[T]]) -> List[Particle[T]]:
        """
        Resample particles using multinomial resampling.
        
        Args:
            particles: The particles to resample.
            
        Returns:
            The resampled particles.
        """
        # Get weights
        weights = [particle.weight for particle in particles]
        
        # Sample indices
        indices = np.random.choice(
            len(particles),
            size=len(particles),
            replace=True,
            p=weights
        )
        
        # Create new particles
        resampled_particles = []
        for index in indices:
            # Create a new particle with the same state but uniform weight
            resampled_particles.append(Particle(
                state=particles[index].state,
                weight=1.0 / len(particles)
            ))
        
        return resampled_particles


@tag("monte_carlo.particle_filter")
class SystematicResampling(ResamplingStrategy[T]):
    """
    Systematic resampling strategy.
    
    This class implements systematic resampling, which samples particles
    using a single random number and systematic spacing.
    
    Attributes:
        name: The name of the resampling strategy.
        metadata: Additional metadata for the resampling strategy.
    
    TODO(Issue #9): Add support for parallel resampling
    TODO(Issue #9): Implement resampling strategy validation
    """
    
    def __init__(self, name: str = "systematic_resampling") -> None:
        """
        Initialize the systematic resampling strategy.
        
        Args:
            name: The name of the resampling strategy.
        """
        super().__init__(name)
    
    def resample(self, particles: List[Particle[T]]) -> List[Particle[T]]:
        """
        Resample particles using systematic resampling.
        
        Args:
            particles: The particles to resample.
            
        Returns:
            The resampled particles.
        """
        # Get weights
        weights = np.array([particle.weight for particle in particles])
        
        # Compute cumulative sum of weights
        cumulative_sum = np.cumsum(weights)
        
        # Generate systematic samples
        num_particles = len(particles)
        u0 = random.random() / num_particles
        u = np.array([u0 + i / num_particles for i in range(num_particles)])
        
        # Find indices of particles to resample
        indices = np.zeros(num_particles, dtype=int)
        j = 0
        for i in range(num_particles):
            while j < num_particles - 1 and u[i] > cumulative_sum[j]:
                j += 1
            indices[i] = j
        
        # Create new particles
        resampled_particles = []
        for index in indices:
            # Create a new particle with the same state but uniform weight
            resampled_particles.append(Particle(
                state=particles[index].state,
                weight=1.0 / num_particles
            ))
        
        return resampled_particles


@tag("monte_carlo.particle_filter")
class StratifiedResampling(ResamplingStrategy[T]):
    """
    Stratified resampling strategy.
    
    This class implements stratified resampling, which samples particles
    using multiple random numbers in stratified intervals.
    
    Attributes:
        name: The name of the resampling strategy.
        metadata: Additional metadata for the resampling strategy.
    
    TODO(Issue #9): Add support for parallel resampling
    TODO(Issue #9): Implement resampling strategy validation
    """
    
    def __init__(self, name: str = "stratified_resampling") -> None:
        """
        Initialize the stratified resampling strategy.
        
        Args:
            name: The name of the resampling strategy.
        """
        super().__init__(name)
    
    def resample(self, particles: List[Particle[T]]) -> List[Particle[T]]:
        """
        Resample particles using stratified resampling.
        
        Args:
            particles: The particles to resample.
            
        Returns:
            The resampled particles.
        """
        # Get weights
        weights = np.array([particle.weight for particle in particles])
        
        # Compute cumulative sum of weights
        cumulative_sum = np.cumsum(weights)
        
        # Generate stratified samples
        num_particles = len(particles)
        u = np.array([
            (i + random.random()) / num_particles for i in range(num_particles)
        ])
        
        # Find indices of particles to resample
        indices = np.zeros(num_particles, dtype=int)
        j = 0
        for i in range(num_particles):
            while j < num_particles - 1 and u[i] > cumulative_sum[j]:
                j += 1
            indices[i] = j
        
        # Create new particles
        resampled_particles = []
        for index in indices:
            # Create a new particle with the same state but uniform weight
            resampled_particles.append(Particle(
                state=particles[index].state,
                weight=1.0 / num_particles
            ))
        
        return resampled_particles


@tag("monte_carlo.particle_filter")
class ResidualResampling(ResamplingStrategy[T]):
    """
    Residual resampling strategy.
    
    This class implements residual resampling, which deterministically
    resamples particles based on the integer part of their expected counts,
    and then randomly resamples the remainder.
    
    Attributes:
        name: The name of the resampling strategy.
        metadata: Additional metadata for the resampling strategy.
    
    TODO(Issue #9): Add support for parallel resampling
    TODO(Issue #9): Implement resampling strategy validation
    """
    
    def __init__(self, name: str = "residual_resampling") -> None:
        """
        Initialize the residual resampling strategy.
        
        Args:
            name: The name of the resampling strategy.
        """
        super().__init__(name)
    
    def resample(self, particles: List[Particle[T]]) -> List[Particle[T]]:
        """
        Resample particles using residual resampling.
        
        Args:
            particles: The particles to resample.
            
        Returns:
            The resampled particles.
        """
        # Get weights
        weights = np.array([particle.weight for particle in particles])
        
        # Compute expected counts
        num_particles = len(particles)
        expected_counts = weights * num_particles
        
        # Compute integer part and residual
        integer_counts = np.floor(expected_counts).astype(int)
        residual_weights = expected_counts - integer_counts
        
        # Normalize residual weights
        residual_sum = np.sum(residual_weights)
        if residual_sum > 0:
            residual_weights = residual_weights / residual_sum
        
        # Compute number of particles to resample
        num_residual = num_particles - np.sum(integer_counts)
        
        # Create new particles
        resampled_particles = []
        
        # Add particles based on integer counts
        for i, count in enumerate(integer_counts):
            for _ in range(count):
                resampled_particles.append(Particle(
                    state=particles[i].state,
                    weight=1.0 / num_particles
                ))
        
        # Resample remaining particles based on residual weights
        if num_residual > 0 and residual_sum > 0:
            residual_indices = np.random.choice(
                len(particles),
                size=num_residual,
                replace=True,
                p=residual_weights
            )
            
            for index in residual_indices:
                resampled_particles.append(Particle(
                    state=particles[index].state,
                    weight=1.0 / num_particles
                ))
        
        return resampled_particles
