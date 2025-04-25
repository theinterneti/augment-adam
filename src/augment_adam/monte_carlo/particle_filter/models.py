"""
Models for particle filtering.

This module provides system and observation models for particle filtering,
including linear and nonlinear models.
"""

import math
import random
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.particle_filter.base import SystemModel, ObservationModel


@tag("monte_carlo.particle_filter")
class LinearSystemModel(SystemModel[np.ndarray]):
    """
    Linear system model for particle filtering.
    
    This class implements a linear system model, which propagates the state
    using a linear state transition matrix and additive Gaussian noise.
    
    Attributes:
        name: The name of the system model.
        metadata: Additional metadata for the system model.
        state_transition_matrix: The state transition matrix.
        process_noise_covariance: The covariance matrix of the process noise.
    
    TODO(Issue #9): Add support for control inputs
    TODO(Issue #9): Implement system model validation
    """
    
    def __init__(
        self,
        state_transition_matrix: np.ndarray,
        process_noise_covariance: np.ndarray,
        name: str = "linear_system_model"
    ) -> None:
        """
        Initialize the linear system model.
        
        Args:
            state_transition_matrix: The state transition matrix.
            process_noise_covariance: The covariance matrix of the process noise.
            name: The name of the system model.
        """
        super().__init__(name)
        
        self.state_transition_matrix = state_transition_matrix
        self.process_noise_covariance = process_noise_covariance
        
        self.metadata["state_transition_matrix"] = state_transition_matrix
        self.metadata["process_noise_covariance"] = process_noise_covariance
    
    def propagate(self, state: np.ndarray, dt: float) -> np.ndarray:
        """
        Propagate the state forward in time.
        
        Args:
            state: The current state.
            dt: The time step.
            
        Returns:
            The propagated state.
        """
        # Compute state transition matrix for the given time step
        F = np.eye(self.state_transition_matrix.shape[0]) + dt * self.state_transition_matrix
        
        # Propagate state
        propagated_state = F @ state
        
        # Add process noise
        noise = np.random.multivariate_normal(
            np.zeros(state.shape),
            dt * self.process_noise_covariance
        )
        
        return propagated_state + noise


@tag("monte_carlo.particle_filter")
class NonlinearSystemModel(SystemModel[np.ndarray]):
    """
    Nonlinear system model for particle filtering.
    
    This class implements a nonlinear system model, which propagates the state
    using a nonlinear state transition function and additive Gaussian noise.
    
    Attributes:
        name: The name of the system model.
        metadata: Additional metadata for the system model.
        state_transition_function: The state transition function.
        process_noise_covariance: The covariance matrix of the process noise.
    
    TODO(Issue #9): Add support for control inputs
    TODO(Issue #9): Implement system model validation
    """
    
    def __init__(
        self,
        state_transition_function: Callable[[np.ndarray, float], np.ndarray],
        process_noise_covariance: np.ndarray,
        name: str = "nonlinear_system_model"
    ) -> None:
        """
        Initialize the nonlinear system model.
        
        Args:
            state_transition_function: The state transition function.
            process_noise_covariance: The covariance matrix of the process noise.
            name: The name of the system model.
        """
        super().__init__(name)
        
        self.state_transition_function = state_transition_function
        self.process_noise_covariance = process_noise_covariance
        
        self.metadata["process_noise_covariance"] = process_noise_covariance
    
    def propagate(self, state: np.ndarray, dt: float) -> np.ndarray:
        """
        Propagate the state forward in time.
        
        Args:
            state: The current state.
            dt: The time step.
            
        Returns:
            The propagated state.
        """
        # Propagate state
        propagated_state = self.state_transition_function(state, dt)
        
        # Add process noise
        noise = np.random.multivariate_normal(
            np.zeros(state.shape),
            dt * self.process_noise_covariance
        )
        
        return propagated_state + noise


@tag("monte_carlo.particle_filter")
class LinearObservationModel(ObservationModel[np.ndarray, np.ndarray]):
    """
    Linear observation model for particle filtering.
    
    This class implements a linear observation model, which generates observations
    using a linear observation matrix and additive Gaussian noise.
    
    Attributes:
        name: The name of the observation model.
        metadata: Additional metadata for the observation model.
        observation_matrix: The observation matrix.
        observation_noise_covariance: The covariance matrix of the observation noise.
    
    TODO(Issue #9): Add support for time-varying observation models
    TODO(Issue #9): Implement observation model validation
    """
    
    def __init__(
        self,
        observation_matrix: np.ndarray,
        observation_noise_covariance: np.ndarray,
        name: str = "linear_observation_model"
    ) -> None:
        """
        Initialize the linear observation model.
        
        Args:
            observation_matrix: The observation matrix.
            observation_noise_covariance: The covariance matrix of the observation noise.
            name: The name of the observation model.
        """
        super().__init__(name)
        
        self.observation_matrix = observation_matrix
        self.observation_noise_covariance = observation_noise_covariance
        
        self.metadata["observation_matrix"] = observation_matrix
        self.metadata["observation_noise_covariance"] = observation_noise_covariance
    
    def likelihood(self, state: np.ndarray, observation: np.ndarray) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            state: The state.
            observation: The observation.
            
        Returns:
            The likelihood of the observation given the state.
        """
        # Compute expected observation
        expected_observation = self.observation_matrix @ state
        
        # Compute innovation
        innovation = observation - expected_observation
        
        # Compute likelihood
        inv_cov = np.linalg.inv(self.observation_noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(observation) * np.linalg.det(self.observation_noise_covariance))
        
        return normalization * math.exp(exponent)


@tag("monte_carlo.particle_filter")
class NonlinearObservationModel(ObservationModel[np.ndarray, np.ndarray]):
    """
    Nonlinear observation model for particle filtering.
    
    This class implements a nonlinear observation model, which generates observations
    using a nonlinear observation function and additive Gaussian noise.
    
    Attributes:
        name: The name of the observation model.
        metadata: Additional metadata for the observation model.
        observation_function: The observation function.
        observation_noise_covariance: The covariance matrix of the observation noise.
    
    TODO(Issue #9): Add support for time-varying observation models
    TODO(Issue #9): Implement observation model validation
    """
    
    def __init__(
        self,
        observation_function: Callable[[np.ndarray], np.ndarray],
        observation_noise_covariance: np.ndarray,
        name: str = "nonlinear_observation_model"
    ) -> None:
        """
        Initialize the nonlinear observation model.
        
        Args:
            observation_function: The observation function.
            observation_noise_covariance: The covariance matrix of the observation noise.
            name: The name of the observation model.
        """
        super().__init__(name)
        
        self.observation_function = observation_function
        self.observation_noise_covariance = observation_noise_covariance
        
        self.metadata["observation_noise_covariance"] = observation_noise_covariance
    
    def likelihood(self, state: np.ndarray, observation: np.ndarray) -> float:
        """
        Compute the likelihood of an observation given a state.
        
        Args:
            state: The state.
            observation: The observation.
            
        Returns:
            The likelihood of the observation given the state.
        """
        # Compute expected observation
        expected_observation = self.observation_function(state)
        
        # Compute innovation
        innovation = observation - expected_observation
        
        # Compute likelihood
        inv_cov = np.linalg.inv(self.observation_noise_covariance)
        exponent = -0.5 * innovation.T @ inv_cov @ innovation
        normalization = 1.0 / math.sqrt((2 * math.pi) ** len(observation) * np.linalg.det(self.observation_noise_covariance))
        
        return normalization * math.exp(exponent)
