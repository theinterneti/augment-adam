"""
Adaptive importance sampling.

This module provides adaptive importance sampling, which adjusts the proposal
distribution based on previous samples.
"""

import math
import random
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.importance_sampling.base import (
    ImportanceSampler, ProposalDistribution, TargetDistribution, WeightedSample
)


T = TypeVar('T')  # Type of sample


@tag("monte_carlo.importance_sampling")
class MixtureProposalDistribution(ProposalDistribution[T]):
    """
    Mixture proposal distribution for adaptive importance sampling.
    
    This class implements a mixture proposal distribution, which combines
    multiple proposal distributions with weights.
    
    Attributes:
        name: The name of the proposal distribution.
        metadata: Additional metadata for the proposal distribution.
        components: The component proposal distributions.
        weights: The weights of the components.
    
    TODO(Issue #9): Add support for more mixture types
    TODO(Issue #9): Implement proposal distribution validation
    """
    
    def __init__(
        self,
        components: List[ProposalDistribution[T]],
        weights: Optional[List[float]] = None,
        name: str = "mixture_proposal_distribution"
    ) -> None:
        """
        Initialize the mixture proposal distribution.
        
        Args:
            components: The component proposal distributions.
            weights: The weights of the components. If None, uniform weights are used.
            name: The name of the proposal distribution.
        """
        super().__init__(name)
        
        self.components = components
        
        if weights is None:
            # Use uniform weights
            self.weights = [1.0 / len(components)] * len(components)
        else:
            # Normalize weights to sum to 1
            total = sum(weights)
            self.weights = [w / total for w in weights]
        
        self.metadata["components"] = [component.name for component in components]
        self.metadata["weights"] = self.weights
    
    def sample(self) -> T:
        """
        Sample from the mixture proposal distribution.
        
        Returns:
            A sample from the distribution.
        """
        # Select a component based on weights
        component_index = random.choices(range(len(self.components)), weights=self.weights, k=1)[0]
        
        # Sample from the selected component
        return self.components[component_index].sample()
    
    def pdf(self, x: T) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        # Compute weighted sum of component PDFs
        return sum(w * component.pdf(x) for w, component in zip(self.weights, self.components))
    
    def update_weights(self, weights: List[float]) -> None:
        """
        Update the weights of the components.
        
        Args:
            weights: The new weights of the components.
        """
        # Normalize weights to sum to 1
        total = sum(weights)
        if total > 0:
            self.weights = [w / total for w in weights]
        else:
            # If all weights are zero, use uniform weights
            self.weights = [1.0 / len(self.components)] * len(self.components)
        
        self.metadata["weights"] = self.weights


@tag("monte_carlo.importance_sampling")
class AdaptiveImportanceSampler(ImportanceSampler[T]):
    """
    Adaptive importance sampler for efficient sampling from complex distributions.
    
    This class implements adaptive importance sampling, which adjusts the proposal
    distribution based on previous samples.
    
    Attributes:
        name: The name of the importance sampler.
        metadata: Additional metadata for the importance sampler.
        proposal_distribution: The proposal distribution.
        target_distribution: The target distribution.
        samples: The weighted samples.
        adaptation_interval: The interval at which to adapt the proposal distribution.
    
    TODO(Issue #9): Add support for more adaptation strategies
    TODO(Issue #9): Implement importance sampler validation
    """
    
    def __init__(
        self,
        proposal_distribution: MixtureProposalDistribution[T],
        target_distribution: TargetDistribution[T],
        adaptation_interval: int = 100,
        name: str = "adaptive_importance_sampler"
    ) -> None:
        """
        Initialize the adaptive importance sampler.
        
        Args:
            proposal_distribution: The proposal distribution.
            target_distribution: The target distribution.
            adaptation_interval: The interval at which to adapt the proposal distribution.
            name: The name of the importance sampler.
        """
        super().__init__(proposal_distribution, target_distribution, name)
        
        self.adaptation_interval = adaptation_interval
        self.metadata["adaptation_interval"] = adaptation_interval
    
    def sample(self, num_samples: int) -> List[WeightedSample[T]]:
        """
        Generate weighted samples with adaptation.
        
        Args:
            num_samples: The number of samples to generate.
            
        Returns:
            The weighted samples.
        """
        samples = []
        
        for i in range(num_samples):
            # Sample from proposal distribution
            x = self.proposal_distribution.sample()
            
            # Compute weight
            proposal_pdf = self.proposal_distribution.pdf(x)
            target_pdf = self.target_distribution.pdf(x)
            
            if proposal_pdf > 0:
                weight = target_pdf / proposal_pdf
            else:
                weight = 0.0
            
            # Create weighted sample
            sample = WeightedSample(x, weight)
            samples.append(sample)
            
            # Adapt proposal distribution
            if (i + 1) % self.adaptation_interval == 0:
                self._adapt_proposal_distribution(samples)
        
        # Store samples
        self.samples = samples
        
        return samples
    
    def _adapt_proposal_distribution(self, samples: List[WeightedSample[T]]) -> None:
        """
        Adapt the proposal distribution based on samples.
        
        Args:
            samples: The samples to use for adaptation.
        """
        if not isinstance(self.proposal_distribution, MixtureProposalDistribution):
            return
        
        # Compute component weights based on samples
        component_weights = [0.0] * len(self.proposal_distribution.components)
        
        for sample in samples:
            # Compute component PDFs
            component_pdfs = [component.pdf(sample.sample) for component in self.proposal_distribution.components]
            
            # Compute component responsibilities
            total_pdf = sum(w * pdf for w, pdf in zip(self.proposal_distribution.weights, component_pdfs))
            
            if total_pdf > 0:
                responsibilities = [w * pdf / total_pdf for w, pdf in zip(self.proposal_distribution.weights, component_pdfs)]
            else:
                responsibilities = [1.0 / len(component_pdfs)] * len(component_pdfs)
            
            # Update component weights
            for i, responsibility in enumerate(responsibilities):
                component_weights[i] += sample.weight * responsibility
        
        # Update proposal distribution weights
        self.proposal_distribution.update_weights(component_weights)
