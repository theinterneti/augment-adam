"""Sequential Monte Carlo (SMC) for the AI Agent.

This module provides components for controlled generation using
Sequential Monte Carlo.

Version: 0.1.0
Created: 2025-04-27
"""

from augment_adam.ai_agent.smc.particle import Particle
from augment_adam.ai_agent.smc.potential import Potential, GrammarPotential, SemanticPotential
from augment_adam.ai_agent.smc.sampler import SequentialMonteCarlo

__all__ = [
    "Particle",
    "Potential",
    "GrammarPotential",
    "SemanticPotential",
    "SequentialMonteCarlo",
]
