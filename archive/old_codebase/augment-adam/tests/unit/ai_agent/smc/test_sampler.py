"""Unit tests for the SequentialMonteCarlo class."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from augment_adam.ai_agent.smc.sampler import SequentialMonteCarlo
from augment_adam.ai_agent.smc.particle import Particle
from augment_adam.ai_agent.smc.potential import Potential, RegexPotential


class TestSequentialMonteCarlo(unittest.TestCase):
    """Tests for the SequentialMonteCarlo class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create potentials for testing
        self.efficient_potential = RegexPotential(
            pattern=r".*",
            name="efficient_potential"
        )
        
        # Create a non-efficient potential
        class NonEfficientPotential(Potential):
            def evaluate(self, sequence):
                return 1.0
            
            def is_efficient(self):
                return False
        
        self.non_efficient_potential = NonEfficientPotential(
            name="non_efficient_potential"
        )
        
        # Create a sampler
        self.sampler = SequentialMonteCarlo(
            num_particles=10,
            potentials=[self.efficient_potential, self.non_efficient_potential],
            ess_threshold=0.5
        )
    
    def test_initialization(self):
        """Test sampler initialization."""
        self.assertEqual(self.sampler.num_particles, 10)
        self.assertEqual(len(self.sampler.potentials), 2)
        self.assertEqual(len(self.sampler.efficient_potentials), 1)
        self.assertEqual(len(self.sampler.expensive_potentials), 1)
        self.assertEqual(self.sampler.ess_threshold, 0.5)
    
    def test_update_potentials(self):
        """Test updating potentials."""
        # Create a new potential
        new_potential = RegexPotential(
            pattern=r".*",
            name="new_potential"
        )
        
        # Update potentials
        self.sampler.update_potentials([new_potential])
        
        # Check that the potentials were updated
        self.assertEqual(len(self.sampler.potentials), 1)
        self.assertEqual(len(self.sampler.efficient_potentials), 1)
        self.assertEqual(len(self.sampler.expensive_potentials), 0)
    
    def test_initialize_particles(self):
        """Test initializing particles."""
        # Initialize particles
        self.sampler.initialize_particles("Hello")
        
        # Check that particles were created
        self.assertEqual(len(self.sampler.particles), 10)
        
        # Check that each particle has the correct sequence
        for particle in self.sampler.particles:
            self.assertEqual(particle.sequence, list("Hello"))
    
    def test_extend_particles(self):
        """Test extending particles."""
        # Initialize particles
        self.sampler.initialize_particles("Hello")
        
        # Mock random.choices to return a predictable result
        with patch('random.choices', return_value=["!"]):
            # Extend particles
            self.sampler.extend_particles()
        
        # Check that particles were extended
        for particle in self.sampler.particles:
            self.assertEqual(particle.sequence, list("Hello") + ["!"])
    
    def test_reweight_particles(self):
        """Test reweighting particles."""
        # Initialize particles
        self.sampler.initialize_particles("Hello")
        
        # Mock the evaluate method to return a predictable result
        self.efficient_potential.evaluate = MagicMock(return_value=0.5)
        self.non_efficient_potential.evaluate = MagicMock(return_value=0.5)
        
        # Reweight particles
        self.sampler.reweight_particles()
        
        # Check that particles were reweighted
        for particle in self.sampler.particles:
            self.assertEqual(particle.weight, 0.25)  # 0.5 * 0.5
    
    def test_resample_particles(self):
        """Test resampling particles."""
        # Initialize particles
        self.sampler.initialize_particles("Hello")
        
        # Set particle weights to trigger resampling
        weights = np.zeros(10)
        weights[0] = 1.0  # One particle has all the weight
        
        for i, particle in enumerate(self.sampler.particles):
            particle.weight = weights[i]
        
        # Mock np.random.choice to return a predictable result
        with patch('numpy.random.choice', return_value=np.zeros(10, dtype=int)):
            # Resample particles
            self.sampler.resample_particles()
        
        # Check that particles were resampled
        for particle in self.sampler.particles:
            self.assertEqual(particle.weight, 0.1)  # 1.0 / 10
    
    def test_sample(self):
        """Test sampling."""
        # Mock the initialize_particles method
        self.sampler.initialize_particles = MagicMock()
        
        # Mock the extend_particles method
        self.sampler.extend_particles = MagicMock()
        
        # Mock the reweight_particles method
        self.sampler.reweight_particles = MagicMock()
        
        # Mock the resample_particles method
        self.sampler.resample_particles = MagicMock()
        
        # Create a particle with the highest weight
        best_particle = Particle(
            sequence=list("Hello world"),
            weight=1.0
        )
        
        # Set the particles
        self.sampler.particles = [
            Particle(sequence=list("Hello"), weight=0.5),
            best_particle
        ]
        
        # Mock random.random to return a value that will terminate sampling
        with patch('random.random', return_value=0.05):
            # Sample
            result = self.sampler.sample("Hello", max_tokens=10)
        
        # Check that the result is the sequence of the best particle
        self.assertEqual(result, "Hello world")
        
        # Verify that the methods were called
        self.sampler.initialize_particles.assert_called_once_with("Hello")
        self.sampler.extend_particles.assert_called_once()
        self.sampler.reweight_particles.assert_called_once()
        self.sampler.resample_particles.assert_called_once()


if __name__ == '__main__':
    unittest.main()
