"""
Statistical utilities for Monte Carlo techniques.

This module provides statistical utilities for Monte Carlo techniques,
including estimation of statistics, effective sample size, and autocorrelation.
"""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory


def estimate_statistics(
    samples: List[Union[float, np.ndarray]],
    weights: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Estimate statistics from samples.
    
    Args:
        samples: The samples to estimate statistics from.
        weights: The weights of the samples. If None, uniform weights are used.
        
    Returns:
        Dictionary of estimated statistics, including mean, variance, and standard deviation.
    """
    if not samples:
        return {
            "mean": None,
            "variance": None,
            "std_dev": None,
            "min": None,
            "max": None,
            "median": None,
            "quantiles": None
        }
    
    # Convert samples to numpy array
    samples_array = np.array(samples)
    
    # If weights are provided, normalize them
    if weights is not None:
        weights_array = np.array(weights)
        weights_array = weights_array / np.sum(weights_array)
    else:
        weights_array = np.ones(len(samples)) / len(samples)
    
    # Compute statistics
    mean = np.sum(samples_array * weights_array.reshape(-1, 1) if samples_array.ndim > 1 else samples_array * weights_array)
    
    # Compute variance
    if samples_array.ndim > 1:
        variance = np.sum(weights_array.reshape(-1, 1) * (samples_array - mean) ** 2, axis=0)
    else:
        variance = np.sum(weights_array * (samples_array - mean) ** 2)
    
    # Compute standard deviation
    std_dev = np.sqrt(variance)
    
    # Compute min and max
    min_value = np.min(samples_array, axis=0)
    max_value = np.max(samples_array, axis=0)
    
    # Compute median and quantiles
    sorted_indices = np.argsort(samples_array, axis=0)
    cumulative_weights = np.cumsum(weights_array[sorted_indices])
    
    median_index = np.searchsorted(cumulative_weights, 0.5)
    median = samples_array[sorted_indices[median_index]]
    
    quantiles = {
        "0.025": samples_array[sorted_indices[np.searchsorted(cumulative_weights, 0.025)]],
        "0.25": samples_array[sorted_indices[np.searchsorted(cumulative_weights, 0.25)]],
        "0.5": median,
        "0.75": samples_array[sorted_indices[np.searchsorted(cumulative_weights, 0.75)]],
        "0.975": samples_array[sorted_indices[np.searchsorted(cumulative_weights, 0.975)]]
    }
    
    return {
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "min": min_value,
        "max": max_value,
        "median": median,
        "quantiles": quantiles
    }


def compute_effective_sample_size(weights: List[float]) -> float:
    """
    Compute the effective sample size from weights.
    
    Args:
        weights: The weights of the samples.
        
    Returns:
        The effective sample size.
    """
    if not weights:
        return 0.0
    
    # Normalize weights
    weights_array = np.array(weights)
    weights_array = weights_array / np.sum(weights_array)
    
    # Compute effective sample size
    return 1.0 / np.sum(weights_array ** 2)


def compute_autocorrelation(
    samples: List[Union[float, np.ndarray]],
    max_lag: int = 50
) -> np.ndarray:
    """
    Compute the autocorrelation of samples.
    
    Args:
        samples: The samples to compute autocorrelation from.
        max_lag: The maximum lag to compute autocorrelation for.
        
    Returns:
        Array of autocorrelation values for lags from 0 to max_lag.
    """
    if not samples:
        return np.array([])
    
    # Convert samples to numpy array
    samples_array = np.array(samples)
    
    # Compute mean and variance
    mean = np.mean(samples_array, axis=0)
    variance = np.var(samples_array, axis=0)
    
    # If variance is zero, return zeros
    if np.all(variance == 0):
        return np.zeros(max_lag + 1)
    
    # Compute autocorrelation
    autocorr = np.zeros(max_lag + 1)
    for lag in range(max_lag + 1):
        if samples_array.ndim > 1:
            autocorr[lag] = np.mean(np.sum(
                (samples_array[:-lag] - mean) * (samples_array[lag:] - mean),
                axis=1
            )) / np.sum(variance)
        else:
            autocorr[lag] = np.mean(
                (samples_array[:-lag] - mean) * (samples_array[lag:] - mean)
            ) / variance
    
    return autocorr


def compute_credible_interval(
    samples: List[Union[float, np.ndarray]],
    weights: Optional[List[float]] = None,
    alpha: float = 0.05
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Compute the credible interval from samples.
    
    Args:
        samples: The samples to compute the credible interval from.
        weights: The weights of the samples. If None, uniform weights are used.
        alpha: The significance level (e.g., 0.05 for 95% credible interval).
        
    Returns:
        Tuple of (lower_bound, upper_bound) of the credible interval.
    """
    if not samples:
        return (None, None)
    
    # Convert samples to numpy array
    samples_array = np.array(samples)
    
    # If weights are provided, normalize them
    if weights is not None:
        weights_array = np.array(weights)
        weights_array = weights_array / np.sum(weights_array)
    else:
        weights_array = np.ones(len(samples)) / len(samples)
    
    # Sort samples and weights
    sorted_indices = np.argsort(samples_array, axis=0)
    sorted_samples = samples_array[sorted_indices]
    sorted_weights = weights_array[sorted_indices]
    
    # Compute cumulative weights
    cumulative_weights = np.cumsum(sorted_weights)
    
    # Compute lower and upper bounds
    lower_index = np.searchsorted(cumulative_weights, alpha / 2)
    upper_index = np.searchsorted(cumulative_weights, 1 - alpha / 2)
    
    lower_bound = sorted_samples[lower_index]
    upper_bound = sorted_samples[upper_index]
    
    return (lower_bound, upper_bound)
