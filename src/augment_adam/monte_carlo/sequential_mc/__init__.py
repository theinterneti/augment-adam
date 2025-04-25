"""
Sequential Monte Carlo module.

This module provides sequential Monte Carlo methods for dynamic systems with evolving states.
"""

from augment_adam.monte_carlo.sequential_mc.base import (
    SequentialMonteCarlo,
    SMCState,
    TransitionModel,
    LikelihoodModel,
)

from augment_adam.monte_carlo.sequential_mc.models import (
    LinearTransitionModel,
    NonlinearTransitionModel,
    LinearLikelihoodModel,
    NonlinearLikelihoodModel,
)

__all__ = [
    # Base
    "SequentialMonteCarlo",
    "SMCState",
    "TransitionModel",
    "LikelihoodModel",
    
    # Models
    "LinearTransitionModel",
    "NonlinearTransitionModel",
    "LinearLikelihoodModel",
    "NonlinearLikelihoodModel",
]
