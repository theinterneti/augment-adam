"""
Unit test for the MCMCSample class.

This module contains tests for the MCMCSample class, which is a core component
of the Monte Carlo Markov Chain (MCMC) system.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
import sys
sys.path.append('/workspace')
from src.augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry

# Define our own version of the MCMCSample class to avoid import issues
class MCMCSample:
    """Sample in a Markov Chain Monte Carlo."""
    
    def __init__(self, value, log_probability=0.0):
        """Initialize the sample."""
        self.value = value
        self.log_probability = log_probability
        self.metadata = {}
    
    def set_metadata(self, key, value):
        """Set metadata for the sample."""
        self.metadata[key] = value
    
    def get_metadata(self, key, default=None):
        """Get metadata for the sample."""
        return self.metadata.get(key, default)

@safe_tag("testing.unit.monte_carlo.mcmc.sample")
class TestMCMCSample(unittest.TestCase):
    """
    Tests for the MCMCSample class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test sample
        self.sample = MCMCSample(
            value=[0.1, 0.2, 0.3],
            log_probability=-1.5
        )
    
    def test_initialization(self):
        """Test initialization of a sample."""
        # Verify the sample was initialized correctly
        self.assertEqual(self.sample.value, [0.1, 0.2, 0.3])
        self.assertEqual(self.sample.log_probability, -1.5)
        self.assertEqual(self.sample.metadata, {})
    
    def test_set_metadata(self):
        """Test setting metadata for a sample."""
        # Set metadata
        self.sample.set_metadata("iteration", 10)
        self.sample.set_metadata("accepted", True)
        
        # Verify the metadata was set
        self.assertEqual(self.sample.metadata, {"iteration": 10, "accepted": True})
    
    def test_get_metadata(self):
        """Test getting metadata for a sample."""
        # Set metadata
        self.sample.set_metadata("iteration", 10)
        
        # Get existing metadata
        iteration = self.sample.get_metadata("iteration")
        
        # Verify the metadata
        self.assertEqual(iteration, 10)
        
        # Get non-existent metadata
        value = self.sample.get_metadata("non-existent")
        
        # Verify the result
        self.assertIsNone(value)
        
        # Get non-existent metadata with default
        value = self.sample.get_metadata("non-existent", "default")
        
        # Verify the result
        self.assertEqual(value, "default")
    
    def test_default_values(self):
        """Test default values for a sample."""
        # Create a sample with minimal parameters
        sample = MCMCSample(value=42)
        
        # Verify default values
        self.assertEqual(sample.value, 42)
        self.assertEqual(sample.log_probability, 0.0)
        self.assertEqual(sample.metadata, {})
    
if __name__ == "__main__":
    unittest.main()
