"""
Proposal distributions for Markov Chain Monte Carlo.

This module provides proposal distributions for Markov Chain Monte Carlo,
including Gaussian, uniform, and adaptive proposals.
"""

import math
import random
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.mcmc.base import ProposalDistribution


T = TypeVar('T')  # Type of sample


@tag("monte_carlo.mcmc")
class GaussianProposal(ProposalDistribution[np.ndarray]):
    """
    Gaussian proposal distribution for Markov Chain Monte Carlo.
    
    This class implements a Gaussian proposal distribution, which proposes
    new samples by adding Gaussian noise to the current sample.
    
    Attributes:
        name: The name of the proposal distribution.
        metadata: Additional metadata for the proposal distribution.
        scale: The scale of the Gaussian noise.
    
    TODO(Issue #9): Add support for full covariance matrix
    TODO(Issue #9): Implement proposal distribution validation
    """
    
    def __init__(
        self,
        scale: Union[float, np.ndarray],
        name: str = "gaussian_proposal"
    ) -> None:
        """
        Initialize the Gaussian proposal distribution.
        
        Args:
            scale: The scale of the Gaussian noise.
            name: The name of the proposal distribution.
        """
        super().__init__(name)
        
        self.scale = scale
        self.metadata["scale"] = scale
    
    def propose(self, current: np.ndarray) -> np.ndarray:
        """
        Propose a new sample by adding Gaussian noise.
        
        Args:
            current: The current sample.
            
        Returns:
            The proposed sample.
        """
        return current + np.random.normal(0, self.scale, size=current.shape)
    
    def log_probability(self, proposed: np.ndarray, current: np.ndarray) -> float:
        """
        Compute the log probability of proposing a sample.
        
        Args:
            proposed: The proposed sample.
            current: The current sample.
            
        Returns:
            The log probability of proposing the sample.
        """
        # Compute the log probability of the Gaussian distribution
        diff = proposed - current
        
        if isinstance(self.scale, float):
            return -0.5 * np.sum(diff ** 2) / (self.scale ** 2) - 0.5 * len(diff) * math.log(2 * math.pi * self.scale ** 2)
        else:
            return -0.5 * np.sum((diff / self.scale) ** 2) - 0.5 * len(diff) * math.log(2 * math.pi) - np.sum(np.log(self.scale))


@tag("monte_carlo.mcmc")
class UniformProposal(ProposalDistribution[np.ndarray]):
    """
    Uniform proposal distribution for Markov Chain Monte Carlo.
    
    This class implements a uniform proposal distribution, which proposes
    new samples by adding uniform noise to the current sample.
    
    Attributes:
        name: The name of the proposal distribution.
        metadata: Additional metadata for the proposal distribution.
        width: The width of the uniform noise.
    
    TODO(Issue #9): Add support for different widths per dimension
    TODO(Issue #9): Implement proposal distribution validation
    """
    
    def __init__(
        self,
        width: float,
        name: str = "uniform_proposal"
    ) -> None:
        """
        Initialize the uniform proposal distribution.
        
        Args:
            width: The width of the uniform noise.
            name: The name of the proposal distribution.
        """
        super().__init__(name)
        
        self.width = width
        self.metadata["width"] = width
    
    def propose(self, current: np.ndarray) -> np.ndarray:
        """
        Propose a new sample by adding uniform noise.
        
        Args:
            current: The current sample.
            
        Returns:
            The proposed sample.
        """
        return current + np.random.uniform(-self.width / 2, self.width / 2, size=current.shape)
    
    def log_probability(self, proposed: np.ndarray, current: np.ndarray) -> float:
        """
        Compute the log probability of proposing a sample.
        
        Args:
            proposed: The proposed sample.
            current: The current sample.
            
        Returns:
            The log probability of proposing the sample.
        """
        # Compute the log probability of the uniform distribution
        diff = proposed - current
        
        if np.all(np.abs(diff) <= self.width / 2):
            return -len(diff) * math.log(self.width)
        else:
            return float('-inf')


@tag("monte_carlo.mcmc")
class AdaptiveProposal(ProposalDistribution[np.ndarray]):
    """
    Adaptive proposal distribution for Markov Chain Monte Carlo.
    
    This class implements an adaptive proposal distribution, which adjusts
    the proposal distribution based on the acceptance rate.
    
    Attributes:
        name: The name of the proposal distribution.
        metadata: Additional metadata for the proposal distribution.
        scale: The scale of the Gaussian noise.
        target_acceptance: The target acceptance rate.
        adaptation_rate: The rate at which to adapt the scale.
    
    TODO(Issue #9): Add support for full covariance matrix
    TODO(Issue #9): Implement proposal distribution validation
    """
    
    def __init__(
        self,
        initial_scale: Union[float, np.ndarray],
        target_acceptance: float = 0.234,
        adaptation_rate: float = 0.01,
        name: str = "adaptive_proposal"
    ) -> None:
        """
        Initialize the adaptive proposal distribution.
        
        Args:
            initial_scale: The initial scale of the Gaussian noise.
            target_acceptance: The target acceptance rate.
            adaptation_rate: The rate at which to adapt the scale.
            name: The name of the proposal distribution.
        """
        super().__init__(name)
        
        self.scale = initial_scale
        self.target_acceptance = target_acceptance
        self.adaptation_rate = adaptation_rate
        self.acceptance_count = 0
        self.proposal_count = 0
        
        self.metadata["initial_scale"] = initial_scale
        self.metadata["target_acceptance"] = target_acceptance
        self.metadata["adaptation_rate"] = adaptation_rate
    
    def propose(self, current: np.ndarray) -> np.ndarray:
        """
        Propose a new sample by adding Gaussian noise.
        
        Args:
            current: The current sample.
            
        Returns:
            The proposed sample.
        """
        self.proposal_count += 1
        return current + np.random.normal(0, self.scale, size=current.shape)
    
    def log_probability(self, proposed: np.ndarray, current: np.ndarray) -> float:
        """
        Compute the log probability of proposing a sample.
        
        Args:
            proposed: The proposed sample.
            current: The current sample.
            
        Returns:
            The log probability of proposing the sample.
        """
        # Compute the log probability of the Gaussian distribution
        diff = proposed - current
        
        if isinstance(self.scale, float):
            return -0.5 * np.sum(diff ** 2) / (self.scale ** 2) - 0.5 * len(diff) * math.log(2 * math.pi * self.scale ** 2)
        else:
            return -0.5 * np.sum((diff / self.scale) ** 2) - 0.5 * len(diff) * math.log(2 * math.pi) - np.sum(np.log(self.scale))
    
    def update(self, accepted: bool) -> None:
        """
        Update the proposal distribution based on acceptance.
        
        Args:
            accepted: Whether the proposal was accepted.
        """
        if accepted:
            self.acceptance_count += 1
        
        # Adapt the scale
        if self.proposal_count > 0:
            acceptance_rate = self.acceptance_count / self.proposal_count
            log_scale_adjustment = self.adaptation_rate * (acceptance_rate - self.target_acceptance)
            
            if isinstance(self.scale, float):
                self.scale *= math.exp(log_scale_adjustment)
            else:
                self.scale *= math.exp(log_scale_adjustment)
    
    def get_acceptance_rate(self) -> float:
        """
        Get the current acceptance rate.
        
        Returns:
            The acceptance rate.
        """
        if self.proposal_count > 0:
            return self.acceptance_count / self.proposal_count
        else:
            return 0.0
