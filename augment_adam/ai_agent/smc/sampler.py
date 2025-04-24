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
        ess_threshold: float = 0.5,
        model: Any = None
    ):
        """Initialize the Sequential Monte Carlo Sampler.

        Args:
            num_particles: Number of particles
            potentials: List of potential functions
            ess_threshold: Threshold for effective sample size
            model: The language model to use
        """
        self.num_particles = num_particles
        self.potentials = potentials or []
        self.particles = []
        self.ess_threshold = ess_threshold
        self.model = model

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

    def extend_particles(self, model: Any = None, num_candidates: int = 5, temperature: float = 0.8) -> None:
        """Extend particles with new tokens.

        Args:
            model: The language model to use (if None, use the model from initialization)
            num_candidates: Number of candidate tokens to consider for each particle
            temperature: Temperature for token sampling
        """
        new_particles = []
        model_to_use = model or self.model

        for particle in self.particles:
            # Get current text
            current_text = particle.get_sequence_text()

            # Generate candidate tokens
            candidate_tokens = self._generate_candidate_tokens(
                current_text,
                model_to_use,
                num_candidates,
                temperature
            )

            # Create new particles for each candidate token
            for token in candidate_tokens:
                new_particle = particle.extend(token)
                new_particles.append(new_particle)

        # If we have too many particles, sample down to the original number
        if len(new_particles) > self.num_particles:
            # Prioritize particles from high-weight parents
            parent_weights = []
            for i, particle in enumerate(self.particles):
                parent_weights.extend([particle.weight] * num_candidates)

            # Sample particles based on parent weights
            indices = np.random.choice(
                len(new_particles),
                size=self.num_particles,
                replace=False,
                p=np.array(parent_weights) / sum(parent_weights)
            )

            new_particles = [new_particles[i] for i in indices]

        self.particles = new_particles
        logger.info(f"Extended {len(self.particles)} particles with {num_candidates} candidates each")

    def _generate_candidate_tokens(
        self,
        text: str,
        model: Any,
        num_candidates: int,
        temperature: float
    ) -> List[str]:
        """Generate candidate tokens for a given text.

        Args:
            text: The text to generate candidates for
            model: The language model to use
            num_candidates: Number of candidates to generate
            temperature: Temperature for token sampling

        Returns:
            List of candidate tokens
        """
        if not model:
            # No model available, use a simple model that generates random characters
            candidates = ["a", "b", "c", "d", "e", " ", ".", ",", "!", "?", "\n"]
            probabilities = [0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]

            # Sample candidates
            return random.choices(candidates, weights=probabilities, k=num_candidates)

        try:
            # Try to get token probabilities from the model
            if hasattr(model, "get_token_probabilities"):
                # If the model supports token probability API
                token_probs = model.get_token_probabilities(
                    prompt=text,
                    temperature=temperature
                )

                # Sample tokens based on probabilities
                tokens = []
                probs = []

                for token, prob in token_probs[:20]:  # Consider top 20 tokens
                    tokens.append(token)
                    probs.append(prob)

                # Normalize probabilities
                probs = np.array(probs) / sum(probs)

                # Sample candidates
                return np.random.choice(tokens, size=num_candidates, replace=True, p=probs).tolist()
            else:
                # Generate multiple completions and extract first token from each
                candidates = []

                for _ in range(num_candidates):
                    try:
                        continuation = model.generate(
                            prompt=text,
                            max_tokens=1,
                            temperature=temperature
                        )

                        # Extract the first character of the continuation
                        if continuation and len(continuation) > len(text):
                            next_token = continuation[len(text)]
                            candidates.append(next_token)
                        else:
                            # Fallback if model doesn't return a continuation
                            candidates.append(" ")
                    except Exception as e:
                        logger.warning(f"Error generating candidate: {e}")
                        # Add a fallback token
                        candidates.append(" ")

                # If we couldn't generate enough candidates, add some random ones
                while len(candidates) < num_candidates:
                    candidates.append(random.choice(["a", "e", "i", "o", "u", " ", "."]))

                return candidates
        except Exception as e:
            logger.warning(f"Error generating candidates: {e}")
            # Fallback to random characters
            return [random.choice(["a", "e", "i", "o", "u", " ", "."]) for _ in range(num_candidates)]

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
        model: Any = None,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        num_candidates: int = 5,
        batch_size: int = 10,
        early_stopping: bool = True
    ) -> str:
        """Sample a sequence using SMC.

        Args:
            prompt: The prompt to start with
            max_tokens: Maximum number of tokens to generate
            model: The language model to use (if None, use the model from initialization)
            temperature: Sampling temperature (higher = more random)
            stop: List of strings that stop generation when encountered
            num_candidates: Number of candidate tokens to consider for each particle
            batch_size: Number of tokens to generate before reweighting
            early_stopping: Whether to use early stopping

        Returns:
            The generated sequence
        """
        try:
            # Use provided model or the one from initialization
            model_to_use = model or self.model

            # If we have a model but no potentials, use the model directly
            if model_to_use and not self.potentials:
                logger.info("No potentials provided, using model directly")
                return model_to_use.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop
                )

            # Initialize particles
            self.initialize_particles(prompt)

            # Track best particle and its score
            best_particle = None
            best_score = 0.0

            # Track number of tokens without improvement
            tokens_without_improvement = 0

            # Generate tokens in batches
            for i in range(0, max_tokens, batch_size):
                # Determine batch size (might be smaller for the last batch)
                current_batch_size = min(batch_size, max_tokens - i)

                # Generate tokens for the current batch
                for j in range(current_batch_size):
                    # Extend particles
                    self.extend_particles(
                        model=model_to_use,
                        num_candidates=num_candidates,
                        temperature=temperature
                    )

                    # Check for stop sequences after each token
                    if stop:
                        should_stop = False
                        for particle in self.particles:
                            text = particle.get_sequence_text()
                            if any(s in text for s in stop):
                                logger.info(f"Stopping generation at token {i+j} due to stop sequence")
                                should_stop = True
                                break

                        if should_stop:
                            break

                # Reweight particles after the batch
                self.reweight_particles()

                # Resample particles
                self.resample_particles()

                # Get current best particle
                current_best_particle = max(self.particles, key=lambda p: p.weight)
                current_score = current_best_particle.weight

                # Update best particle if improved
                if best_particle is None or current_score > best_score:
                    best_particle = current_best_particle
                    best_score = current_score
                    tokens_without_improvement = 0
                else:
                    tokens_without_improvement += current_batch_size

                # Early stopping if no improvement for a while
                if early_stopping and tokens_without_improvement >= max(20, max_tokens // 5):
                    logger.info(f"Early stopping after {i + current_batch_size} tokens due to no improvement")
                    break

                # Check for natural stopping points in best particle
                text = current_best_particle.get_sequence_text()
                if (text.endswith(".") or text.endswith("!") or text.endswith("?") or
                    text.endswith("\n\n") or text.endswith("</s>") or text.endswith("</answer>")):
                    if random.random() < 0.5:  # 50% chance of termination at natural end
                        logger.info(f"Stopping generation at token {i + current_batch_size} due to natural end")
                        break

            # Use the best particle found during generation
            result = best_particle.get_sequence_text() if best_particle else prompt

            # If result is just the prompt, and we have a model, generate directly
            if result == prompt and model_to_use:
                logger.info("SMC didn't generate any new tokens, using model directly")
                return model_to_use.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop
                )

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

            # If we have a model, try to generate directly as a fallback
            if model or self.model:
                try:
                    model_to_use = model or self.model
                    logger.info("Falling back to direct model generation")
                    return model_to_use.generate(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop=stop
                    )
                except Exception as e2:
                    logger.error(f"Fallback generation also failed: {e2}")

            # Fall back to prompt
            return prompt
