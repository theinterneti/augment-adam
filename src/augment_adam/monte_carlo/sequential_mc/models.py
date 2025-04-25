"""
Models for sequential Monte Carlo.

This module provides transition and likelihood models for sequential Monte Carlo,
including linear and nonlinear models.
"""

import math
import random
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.sequential_mc.base import TransitionModel, LikelihoodModel


@tag("monte_carlo.sequential_mc")
class LinearTransitionModel(TransitionModel[np.ndarray]):
    """
    Linear transition model for sequential Monte Carlo.
    
    This class implements a linear transition model, which propagates the state
    using a linear state transition matrix and additive Gaussian noise.
    
    Attributes:
        name: The name of the transition model.
        metadata: Additional metadata for the transition model.
        transition_matrix: The state transition matrix.
        noise_covariance: The covariance matrix of the noise.
    
    TODO(Issue #9): Add support for control inputs
    TODO(Issue #9): Implement transition model validation
    """
    
    def __init__(
        self,
        transition_matrix: np.ndarray,
        noise_covariance: np.ndarray,
        name: str = "linear_transition_model"
    ) -> None:
        """
        Initialize the linear transition model.
        
        Args:
            transition_matrix: The state transition matrix.
            noise_covariance: The covariance matrix of the noise.
            name: The name of the transition model.
        """
        super().__init__(name)
        
        self.transition_matrix = transition_matrix
        self.noise_covariance = noise_covariance
        
        self.metadata["transition_matrix"] = transition_matrix
        self.metadata["noise_covariance"] = noise_covariance
    
    def sample(self, state: np.ndarray) -> np.ndarray:
        """
        Sample the next state given the current state.
        
        Args:
            state: The current state.
            
        Returns:
            The next state.
        """
        # Propagate state
        next_state = self.transition_matrix @ state
        
        # Add noise
        noise = np.random.multivariate_normal(
            np.zeros(state.shape),
            self.noise_covariance
        )
        
        return next_state + noise
    
    def pdf(self, next_state: np.ndarray, current_state: np.ndarray) -> float:
        """
        Compute the probability density function (PDF) of the next state given the current state.
        
        Args:
            next_state: The next state.
            current_state: The current state.
            
        Returns:
            The PDF value.
        """
        # Compute expected next state
        expected_next_state = self.transition_matrix @ current_state
        
        # Compute innovation
        innovation = next_state - expected_next_state
        
        # Compute PDF
        inv_cov = np.linalg.inv(self.noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(next_state) * np.linalg.det(self.noise_covariance))
        
        return normalization * math.exp(exponent)


@tag("monte_carlo.sequential_mc")
class NonlinearTransitionModel(TransitionModel[np.ndarray]):
    """
    Nonlinear transition model for sequential Monte Carlo.
    
    This class implements a nonlinear transition model, which propagates the state
    using a nonlinear transition function and additive Gaussian noise.
    
    Attributes:
        name: The name of the transition model.
        metadata: Additional metadata for the transition model.
        transition_function: The state transition function.
        noise_covariance: The covariance matrix of the noise.
    
    TODO(Issue #9): Add support for control inputs
    TODO(Issue #9): Implement transition model validation
    """
    
    def __init__(
        self,
        transition_function: Callable[[np.ndarray], np.ndarray],
        noise_covariance: np.ndarray,
        name: str = "nonlinear_transition_model"
    ) -> None:
        """
        Initialize the nonlinear transition model.
        
        Args:
            transition_function: The state transition function.
            noise_covariance: The covariance matrix of the noise.
            name: The name of the transition model.
        """
        super().__init__(name)
        
        self.transition_function = transition_function
        self.noise_covariance = noise_covariance
        
        self.metadata["noise_covariance"] = noise_covariance
    
    def sample(self, state: np.ndarray) -> np.ndarray:
        """
        Sample the next state given the current state.
        
        Args:
            state: The current state.
            
        Returns:
            The next state.
        """
        # Propagate state
        next_state = self.transition_function(state)
        
        # Add noise
        noise = np.random.multivariate_normal(
            np.zeros(state.shape),
            self.noise_covariance
        )
        
        return next_state + noise
    
    def pdf(self, next_state: np.ndarray, current_state: np.ndarray) -> float:
        """
        Compute the probability density function (PDF) of the next state given the current state.
        
        Args:
            next_state: The next state.
            current_state: The current state.
            
        Returns:
            The PDF value.
        """
        # Compute expected next state
        expected_next_state = self.transition_function(current_state)
        
        # Compute innovation
        innovation = next_state - expected_next_state
        
        # Compute PDF
        inv_cov = np.linalg.inv(self.noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(next_state) * np.linalg.det(self.noise_covariance))
        
        return normalization * math.exp(exponent)


