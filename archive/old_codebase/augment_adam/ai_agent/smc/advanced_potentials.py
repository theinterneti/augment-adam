"""Advanced Potential Functions for SMC.

This module implements advanced potential functions for the Sequential Monte Carlo sampler.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import numpy as np

from augment_adam.ai_agent.smc.potential import Potential

logger = logging.getLogger(__name__)


class CoherencePotential(Potential):
    """Coherence Potential.
    
    This potential evaluates the coherence of a sequence by checking
    if it maintains a consistent topic or theme.
    
    Attributes:
        embedding_fn: Function to get embeddings
        reference_embedding: Reference embedding to compare against
        threshold: Similarity threshold
    """
    
    def __init__(
        self,
        embedding_fn: Callable[[str], List[float]],
        reference_text: str = None,
        reference_embedding: List[float] = None,
        threshold: float = 0.7,
        name: str = "coherence_potential"
    ):
        """Initialize the Coherence Potential.
        
        Args:
            embedding_fn: Function to get embeddings
            reference_text: Reference text to compare against
            reference_embedding: Reference embedding to compare against
            threshold: Similarity threshold
            name: Name of the potential
        """
        super().__init__(name=name)
        self.embedding_fn = embedding_fn
        self.threshold = threshold
        
        # Set reference embedding
        if reference_embedding is not None:
            self.reference_embedding = reference_embedding
        elif reference_text is not None:
            self.reference_embedding = embedding_fn(reference_text)
        else:
            self.reference_embedding = None
            logger.warning("No reference text or embedding provided for CoherencePotential")
    
    def evaluate(self, sequence: List[str]) -> float:
        """Evaluate the potential on a sequence.
        
        Args:
            sequence: The sequence to evaluate
            
        Returns:
            The potential value (between 0 and 1)
        """
        if self.reference_embedding is None:
            return 1.0
        
        # Get sequence text
        text = "".join(sequence)
        
        # Get embedding
        try:
            embedding = self.embedding_fn(text)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(embedding, self.reference_embedding)
            
            # Apply threshold
            if similarity >= self.threshold:
                return 1.0
            else:
                # Scale between 0 and 1
                return max(0.0, similarity / self.threshold)
        except Exception as e:
            logger.warning(f"Error in CoherencePotential: {e}")
            return 1.0
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity
        """
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def is_efficient(self) -> bool:
        """Check if the potential is efficient.
        
        Returns:
            False (embedding calculation is expensive)
        """
        return False


class FactualPotential(Potential):
    """Factual Potential.
    
    This potential evaluates the factual accuracy of a sequence by checking
    if it contains specific facts or information.
    
    Attributes:
        facts: List of facts to check
        threshold: Minimum number of facts required
    """
    
    def __init__(
        self,
        facts: List[str],
        threshold: int = 1,
        name: str = "factual_potential"
    ):
        """Initialize the Factual Potential.
        
        Args:
            facts: List of facts to check
            threshold: Minimum number of facts required
            name: Name of the potential
        """
        super().__init__(name=name)
        self.facts = facts
        self.threshold = threshold
    
    def evaluate(self, sequence: List[str]) -> float:
        """Evaluate the potential on a sequence.
        
        Args:
            sequence: The sequence to evaluate
            
        Returns:
            The potential value (between 0 and 1)
        """
        # Get sequence text
        text = "".join(sequence)
        
        # Count facts
        fact_count = sum(1 for fact in self.facts if fact.lower() in text.lower())
        
        # Apply threshold
        if fact_count >= self.threshold:
            return 1.0
        elif fact_count == 0:
            return 0.1  # Small non-zero value to avoid complete rejection
        else:
            # Scale between 0.1 and 1.0
            return 0.1 + 0.9 * (fact_count / self.threshold)
    
    def is_efficient(self) -> bool:
        """Check if the potential is efficient.
        
        Returns:
            True (string matching is efficient)
        """
        return True


class StylePotential(Potential):
    """Style Potential.
    
    This potential evaluates the style of a sequence by checking
    if it matches a specific writing style.
    
    Attributes:
        style_patterns: Dictionary of style patterns and their weights
    """
    
    def __init__(
        self,
        style_patterns: Dict[str, float],
        name: str = "style_potential"
    ):
        """Initialize the Style Potential.
        
        Args:
            style_patterns: Dictionary of style patterns and their weights
            name: Name of the potential
        """
        super().__init__(name=name)
        self.style_patterns = {re.compile(pattern): weight for pattern, weight in style_patterns.items()}
    
    def evaluate(self, sequence: List[str]) -> float:
        """Evaluate the potential on a sequence.
        
        Args:
            sequence: The sequence to evaluate
            
        Returns:
            The potential value (between 0 and 1)
        """
        # Get sequence text
        text = "".join(sequence)
        
        # Calculate style score
        total_weight = sum(weight for _, weight in self.style_patterns.items())
        score = 0.0
        
        for pattern, weight in self.style_patterns.items():
            if pattern.search(text):
                score += weight
        
        # Normalize score
        if total_weight > 0:
            score /= total_weight
        
        return score
    
    def is_efficient(self) -> bool:
        """Check if the potential is efficient.
        
        Returns:
            True (regex matching is relatively efficient)
        """
        return True


