# Monte Carlo Techniques

## Overview

This module provides Monte Carlo techniques for probabilistic modeling, sampling, and decision-making under uncertainty. It includes particle filtering, importance sampling, sequential Monte Carlo, Monte Carlo Tree Search (MCTS), and Markov Chain Monte Carlo (MCMC) methods.

## Components

### Particle Filter

The particle filter module provides tools for state estimation in noisy environments:

- **ParticleFilter**: Filter for state estimation using particles
- **Particle**: Particle in a particle filter
- **SystemModel**: Model for system dynamics
- **ObservationModel**: Model for observations
- **ResamplingStrategy**: Strategy for resampling particles

### Importance Sampling

The importance sampling module provides tools for efficient sampling from complex distributions:

- **ImportanceSampler**: Sampler for efficient sampling
- **WeightedSample**: Sample with a weight
- **ProposalDistribution**: Distribution for proposing samples
- **TargetDistribution**: Target distribution to sample from
- **AdaptiveImportanceSampler**: Sampler that adapts the proposal distribution

### Sequential Monte Carlo

The sequential Monte Carlo module provides tools for dynamic systems with evolving states:

- **SequentialMonteCarlo**: Method for sequential estimation
- **SMCState**: State in sequential Monte Carlo
- **TransitionModel**: Model for state transitions
- **LikelihoodModel**: Model for observation likelihoods

### Monte Carlo Tree Search

The Monte Carlo Tree Search module provides tools for decision-making in large state spaces:

- **MonteCarloTreeSearch**: Search algorithm for decision-making
- **MCTSNode**: Node in a Monte Carlo Tree Search
- **ActionSelectionStrategy**: Strategy for selecting actions
- **UCB1Strategy**: Strategy using the UCB1 formula
- **RolloutPolicy**: Policy for rollouts
- **RandomRolloutPolicy**: Policy that selects actions randomly

### Markov Chain Monte Carlo

The Markov Chain Monte Carlo module provides tools for sampling from complex posterior distributions:

- **MarkovChainMonteCarlo**: Base class for MCMC methods
- **MCMCSample**: Sample in a Markov chain
- **ProposalDistribution**: Distribution for proposing new samples
- **MetropolisHastings**: Metropolis-Hastings algorithm
- **GibbsSampler**: Gibbs sampling algorithm
- **HamiltonianMC**: Hamiltonian Monte Carlo

### Utilities

The utilities module provides common functions and classes for Monte Carlo techniques:

- **Distribution**: Base class for probability distributions
- **GaussianDistribution**: Gaussian probability distribution
- **UniformDistribution**: Uniform probability distribution
- **DiscreteDistribution**: Discrete probability distribution
- **sample_from_distribution**: Function for sampling from a distribution
- **estimate_statistics**: Function for estimating statistics from samples

## Usage

### Particle Filter

```python
from augment_adam.monte_carlo import (
    ParticleFilter,
    LinearSystemModel,
    LinearObservationModel,
    SystematicResampling,
)
import numpy as np

# Create models
system_model = LinearSystemModel(
    state_transition_matrix=np.array([[1, 1], [0, 1]]),
    process_noise_covariance=np.array([[0.1, 0], [0, 0.1]])
)

observation_model = LinearObservationModel(
    observation_matrix=np.array([[1, 0]]),
    observation_noise_covariance=np.array([[1.0]])
)

# Create resampling strategy
resampling_strategy = SystematicResampling()

# Create particle filter
particle_filter = ParticleFilter(
    system_model=system_model,
    observation_model=observation_model,
    resampling_strategy=resampling_strategy,
    num_particles=100
)

# Initialize the filter
initial_states = [np.array([0, 0]) for _ in range(100)]
particle_filter.initialize(initial_states)

# Predict and update
particle_filter.predict(dt=1.0)
particle_filter.update(observation=np.array([1.0]))

# Estimate the state
estimated_state = particle_filter.estimate_state()
```

### Importance Sampling

