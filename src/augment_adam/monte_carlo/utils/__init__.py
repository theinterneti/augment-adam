"""
Utility functions and classes for Monte Carlo techniques.

This module provides utility functions and classes for Monte Carlo techniques,
including distributions, sampling, and statistical estimation.
"""

from augment_adam.monte_carlo.utils.distributions import (
    Distribution,
    GaussianDistribution,
    UniformDistribution,
    DiscreteDistribution,
    sample_from_distribution,
)

from augment_adam.monte_carlo.utils.statistics import (
    estimate_statistics,
    compute_effective_sample_size,
    compute_autocorrelation,
    compute_credible_interval,
)

__all__ = [
    # Distributions
    "Distribution",
    "GaussianDistribution",
    "UniformDistribution",
    "DiscreteDistribution",
    "sample_from_distribution",
    
    # Statistics
    "estimate_statistics",
    "compute_effective_sample_size",
    "compute_autocorrelation",
    "compute_credible_interval",
]
