"""
Monte Carlo Techniques.

This module provides Monte Carlo techniques for probabilistic modeling,
sampling, and decision-making under uncertainty.

TODO(Issue #9): Add support for parallel Monte Carlo simulations
TODO(Issue #9): Implement adaptive sampling techniques
TODO(Issue #9): Add visualization tools for Monte Carlo results
"""

from augment_adam.monte_carlo.particle_filter import (
    ParticleFilter,
    Particle,
    ResamplingStrategy,
    SystemModel,
    ObservationModel,
)

from augment_adam.monte_carlo.importance_sampling import (
    ImportanceSampler,
    ProposalDistribution,
    TargetDistribution,
    WeightedSample,
)

from augment_adam.monte_carlo.sequential_mc import (
    SequentialMonteCarlo,
    SMCState,
    TransitionModel,
    LikelihoodModel,
)

from augment_adam.monte_carlo.mcts import (
    MonteCarloTreeSearch,
    MCTSNode,
    ActionSelectionStrategy,
    UCB1Strategy,
    RolloutPolicy,
    RandomRolloutPolicy,
)

from augment_adam.monte_carlo.mcmc import (
    MarkovChainMonteCarlo,
    MetropolisHastings,
    GibbsSampler,
    HamiltonianMC,
    MCMCSample,
    ProposalDistribution as MCMCProposalDistribution,
)

from augment_adam.monte_carlo.utils import (
    Distribution,
    GaussianDistribution,
    UniformDistribution,
    DiscreteDistribution,
    sample_from_distribution,
    estimate_statistics,
)

__all__ = [
    # Particle Filter
    "ParticleFilter",
    "Particle",
    "ResamplingStrategy",
    "SystemModel",
    "ObservationModel",
    
    # Importance Sampling
    "ImportanceSampler",
    "ProposalDistribution",
    "TargetDistribution",
    "WeightedSample",
    
    # Sequential Monte Carlo
    "SequentialMonteCarlo",
    "SMCState",
    "TransitionModel",
    "LikelihoodModel",
    
    # Monte Carlo Tree Search
    "MonteCarloTreeSearch",
    "MCTSNode",
    "ActionSelectionStrategy",
    "UCB1Strategy",
    "RolloutPolicy",
    "RandomRolloutPolicy",
    
    # Markov Chain Monte Carlo
    "MarkovChainMonteCarlo",
    "MetropolisHastings",
    "GibbsSampler",
    "HamiltonianMC",
    "MCMCSample",
    "MCMCProposalDistribution",
    
    # Utilities
    "Distribution",
    "GaussianDistribution",
    "UniformDistribution",
    "DiscreteDistribution",
    "sample_from_distribution",
    "estimate_statistics",
]
