"""Sequential Monte Carlo Sampler.

This module implements the Sequential Monte Carlo sampler.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import random
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.smc.particle import Particle
from augment_adam.ai_agent.smc.potential import Potential

logger = logging.getLogger(__name__)


class SequentialMonteCarlo:
    """Sequential Monte Carlo Sampler.
    
    This class implements the Sequential Monte Carlo algorithm for
    controlled generation from language models.
    
    Attributes:
        num_particles: Number of particles
        potentials: List of potential functions
        particles: List of current particles
        ess_threshold: Threshold for effective sample size
    """
    
    def __init__(
        self,
        num_particles: int = 100,
        potentials: Optional[List[Potential]] = None,
        ess_threshold: float = 0.5
    ):
        """Initialize the Sequential Monte Carlo Sampler.
        
        Args:
            num_particles: Number of particles
            potentials: List of potential functions
            ess_threshold: Threshold for effective sample size
        """
        self.num_particles = num_particles
        self.potentials = potentials or []
        self.particles = []
        self.ess_threshold = ess_threshold
        
        # Separate efficient and expensive potentials
        self.efficient_potentials = [p for p in self.potentials if p.is_efficient()]
        self.expensive_potentials = [p for p in self.potentials if not p.is_efficient()]
        
        logger.info(f"Initialized SMC sampler with {num_particles} particles")
    
    def update_potentials(self, potentials: List[Potential]) -> None:
        """Update the potential functions.
        
        Args:
            potentials: List of potential functions
        """
        self.potentials = potentials
        
        # Separate efficient and expensive potentials
        self.efficient_potentials = [p for p in self.potentials if p.is_efficient()]
        self.expensive_potentials = [p for p in self.potentials if not p.is_efficient()]
        
        logger.info(f"Updated potentials: {len(self.efficient_potentials)} efficient, {len(self.expensive_potentials)} expensive")
    
    def initialize_particles(self, prompt: str) -> None:
        """Initialize particles with the prompt.
        
        Args:
            prompt: The prompt to initialize with
        """
        # Convert prompt to tokens (character-level for simplicity)
        # In a real implementation, use a proper tokenizer
        tokens = list(prompt)
        
        # Create particles
        self.particles = []
        for _ in range(self.num_particles):
            particle = Particle(sequence=tokens.copy())
            self.particles.append(particle)
        
        logger.info(f"Initialized {len(self.particles)} particles with prompt: {prompt[:20]}...")
    
    def extend_particles(self, model: Any = None) -> None:
        """Extend particles with new tokens.
        
        Args:
            model: The language model to use (if None, use a simple model)
        """
        new_particles = []
        
        for particle in self.particles:
            # Get next token probabilities
            # In a real implementation, use the language model
            # For now, use a simple model that generates random characters
            next_tokens = ["a", "b", "c", "d", "e", " "]
            next_probs = [0.2, 0.2, 0.2, 0.2, 0.1, 0.1]
            
            # Sample next token
            next_token = random.choices(next_tokens, weights=next_probs)[0]
            
            # Extend particle
            new_particle = particle.extend(next_token)
            new_particles.append(new_particle)
        
        self.particles = new_particles
        logger.info(f"Extended {len(self.particles)} particles")
    
    def reweight_particles(self) -> None:
        """Reweight particles using potential functions."""
        # Apply efficient potentials
        for potential in self.efficient_potentials:
            for particle in self.particles:
                weight = potential.evaluate(particle.sequence)
                particle.update_weight(weight)
        
        # Apply expensive potentials (less frequently)
        # In a real implementation, apply these less frequently
        for potential in self.expensive_potentials:
            for particle in self.particles:
                weight = potential.evaluate(particle.sequence)
                particle.update_weight(weight)
        
        # Normalize weights
        total_weight = sum(p.weight for p in self.particles)
        if total_weight > 0:
            for particle in self.particles:
                particle.weight /= total_weight
        
        logger.info(f"Reweighted {len(self.particles)} particles")
    
    def resample_particles(self) -> None:
        """Resample particles based on weights."""
        # Calculate effective sample size
        weights = np.array([p.weight for p in self.particles])
        ess = 1.0 / np.sum(weights ** 2)
        ess_ratio = ess / len(self.particles)
        
        # Resample if ESS is below threshold
        if ess_ratio < self.ess_threshold:
            # Multinomial resampling
            indices = np.random.choice(
                len(self.particles),
                size=len(self.particles),
                replace=True,
                p=weights
            )
            
            # Create new particles
            new_particles = []
            for idx in indices:
                new_particle = Particle(
                    sequence=self.particles[idx].sequence.copy(),
                    weight=1.0 / len(self.particles),
                    log_weight=0.0,
                    metadata=self.particles[idx].metadata.copy()
                )
                new_particles.append(new_particle)
            
            self.particles = new_particles
            logger.info(f"Resampled particles (ESS ratio: {ess_ratio:.4f})")
    
    def sample(
        self,
        prompt: str,
        max_tokens: int = 100,
        model: Any = None
    ) -> str:
        """Sample a sequence using SMC.
        
        Args:
            prompt: The prompt to start with
            max_tokens: Maximum number of tokens to generate
            model: The language model to use
            
        Returns:
            The generated sequence
        """
        try:
            # Initialize particles
            self.initialize_particles(prompt)
            
            # Generate tokens
            for _ in range(max_tokens):
                # Extend particles
                self.extend_particles(model)
                
                # Reweight particles
                self.reweight_particles()
                
                # Resample particles
                self.resample_particles()
                
                # Check for termination
                # In a real implementation, check for end-of-sequence tokens
                if random.random() < 0.1:  # 10% chance of termination
                    break
            
            # Select best particle
            best_particle = max(self.particles, key=lambda p: p.weight)
            
            # Get sequence text
            result = best_particle.get_sequence_text()
            
            logger.info(f"Generated sequence with {len(result) - len(prompt)} new tokens")
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to sample using SMC",
                category=ErrorCategory.RESOURCE,
                details={"prompt_length": len(prompt) if prompt else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to prompt
            return prompt
