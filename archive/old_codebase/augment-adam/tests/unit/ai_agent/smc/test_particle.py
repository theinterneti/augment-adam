"""Unit tests for the Particle class."""

import unittest

from augment_adam.ai_agent.smc.particle import Particle


class TestParticle(unittest.TestCase):
    """Tests for the Particle class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sequence = ["Hello", " ", "world"]
        self.weight = 0.5
        self.log_weight = -0.693  # ln(0.5)
        self.metadata = {"key": "value"}
        
        self.particle = Particle(
            sequence=self.sequence,
            weight=self.weight,
            log_weight=self.log_weight,
            metadata=self.metadata
        )
    
    def test_initialization(self):
        """Test particle initialization."""
        self.assertEqual(self.particle.sequence, self.sequence)
        self.assertEqual(self.particle.weight, self.weight)
        self.assertEqual(self.particle.log_weight, self.log_weight)
        self.assertEqual(self.particle.metadata, self.metadata)
    
    def test_initialization_with_defaults(self):
        """Test particle initialization with default values."""
        particle = Particle()
        
        self.assertEqual(particle.sequence, [])
        self.assertEqual(particle.weight, 1.0)
        self.assertEqual(particle.log_weight, 0.0)
        self.assertEqual(particle.metadata, {})
    
    def test_extend(self):
        """Test extending a particle."""
        new_particle = self.particle.extend("!")
        
        # Check that the original particle is unchanged
        self.assertEqual(self.particle.sequence, self.sequence)
        
        # Check that the new particle has the extended sequence
        self.assertEqual(new_particle.sequence, self.sequence + ["!"])
        
        # Check that the weight and log_weight are copied
        self.assertEqual(new_particle.weight, self.weight)
        self.assertEqual(new_particle.log_weight, self.log_weight)
        
        # Check that the metadata is copied (but not the same object)
        self.assertEqual(new_particle.metadata, self.metadata)
        self.assertIsNot(new_particle.metadata, self.metadata)
    
    def test_update_weight(self):
        """Test updating the weight of a particle."""
        self.particle.update_weight(2.0)
        
        # Check that the weight is multiplied
        self.assertEqual(self.particle.weight, self.weight * 2.0)
        
        # Check that the log_weight is added
        self.assertEqual(self.particle.log_weight, self.log_weight + 2.0)
    
    def test_get_sequence_text(self):
        """Test getting the sequence as text."""
        self.assertEqual(self.particle.get_sequence_text(), "Hello world")
    
    def test_str_representation(self):
        """Test the string representation of a particle."""
        self.assertIn("Particle", str(self.particle))
        self.assertIn("Hello world", str(self.particle))
        self.assertIn("0.5", str(self.particle))


if __name__ == '__main__':
    unittest.main()