class ConstraintPotential(Potential):
    """Constraint Potential.
    
    This potential enforces constraints on the sequence, such as
    length limits, required elements, or forbidden content.
    
    Attributes:
        constraints: List of constraint functions
    """
    
    def __init__(
        self,
        constraints: List[Callable[[str], float]],
        name: str = "constraint_potential"
    ):
        """Initialize the Constraint Potential.
        
        Args:
            constraints: List of constraint functions
            name: Name of the potential
        """
        super().__init__(name=name)
        self.constraints = constraints
    
    def evaluate(self, sequence: List[str]) -> float:
        """Evaluate the potential on a sequence.
        
        Args:
            sequence: The sequence to evaluate
            
        Returns:
            The potential value (between 0 and 1)
        """
        # Get sequence text
        text = "".join(sequence)
        
        # Apply constraints
        scores = [constraint(text) for constraint in self.constraints]
        
        # Return minimum score (weakest constraint)
        return min(scores) if scores else 1.0
    
    def is_efficient(self) -> bool:
        """Check if the potential is efficient.
        
        Returns:
            True (constraint checking is usually efficient)
        """
        return True


class ContextAwarePotential(Potential):
    """Context-Aware Potential.
    
    This potential evaluates the relevance of a sequence to a given context.
    
    Attributes:
        context: The context to compare against
        retriever: Function to retrieve relevant information
        threshold: Relevance threshold
    """
    
    def __init__(
        self,
        context: str,
        retriever: Callable[[str, str], float],
        threshold: float = 0.5,
        name: str = "context_aware_potential"
    ):
        """Initialize the Context-Aware Potential.
        
        Args:
            context: The context to compare against
            retriever: Function to retrieve relevant information
            threshold: Relevance threshold
            name: Name of the potential
        """
        super().__init__(name=name)
        self.context = context
        self.retriever = retriever
        self.threshold = threshold
    
    def evaluate(self, sequence: List[str]) -> float:
        """Evaluate the potential on a sequence.
        
        Args:
            sequence: The sequence to evaluate
            
        Returns:
            The potential value (between 0 and 1)
        """
        # Get sequence text
        text = "".join(sequence)
        
        # Calculate relevance
        try:
            relevance = self.retriever(text, self.context)
            
            # Apply threshold
            if relevance >= self.threshold:
                return 1.0
            else:
                # Scale between 0 and 1
                return max(0.0, relevance / self.threshold)
        except Exception as e:
            logger.warning(f"Error in ContextAwarePotential: {e}")
            return 1.0
    
    def is_efficient(self) -> bool:
        """Check if the potential is efficient.
        
        Returns:
            False (retrieval is expensive)
        """
        return False


# Common style patterns
FORMAL_STYLE = {
    r"\b(therefore|consequently|thus|hence|accordingly)\b": 0.2,
    r"\b(furthermore|moreover|additionally|in addition)\b": 0.2,
    r"\b(however|nevertheless|nonetheless|conversely)\b": 0.2,
    r"\b(it is|there are|one must|it should be noted)\b": 0.2,
    r"[^.!?]+[.][^.!?]+[.][^.!?]+[.]": 0.2  # Multiple complete sentences
}

CONVERSATIONAL_STYLE = {
    r"\b(I think|I believe|I feel|I'd say)\b": 0.2,
    r"\b(you know|right|actually|basically|honestly)\b": 0.2,
    r"\b(like|so|well|anyway|I mean)\b": 0.2,
    r"[!?]{1,3}": 0.2,
    r"\b(can't|won't|don't|isn't|aren't|wasn't|weren't)\b": 0.2
}

TECHNICAL_STYLE = {
    r"\b(algorithm|function|method|implementation|system)\b": 0.2,
    r"\b(data|input|output|parameter|variable)\b": 0.2,
    r"\b(analysis|performance|efficiency|optimization)\b": 0.2,
    r"\b(technical|specification|requirement|documentation)\b": 0.2,
    r"[a-zA-Z]+\([^)]*\)": 0.2  # Function calls
}

CREATIVE_STYLE = {
    r"\b(beautiful|stunning|gorgeous|magnificent|breathtaking)\b": 0.2,
    r"\b(imagine|dream|wonder|fantasy|magical)\b": 0.2,
    r"[a-zA-Z]+ing [a-zA-Z]+ (like|as) [a-zA-Z]+": 0.2,  # Similes
    r"[a-zA-Z]+ (is|was|are|were) [a-zA-Z]+": 0.2,  # Metaphors
    r"[a-zA-Z]+, [a-zA-Z]+, and [a-zA-Z]+": 0.2  # Rule of three
}


# Common constraints
def length_constraint(min_length: int, max_length: int) -> Callable[[str], float]:
    """Create a length constraint.
    
    Args:
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        Constraint function
    """
    def constraint(text: str) -> float:
        length = len(text)
        if min_length <= length <= max_length:
            return 1.0
        elif length < min_length:
            return max(0.1, length / min_length)
        else:
            return max(0.1, max_length / length)
    
    return constraint


def required_elements_constraint(elements: List[str], threshold: int = 1) -> Callable[[str], float]:
    """Create a required elements constraint.
    
    Args:
        elements: Required elements
        threshold: Minimum number of elements required
        
    Returns:
        Constraint function
    """
    def constraint(text: str) -> float:
        count = sum(1 for element in elements if element.lower() in text.lower())
        if count >= threshold:
            return 1.0
        elif count == 0:
            return 0.1
        else:
            return 0.1 + 0.9 * (count / threshold)
    
    return constraint


def forbidden_content_constraint(forbidden: List[str]) -> Callable[[str], float]:
    """Create a forbidden content constraint.
    
    Args:
        forbidden: Forbidden content
        
    Returns:
        Constraint function
    """
    def constraint(text: str) -> float:
        for content in forbidden:
            if content.lower() in text.lower():
                return 0.1
        return 1.0
    
    return constraint
