"""Unit tests for the Potential classes."""

import unittest
from unittest.mock import MagicMock

from augment_adam.ai_agent.smc.potential import (
    Potential, GrammarPotential, SemanticPotential, RegexPotential
)


class TestPotential(unittest.TestCase):
    """Tests for the Potential base class."""

    def test_initialization(self):
        """Test potential initialization."""
        # Create a concrete subclass for testing
        class ConcretePotential(Potential):
            def evaluate(self, sequence):
                return 1.0
        
        potential = ConcretePotential(name="test_potential")
        
        self.assertEqual(potential.name, "test_potential")
    
    def test_is_efficient(self):
        """Test the is_efficient method."""
        # Create a concrete subclass for testing
        class ConcretePotential(Potential):
            def evaluate(self, sequence):
                return 1.0
        
        potential = ConcretePotential()
        
        # By default, potentials are efficient
        self.assertTrue(potential.is_efficient())


class TestGrammarPotential(unittest.TestCase):
    """Tests for the GrammarPotential class."""

    def setUp(self):
        """Set up test fixtures."""
        self.grammar = MagicMock()
        self.potential = GrammarPotential(
            grammar=self.grammar,
            name="grammar_potential"
        )
    
    def test_initialization(self):
        """Test grammar potential initialization."""
        self.assertEqual(self.potential.name, "grammar_potential")
        self.assertEqual(self.potential.grammar, self.grammar)
    
    def test_evaluate(self):
        """Test the evaluate method."""
        sequence = ["Hello", " ", "world"]
        
        # The evaluate method is a placeholder that always returns 1.0
        self.assertEqual(self.potential.evaluate(sequence), 1.0)
    
    def test_is_efficient(self):
        """Test the is_efficient method."""
        # Grammar potentials are efficient
        self.assertTrue(self.potential.is_efficient())


class TestSemanticPotential(unittest.TestCase):
    """Tests for the SemanticPotential class."""

    def setUp(self):
        """Set up test fixtures."""
        self.semantic_fn = MagicMock(return_value=0.8)
        self.potential = SemanticPotential(
            semantic_fn=self.semantic_fn,
            name="semantic_potential"
        )
    
    def test_initialization(self):
        """Test semantic potential initialization."""
        self.assertEqual(self.potential.name, "semantic_potential")
        self.assertEqual(self.potential.semantic_fn, self.semantic_fn)
    
    def test_evaluate(self):
        """Test the evaluate method."""
        sequence = ["Hello", " ", "world"]
        
        # The evaluate method should call the semantic function
        self.assertEqual(self.potential.evaluate(sequence), 0.8)
        self.semantic_fn.assert_called_once_with(sequence)
    
    def test_is_efficient(self):
        """Test the is_efficient method."""
        # Semantic potentials are not efficient
        self.assertFalse(self.potential.is_efficient())


class TestRegexPotential(unittest.TestCase):
    """Tests for the RegexPotential class."""

    def setUp(self):
        """Set up test fixtures."""
        self.pattern = r"Hello.*"
        self.potential = RegexPotential(
            pattern=self.pattern,
            name="regex_potential"
        )
    
    def test_initialization(self):
        """Test regex potential initialization."""
        self.assertEqual(self.potential.name, "regex_potential")
        self.assertEqual(self.potential.pattern, self.pattern)
    
    def test_evaluate_matching(self):
        """Test the evaluate method with a matching sequence."""
        sequence = ["Hello", " ", "world"]
        
        # The sequence matches the pattern, so the potential should return 1.0
        self.assertEqual(self.potential.evaluate(sequence), 1.0)
    
    def test_evaluate_non_matching(self):
        """Test the evaluate method with a non-matching sequence."""
        sequence = ["Goodbye", " ", "world"]
        
        # The sequence doesn't match the pattern, so the potential should return 0.0
        self.assertEqual(self.potential.evaluate(sequence), 0.0)


if __name__ == '__main__':
    unittest.main()
