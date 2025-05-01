"""Particle for Sequential Monte Carlo.

This module defines the Particle class for SMC.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class Particle:
    """Particle for Sequential Monte Carlo.
    
    A particle represents a partial sequence in SMC.
    
    Attributes:
        sequence: The token sequence
        weight: The particle weight
        log_weight: The log of the particle weight
        metadata: Additional metadata for the particle
    """
    
    def __init__(
        self,
        sequence: List[str] = None,
        weight: float = 1.0,
        log_weight: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        """Initialize a Particle.
        
        Args:
            sequence: The token sequence
            weight: The particle weight
            log_weight: The log of the particle weight
            metadata: Additional metadata for the particle
        """
        self.sequence = sequence or []
        self.weight = weight
        self.log_weight = log_weight
        self.metadata = metadata or {}
    
    def extend(self, token: str) -> "Particle":
        """Extend the particle with a new token.
        
        Args:
            token: The token to add
            
        Returns:
            A new particle with the extended sequence
        """
        new_sequence = self.sequence.copy()
        new_sequence.append(token)
        
        return Particle(
            sequence=new_sequence,
            weight=self.weight,
            log_weight=self.log_weight,
            metadata=self.metadata.copy()
        )
    
    def update_weight(self, weight_factor: float) -> None:
        """Update the particle weight.
        
        Args:
            weight_factor: The factor to multiply the weight by
        """
        self.weight *= weight_factor
        self.log_weight += weight_factor
    
    def get_sequence_text(self) -> str:
        """Get the sequence as text.
        
        Returns:
            The sequence as text
        """
        return "".join(self.sequence)
    
    def __str__(self) -> str:
        """Get a string representation of the particle.
        
        Returns:
            A string representation
        """
        return f"Particle(sequence='{self.get_sequence_text()[:20]}...', weight={self.weight:.4f})"
    
    def __repr__(self) -> str:
        """Get a string representation of the particle.
        
        Returns:
            A string representation
        """
        return self.__str__()