@tag("monte_carlo.sequential_mc")
class LinearLikelihoodModel(LikelihoodModel[np.ndarray, np.ndarray]):
    """
    Linear likelihood model for sequential Monte Carlo.
    
    This class implements a linear likelihood model, which computes the likelihood
    of observations using a linear observation matrix and additive Gaussian noise.
    
    Attributes:
        name: The name of the likelihood model.
        metadata: Additional metadata for the likelihood model.
        observation_matrix: The observation matrix.
        noise_covariance: The covariance matrix of the noise.
    
    TODO(Issue #9): Add support for time-varying likelihood models
    TODO(Issue #9): Implement likelihood model validation
    """
    
    def __init__(
        self,
        observation_matrix: np.ndarray,
        noise_covariance: np.ndarray,
        name: str = "linear_likelihood_model"
    ) -> None:
        """
        Initialize the linear likelihood model.
        
        Args:
            observation_matrix: The observation matrix.
            noise_covariance: The covariance matrix of the noise.
            name: The name of the likelihood model.
        """
        super().__init__(name)
        
        self.observation_matrix = observation_matrix
        self.noise_covariance = noise_covariance
        
        self.metadata["observation_matrix"] = observation_matrix
        self.metadata["noise_covariance"] = noise_covariance
    
    def likelihood(self, observation: np.ndarray, state: np.ndarray) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            observation: The observation.
            state: The state.
            
        Returns:
            The likelihood value.
        """
        # Compute expected observation
        expected_observation = self.observation_matrix @ state
        
        # Compute innovation
        innovation = observation - expected_observation
        
        # Compute likelihood
        inv_cov = np.linalg.inv(self.noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(observation) * np.linalg.det(self.noise_covariance))
        
        return normalization * math.exp(exponent)


@tag("monte_carlo.sequential_mc")
class NonlinearLikelihoodModel(LikelihoodModel[np.ndarray, np.ndarray]):
    """
    Nonlinear likelihood model for sequential Monte Carlo.
    
    This class implements a nonlinear likelihood model, which computes the likelihood
    of observations using a nonlinear observation function and additive Gaussian noise.
    
    Attributes:
        name: The name of the likelihood model.
        metadata: Additional metadata for the likelihood model.
        observation_function: The observation function.
        noise_covariance: The covariance matrix of the noise.
    
    TODO(Issue #9): Add support for time-varying likelihood models
    TODO(Issue #9): Implement likelihood model validation
    """
    
    def __init__(
        self,
        observation_function: Callable[[np.ndarray], np.ndarray],
        noise_covariance: np.ndarray,
        name: str = "nonlinear_likelihood_model"
    ) -> None:
        """
        Initialize the nonlinear likelihood model.
        
        Args:
            observation_function: The observation function.
            noise_covariance: The covariance matrix of the noise.
            name: The name of the likelihood model.
        """
        super().__init__(name)
        
        self.observation_function = observation_function
        self.noise_covariance = noise_covariance
        
        self.metadata["noise_covariance"] = noise_covariance
    
    def likelihood(self, observation: np.ndarray, state: np.ndarray) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            observation: The observation.
            state: The state.
            
        Returns:
            The likelihood value.
        """
        # Compute expected observation
        expected_observation = self.observation_function(state)
        
        # Compute innovation
        innovation = observation - expected_observation
        
        # Compute likelihood
        inv_cov = np.linalg.inv(self.noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(observation) * np.linalg.det(self.noise_covariance))
        
        return normalization * math.exp(exponent)
