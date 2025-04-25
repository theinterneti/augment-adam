"""
Markov Chain Monte Carlo module.

This module provides Markov Chain Monte Carlo (MCMC) methods for sampling from complex distributions.
"""

from augment_adam.monte_carlo.mcmc.base import (
    MarkovChainMonteCarlo,
    MCMCSample,
    ProposalDistribution,
)

from augment_adam.monte_carlo.mcmc.samplers import (
    MetropolisHastings,
    GibbsSampler,
    HamiltonianMC,
)

from augment_adam.monte_carlo.mcmc.proposals import (
    GaussianProposal,
    UniformProposal,
    AdaptiveProposal,
)

__all__ = [
    # Base
    "MarkovChainMonteCarlo",
    "MCMCSample",
    "ProposalDistribution",
    
    # Samplers
    "MetropolisHastings",
    "GibbsSampler",
    "HamiltonianMC",
    
    # Proposals
    "GaussianProposal",
    "UniformProposal",
    "AdaptiveProposal",
]
