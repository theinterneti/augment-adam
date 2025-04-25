"""
Importance Sampling module.

This module provides importance sampling for efficient sampling from complex distributions.
"""

from augment_adam.monte_carlo.importance_sampling.base import (
    ImportanceSampler,
    ProposalDistribution,
    TargetDistribution,
    WeightedSample,
)

from augment_adam.monte_carlo.importance_sampling.adaptive import (
    AdaptiveImportanceSampler,
    MixtureProposalDistribution,
)

__all__ = [
    # Base
    "ImportanceSampler",
    "ProposalDistribution",
    "TargetDistribution",
    "WeightedSample",
    
    # Adaptive
    "AdaptiveImportanceSampler",
    "MixtureProposalDistribution",
]
