"""
Probability distributions for Monte Carlo techniques.

This module provides probability distributions for Monte Carlo techniques,
including Gaussian, uniform, and discrete distributions.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory


T = TypeVar('T')


@tag("monte_carlo.utils")
class Distribution(ABC):
    """
    Base class for probability distributions.
    
    This class defines the interface for probability distributions, which
    are used for sampling and computing probabilities in Monte Carlo techniques.
    
    Attributes:
        name: The name of the distribution.
        metadata: Additional metadata for the distribution.
    
    TODO(Issue #9): Add support for more distribution types
    TODO(Issue #9): Implement distribution validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the distribution.
        
        Args:
            name: The name of the distribution.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def sample(self) -> Any:
        """
        Sample from the distribution.
        
        Returns:
            A sample from the distribution.
        """
        pass
    
    @abstractmethod
    def pdf(self, x: Any) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        pass
    
    @abstractmethod
    def log_pdf(self, x: Any) -> float:
        """
        Compute the log probability density function at a point.
        
        Args:
            x: The point at which to compute the log PDF.
            
        Returns:
            The log PDF value at the point.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the distribution.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the distribution.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.utils")
class GaussianDistribution(Distribution):
    """
    Gaussian (normal) probability distribution.
    
    This class implements a Gaussian probability distribution, which is
    characterized by a mean and standard deviation.
    
    Attributes:
        name: The name of the distribution.
        metadata: Additional metadata for the distribution.
        mean: The mean of the distribution.
        std_dev: The standard deviation of the distribution.
        dimension: The dimension of the distribution.
    
    TODO(Issue #9): Add support for multivariate Gaussian distributions
    TODO(Issue #9): Implement distribution validation
    """
    
    def __init__(
        self,
        mean: Union[float, np.ndarray],
        std_dev: Union[float, np.ndarray],
        name: str = "gaussian_distribution",
        dimension: int = 1
    ) -> None:
        """
        Initialize the Gaussian distribution.
        
        Args:
            mean: The mean of the distribution.
            std_dev: The standard deviation of the distribution.
            name: The name of the distribution.
            dimension: The dimension of the distribution.
        """
        super().__init__(name)
        
        self.mean = mean
        self.std_dev = std_dev
        self.dimension = dimension
        
        self.metadata["mean"] = mean
        self.metadata["std_dev"] = std_dev
        self.metadata["dimension"] = dimension
    
    def sample(self) -> Union[float, np.ndarray]:
        """
        Sample from the Gaussian distribution.
        
        Returns:
            A sample from the distribution.
        """
        if self.dimension == 1:
            return random.gauss(self.mean, self.std_dev)
        else:
            return np.random.normal(self.mean, self.std_dev, self.dimension)
    
    def pdf(self, x: Union[float, np.ndarray]) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        if self.dimension == 1:
            return (1.0 / (self.std_dev * math.sqrt(2 * math.pi))) * \
                   math.exp(-0.5 * ((x - self.mean) / self.std_dev) ** 2)
        else:
            # For multivariate Gaussian, we need to compute the determinant of the covariance matrix
            # and the Mahalanobis distance, which is more complex
            # For simplicity, we'll assume diagonal covariance matrix
            return np.prod(
                1.0 / (self.std_dev * math.sqrt(2 * math.pi)) * \
                np.exp(-0.5 * ((x - self.mean) / self.std_dev) ** 2)
            )
    
    def log_pdf(self, x: Union[float, np.ndarray]) -> float:
        """
        Compute the log probability density function at a point.
        
        Args:
            x: The point at which to compute the log PDF.
            
        Returns:
            The log PDF value at the point.
        """
        if self.dimension == 1:
            return -0.5 * math.log(2 * math.pi) - math.log(self.std_dev) - \
                   0.5 * ((x - self.mean) / self.std_dev) ** 2
        else:
            # For multivariate Gaussian, we need to compute the determinant of the covariance matrix
            # and the Mahalanobis distance, which is more complex
            # For simplicity, we'll assume diagonal covariance matrix
            return np.sum(
                -0.5 * math.log(2 * math.pi) - np.log(self.std_dev) - \
                0.5 * ((x - self.mean) / self.std_dev) ** 2
            )


@tag("monte_carlo.utils")
class UniformDistribution(Distribution):
    """
    Uniform probability distribution.
    
    This class implements a uniform probability distribution, which is
    characterized by a lower and upper bound.
    
    Attributes:
        name: The name of the distribution.
        metadata: Additional metadata for the distribution.
        lower_bound: The lower bound of the distribution.
        upper_bound: The upper bound of the distribution.
        dimension: The dimension of the distribution.
    
    TODO(Issue #9): Add support for multivariate uniform distributions
    TODO(Issue #9): Implement distribution validation
    """
    
    def __init__(
        self,
        lower_bound: Union[float, np.ndarray],
        upper_bound: Union[float, np.ndarray],
        name: str = "uniform_distribution",
        dimension: int = 1
    ) -> None:
        """
        Initialize the uniform distribution.
        
        Args:
            lower_bound: The lower bound of the distribution.
            upper_bound: The upper bound of the distribution.
            name: The name of the distribution.
            dimension: The dimension of the distribution.
        """
        super().__init__(name)
        
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.dimension = dimension
        
        self.metadata["lower_bound"] = lower_bound
        self.metadata["upper_bound"] = upper_bound
        self.metadata["dimension"] = dimension
    
    def sample(self) -> Union[float, np.ndarray]:
        """
        Sample from the uniform distribution.
        
        Returns:
            A sample from the distribution.
        """
        if self.dimension == 1:
            return random.uniform(self.lower_bound, self.upper_bound)
        else:
            return np.random.uniform(self.lower_bound, self.upper_bound, self.dimension)
    
    def pdf(self, x: Union[float, np.ndarray]) -> float:
        """
        Compute the probability density function (PDF) at a point.
        
        Args:
            x: The point at which to compute the PDF.
            
        Returns:
            The PDF value at the point.
        """
        if self.dimension == 1:
            if self.lower_bound <= x <= self.upper_bound:
                return 1.0 / (self.upper_bound - self.lower_bound)
            else:
                return 0.0
        else:
            # For multivariate uniform, we need to check if the point is within the bounds
            # For simplicity, we'll assume independent uniform distributions
            in_bounds = np.all((self.lower_bound <= x) & (x <= self.upper_bound))
            if in_bounds:
                return np.prod(1.0 / (self.upper_bound - self.lower_bound))
            else:
                return 0.0
    
    def log_pdf(self, x: Union[float, np.ndarray]) -> float:
        """
        Compute the log probability density function at a point.
        
        Args:
            x: The point at which to compute the log PDF.
            
        Returns:
            The log PDF value at the point.
        """
        pdf_value = self.pdf(x)
        if pdf_value > 0:
            return math.log(pdf_value)
        else:
            return float('-inf')


@tag("monte_carlo.utils")
class DiscreteDistribution(Distribution):
    """
    Discrete probability distribution.
    
    This class implements a discrete probability distribution, which is
    characterized by a set of values and their probabilities.
    
    Attributes:
        name: The name of the distribution.
        metadata: Additional metadata for the distribution.
        values: The possible values of the distribution.
        probabilities: The probabilities of the values.
    
    TODO(Issue #9): Add support for multivariate discrete distributions
    TODO(Issue #9): Implement distribution validation
    """
    
    def __init__(
        self,
        values: List[Any],
        probabilities: Optional[List[float]] = None,
        name: str = "discrete_distribution"
    ) -> None:
        """
        Initialize the discrete distribution.
        
        Args:
            values: The possible values of the distribution.
            probabilities: The probabilities of the values. If None, uniform probabilities are used.
            name: The name of the distribution.
        """
        super().__init__(name)
        
        self.values = values
        
        if probabilities is None:
            # Use uniform probabilities
            self.probabilities = [1.0 / len(values)] * len(values)
        else:
            # Normalize probabilities to sum to 1
            total = sum(probabilities)
            self.probabilities = [p / total for p in probabilities]
        
        self.metadata["values"] = values
        self.metadata["probabilities"] = self.probabilities
    
    def sample(self) -> Any:
        """
        Sample from the discrete distribution.
        
        Returns:
            A sample from the distribution.
        """
        return random.choices(self.values, weights=self.probabilities, k=1)[0]
    
    def pdf(self, x: Any) -> float:
        """
        Compute the probability mass function (PMF) at a point.
        
        Args:
            x: The point at which to compute the PMF.
            
        Returns:
            The PMF value at the point.
        """
        try:
            index = self.values.index(x)
            return self.probabilities[index]
        except ValueError:
            return 0.0
    
    def log_pdf(self, x: Any) -> float:
        """
        Compute the log probability mass function at a point.
        
        Args:
            x: The point at which to compute the log PMF.
            
        Returns:
            The log PMF value at the point.
        """
        pmf_value = self.pdf(x)
        if pmf_value > 0:
            return math.log(pmf_value)
        else:
            return float('-inf')


def sample_from_distribution(
    distribution: Distribution,
    num_samples: int = 1
) -> Union[List[Any], Any]:
    """
    Sample from a distribution.
    
    Args:
        distribution: The distribution to sample from.
        num_samples: The number of samples to generate.
        
    Returns:
        A list of samples from the distribution, or a single sample if num_samples is 1.
    """
    if num_samples == 1:
        return distribution.sample()
    else:
        return [distribution.sample() for _ in range(num_samples)]
