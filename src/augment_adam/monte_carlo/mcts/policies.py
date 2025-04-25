"""
Rollout policies for Monte Carlo Tree Search.

This module provides rollout policies for Monte Carlo Tree Search, including
greedy, heuristic, and epsilon-greedy policies.
"""

import random
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic, Set

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.monte_carlo.mcts.base import RolloutPolicy


S = TypeVar('S')  # Type of state
A = TypeVar('A')  # Type of action


@tag("monte_carlo.mcts")
class GreedyRolloutPolicy(RolloutPolicy[S, A]):
    """
    Greedy rollout policy for Monte Carlo Tree Search.
    
    This class implements a greedy rollout policy, which selects actions
    that maximize a given value function during the simulation phase.
    
    Attributes:
        name: The name of the policy.
        metadata: Additional metadata for the policy.
        value_function: The value function to maximize.
    
    TODO(Issue #9): Add support for more value functions
    TODO(Issue #9): Implement policy validation
    """
    
    def __init__(
        self,
        value_function: Callable[[S, A], float],
        name: str = "greedy_rollout_policy"
    ) -> None:
        """
        Initialize the greedy rollout policy.
        
        Args:
            value_function: The value function to maximize.
            name: The name of the policy.
        """
        super().__init__(name)
        
        self.value_function = value_function
    
    def select_action(self, state: S, available_actions: Set[A]) -> A:
        """
        Select the action that maximizes the value function.
        
        Args:
            state: The state to select an action for.
            available_actions: The available actions from the state.
            
        Returns:
            The selected action.
        """
        # If there are no available actions, raise an error
        if not available_actions:
            raise ValueError("No available actions")
        
        # Return the action with the highest value
        return max(
            available_actions,
            key=lambda action: self.value_function(state, action)
        )


@tag("monte_carlo.mcts")
class HeuristicRolloutPolicy(RolloutPolicy[S, A]):
    """
    Heuristic rollout policy for Monte Carlo Tree Search.
    
    This class implements a heuristic rollout policy, which selects actions
    based on a heuristic function during the simulation phase.
    
    Attributes:
        name: The name of the policy.
        metadata: Additional metadata for the policy.
        heuristic: The heuristic function.
    
    TODO(Issue #9): Add support for more heuristic functions
    TODO(Issue #9): Implement policy validation
    """
    
    def __init__(
        self,
        heuristic: Callable[[S, A], float],
        name: str = "heuristic_rollout_policy"
    ) -> None:
        """
        Initialize the heuristic rollout policy.
        
        Args:
            heuristic: The heuristic function.
            name: The name of the policy.
        """
        super().__init__(name)
        
        self.heuristic = heuristic
    
    def select_action(self, state: S, available_actions: Set[A]) -> A:
        """
        Select an action based on the heuristic function.
        
        Args:
            state: The state to select an action for.
            available_actions: The available actions from the state.
            
        Returns:
            The selected action.
        """
        # If there are no available actions, raise an error
        if not available_actions:
            raise ValueError("No available actions")
        
        # Compute heuristic values
        heuristic_values = {action: self.heuristic(state, action) for action in available_actions}
        
        # Normalize heuristic values
        total = sum(heuristic_values.values())
        if total > 0:
            probabilities = {action: value / total for action, value in heuristic_values.items()}
        else:
            # If all heuristic values are zero, use uniform probabilities
            probabilities = {action: 1.0 / len(available_actions) for action in available_actions}
        
        # Select an action based on probabilities
        actions = list(probabilities.keys())
        probs = [probabilities[action] for action in actions]
        
        return random.choices(actions, weights=probs, k=1)[0]


@tag("monte_carlo.mcts")
class EpsilonGreedyRolloutPolicy(RolloutPolicy[S, A]):
    """
    Epsilon-greedy rollout policy for Monte Carlo Tree Search.
    
    This class implements an epsilon-greedy rollout policy, which selects the
    best action with probability 1-epsilon and a random action with probability epsilon.
    
    Attributes:
        name: The name of the policy.
        metadata: Additional metadata for the policy.
        value_function: The value function to maximize.
        epsilon: The probability of selecting a random action.
    
    TODO(Issue #9): Add support for decaying epsilon
    TODO(Issue #9): Implement policy validation
    """
    
    def __init__(
        self,
        value_function: Callable[[S, A], float],
        epsilon: float = 0.1,
        name: str = "epsilon_greedy_rollout_policy"
    ) -> None:
        """
        Initialize the epsilon-greedy rollout policy.
        
        Args:
            value_function: The value function to maximize.
            epsilon: The probability of selecting a random action.
            name: The name of the policy.
        """
        super().__init__(name)
        
        self.value_function = value_function
        self.epsilon = epsilon
        
        self.metadata["epsilon"] = epsilon
    
    def select_action(self, state: S, available_actions: Set[A]) -> A:
        """
        Select an action using the epsilon-greedy strategy.
        
        Args:
            state: The state to select an action for.
            available_actions: The available actions from the state.
            
        Returns:
            The selected action.
        """
        # If there are no available actions, raise an error
        if not available_actions:
            raise ValueError("No available actions")
        
        # With probability epsilon, select a random action
        if random.random() < self.epsilon:
            return random.choice(list(available_actions))
        
        # Otherwise, select the best action
        return max(
            available_actions,
            key=lambda action: self.value_function(state, action)
        )