```python
from augment_adam.monte_carlo import (
    ImportanceSampler,
    ProposalDistribution,
    TargetDistribution,
)
import numpy as np

# Create proposal distribution
class MyProposalDistribution(ProposalDistribution):
    def sample(self):
        return np.random.normal(0, 1)
    
    def pdf(self, x):
        return (1.0 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x ** 2)

# Create target distribution
class MyTargetDistribution(TargetDistribution):
    def pdf(self, x):
        return (1.0 / np.sqrt(2 * np.pi * 4)) * np.exp(-0.5 * (x - 2) ** 2 / 4)

# Create importance sampler
proposal = MyProposalDistribution(name="my_proposal")
target = MyTargetDistribution(name="my_target")
sampler = ImportanceSampler(proposal, target)

# Generate samples
samples = sampler.sample(num_samples=1000)

# Estimate expectation
expectation = sampler.estimate_expectation(lambda x: x ** 2)
```

### Sequential Monte Carlo

```python
from augment_adam.monte_carlo import (
    SequentialMonteCarlo,
    LinearTransitionModel,
    LinearLikelihoodModel,
)
import numpy as np

# Create models
transition_model = LinearTransitionModel(
    transition_matrix=np.array([[1, 1], [0, 1]]),
    noise_covariance=np.array([[0.1, 0], [0, 0.1]])
)

likelihood_model = LinearLikelihoodModel(
    observation_matrix=np.array([[1, 0]]),
    noise_covariance=np.array([[1.0]])
)

# Create sequential Monte Carlo
smc = SequentialMonteCarlo(
    transition_model=transition_model,
    likelihood_model=likelihood_model,
    num_particles=100
)

# Initialize the SMC
initial_states = [np.array([0, 0]) for _ in range(100)]
smc.initialize(initial_states)

# Predict and update
smc.predict()
smc.update(observation=np.array([1.0]))

# Estimate the state
estimated_state = smc.estimate_state()
```

### Monte Carlo Tree Search

```python
from augment_adam.monte_carlo import (
    MonteCarloTreeSearch,
    UCB1Strategy,
    RandomRolloutPolicy,
)

# Define the problem
def get_available_actions(state):
    # Return the available actions for the state
    return {"left", "right", "up", "down"}

def get_next_state(state, action):
    # Return the next state after taking the action
    if action == "left":
        return (state[0] - 1, state[1])
    elif action == "right":
        return (state[0] + 1, state[1])
    elif action == "up":
        return (state[0], state[1] - 1)
    elif action == "down":
        return (state[0], state[1] + 1)

def is_terminal(state):
    # Check if the state is terminal
    return state == (5, 5)

def get_reward(state):
    # Return the reward for the state
    if state == (5, 5):
        return 1.0
    else:
        return 0.0

# Create MCTS
initial_state = (0, 0)
selection_strategy = UCB1Strategy(exploration_weight=1.0)
rollout_policy = RandomRolloutPolicy()
mcts = MonteCarloTreeSearch(
    initial_state=initial_state,
    selection_strategy=selection_strategy,
    rollout_policy=rollout_policy,
    max_depth=10,
    max_iterations=1000
)

# Search for the best action
best_action = mcts.search(
    get_available_actions=get_available_actions,
    get_next_state=get_next_state,
    is_terminal=is_terminal,
    get_reward=get_reward
)
```

### Markov Chain Monte Carlo

```python
from augment_adam.monte_carlo import (
    MetropolisHastings,
    GaussianProposal,
)
import numpy as np

# Define the target distribution
def target_log_prob_fn(x):
    return -0.5 * np.sum((x - np.array([1.0, 2.0])) ** 2)

# Create proposal distribution
proposal = GaussianProposal(scale=0.1)

# Create MCMC sampler
mcmc = MetropolisHastings(
    target_log_prob_fn=target_log_prob_fn,
    proposal_distribution=proposal
)

# Generate samples
initial_state = np.array([0.0, 0.0])
samples = mcmc.sample(
    initial_state=initial_state,
    num_samples=1000,
    num_burnin=100,
    thin=1
)

# Compute statistics
acceptance_rate = mcmc.compute_acceptance_rate()
effective_sample_size = mcmc.compute_effective_sample_size()
```

## TODOs

- Add support for parallel Monte Carlo simulations (Issue #9)
- Implement adaptive sampling techniques (Issue #9)
- Add visualization tools for Monte Carlo results (Issue #9)
- Implement more advanced MCMC methods (Hamiltonian, No-U-Turn Sampler) (Issue #9)
- Add support for custom proposal distributions (Issue #9)
- Add support for particle filter diagnostics (Issue #9)
- Implement more sophisticated resampling strategies (Issue #9)
- Add support for adaptive proposal distributions (Issue #9)
- Implement more rollout policies for MCTS (Issue #9)
- Add support for MCMC diagnostics (Issue #9)
