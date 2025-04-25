"""Parallel Sequential Monte Carlo Sampler.

This module implements a parallel version of the Sequential Monte Carlo sampler
for more efficient processing across multiple cores or GPU threads.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import torch

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.smc.particle import Particle
from augment_adam.ai_agent.smc.potential import Potential
from augment_adam.ai_agent.smc.sampler import SequentialMonteCarlo

logger = logging.getLogger(__name__)


class ParallelSequentialMonteCarlo(SequentialMonteCarlo):
    """Parallel Sequential Monte Carlo Sampler.

    This class implements a parallel version of the Sequential Monte Carlo algorithm
    for controlled generation from language models.

    Attributes:
        num_particles: Number of particles
        potentials: List of potential functions
        particles: List of current particles
        ess_threshold: Threshold for effective sample size
        num_workers: Number of parallel workers
        use_gpu: Whether to use GPU for parallelization
        batch_size: Batch size for parallel processing
    """

    def __init__(
        self,
        num_particles: int = 100,
        potentials: Optional[List[Potential]] = None,
        ess_threshold: float = 0.5,
        model: Any = None,
        num_workers: int = None,
        use_gpu: bool = False,
        batch_size: int = 10
    ):
        """Initialize the Parallel Sequential Monte Carlo Sampler.

        Args:
            num_particles: Number of particles
            potentials: List of potential functions
            ess_threshold: Threshold for effective sample size
            model: The language model to use
            num_workers: Number of parallel workers (if None, use CPU count)
            use_gpu: Whether to use GPU for parallelization
            batch_size: Batch size for parallel processing
        """
        super().__init__(
            num_particles=num_particles,
            potentials=potentials,
            ess_threshold=ess_threshold,
            model=model
        )
        
        # Set number of workers
        self.num_workers = num_workers or mp.cpu_count()
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.batch_size = batch_size
        
        # If using GPU, adjust workers based on GPU count
        if self.use_gpu:
            gpu_count = torch.cuda.device_count()
            if gpu_count > 0:
                self.num_workers = min(self.num_workers, gpu_count * 2)
                logger.info(f"Using GPU parallelization with {self.num_workers} workers")
            else:
                self.use_gpu = False
                logger.warning("GPU requested but not available, falling back to CPU")
        
        logger.info(f"Initialized Parallel SMC sampler with {num_particles} particles and {self.num_workers} workers")
    
    def _process_particle_batch(self, particles: List[Particle], model: Any) -> List[Particle]:
        """Process a batch of particles in parallel.
        
        Args:
            particles: List of particles to process
            model: The language model to use
            
        Returns:
            List of extended particles
        """
        new_particles = []
        
        # Generate prompts for all particles
        prompts = [particle.get_sequence_text() for particle in particles]
        
        # Generate candidate tokens for all prompts
        all_candidates = []
        
        # If we're using GPU, we can batch process
        if self.use_gpu and hasattr(model, 'batch_get_token_probabilities'):
            # Batch process all prompts
            batch_candidates = model.batch_get_token_probabilities(
                prompts=prompts,
                temperature=0.8,
                top_k=5
            )
            all_candidates = batch_candidates
        else:
            # Process each prompt individually
            for prompt in prompts:
                candidates = self._generate_candidate_tokens(
                    prompt,
                    model,
                    5,  # num_candidates
                    0.8  # temperature
                )
                all_candidates.append(candidates)
        
        # Create new particles for each candidate token
        for i, particle in enumerate(particles):
            candidates = all_candidates[i]
            for token in candidates:
                new_particle = particle.extend(token)
                new_particles.append(new_particle)
        
        return new_particles
    
    def _parallel_extend_particles(self, model: Any) -> List[Particle]:
        """Extend particles in parallel.
        
        Args:
            model: The language model to use
            
        Returns:
            List of extended particles
        """
        model_to_use = model or self.model
        
        # Split particles into batches
        particle_batches = []
        batch_size = max(1, len(self.particles) // self.num_workers)
        
        for i in range(0, len(self.particles), batch_size):
            batch = self.particles[i:i+batch_size]
            particle_batches.append(batch)
        
        # Process batches in parallel
        new_particles = []
        
        if self.use_gpu:
            # Use thread pool for GPU processing (shared memory)
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures = [
                    executor.submit(self._process_particle_batch, batch, model_to_use)
                    for batch in particle_batches
                ]
                
                for future in futures:
                    new_particles.extend(future.result())
        else:
            # Use process pool for CPU processing
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                futures = [
                    executor.submit(self._process_particle_batch, batch, model_to_use)
                    for batch in particle_batches
                ]
                
                for future in futures:
                    new_particles.extend(future.result())
        
        return new_particles
    
    def extend_particles(self, model: Any = None, num_candidates: int = 5, temperature: float = 0.8) -> None:
        """Extend particles with new tokens in parallel.
        
        Args:
            model: The language model to use (if None, use the model from initialization)
            num_candidates: Number of candidate tokens to consider for each particle
            temperature: Temperature for token sampling
        """
        try:
            # Use parallel extension if we have enough particles
            if len(self.particles) >= self.num_workers * 2:
                new_particles = self._parallel_extend_particles(model)
            else:
                # Fall back to sequential processing for small number of particles
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
        except Exception as e:
            logger.warning(f"Error in parallel particle extension: {e}")
            # Fall back to sequential implementation
            super().extend_particles(model, num_candidates, temperature)
    
    def _parallel_evaluate_potentials(self, particles: List[Particle], potentials: List[Potential]) -> List[float]:
        """Evaluate potentials on particles in parallel.
        
        Args:
            particles: List of particles to evaluate
            potentials: List of potentials to apply
            
        Returns:
            List of weights
        """
        weights = [1.0] * len(particles)
        
        for potential in potentials:
            for i, particle in enumerate(particles):
                weight = potential.evaluate(particle.sequence)
                weights[i] *= weight
        
        return weights
    
    def reweight_particles(self) -> None:
        """Reweight particles using potential functions in parallel."""
        try:
            # Split particles into batches
            particle_batches = []
            batch_size = max(1, len(self.particles) // self.num_workers)
            
            for i in range(0, len(self.particles), batch_size):
                batch = self.particles[i:i+batch_size]
                particle_batches.append(batch)
            
            # Process efficient potentials in parallel
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                futures = [
                    executor.submit(self._parallel_evaluate_potentials, batch, self.efficient_potentials)
                    for batch in particle_batches
                ]
                
                # Collect weights
                all_weights = []
                for future in futures:
                    all_weights.extend(future.result())
                
                # Update particle weights
                for i, weight in enumerate(all_weights):
                    self.particles[i].update_weight(weight)
            
            # Apply expensive potentials sequentially (less frequently)
            for potential in self.expensive_potentials:
                for particle in self.particles:
                    weight = potential.evaluate(particle.sequence)
                    particle.update_weight(weight)
            
            # Normalize weights
            total_weight = sum(p.weight for p in self.particles)
            if total_weight > 0:
                for particle in self.particles:
                    particle.weight /= total_weight
            
            logger.info(f"Reweighted {len(self.particles)} particles in parallel")
        except Exception as e:
            logger.warning(f"Error in parallel reweighting: {e}")
            # Fall back to sequential implementation
            super().reweight_particles()
    
    def sample(
        self,
        prompt: str,
        max_tokens: int = 100,
        model: Any = None,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        num_candidates: int = 5,
        batch_size: int = 10,
        early_stopping: bool = True,
        timeout: Optional[int] = None
    ) -> str:
        """Sample a sequence using parallel SMC.
        
        Args:
            prompt: The prompt to start with
            max_tokens: Maximum number of tokens to generate
            model: The language model to use (if None, use the model from initialization)
            temperature: Sampling temperature (higher = more random)
            stop: List of strings that stop generation when encountered
            num_candidates: Number of candidate tokens to consider for each particle
            batch_size: Number of tokens to generate before reweighting
            early_stopping: Whether to use early stopping
            timeout: Maximum time in seconds for generation (if None, no timeout)
            
        Returns:
            The generated sequence
        """
        start_time = time.time()
        
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
                # Check timeout
                if timeout and time.time() - start_time > timeout:
                    logger.info(f"Stopping generation due to timeout after {i} tokens")
                    break
                
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
                    
                    # Check timeout
                    if timeout and time.time() - start_time > timeout:
                        logger.info(f"Stopping generation due to timeout after {i+j} tokens")
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
            
            generation_time = time.time() - start_time
            tokens_generated = len(result) - len(prompt)
            tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
            
            logger.info(f"Generated {tokens_generated} tokens in {generation_time:.2f}s ({tokens_per_second:.2f} tokens/s)")
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to sample using Parallel SMC",
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
