"""
Base classes for Monte Carlo Tree Search.

This module provides the base classes for Monte Carlo Tree Search (MCTS),
including the MonteCarloTreeSearch class and node interfaces.
"""

import math
import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, Generic, Set

from augment_adam.utils.tagging import tag, TagCategory


S = TypeVar('S')  # Type of state
A = TypeVar('A')  # Type of action


@tag("monte_carlo.mcts")
class MCTSNode(Generic[S, A]):
    """
    Node in a Monte Carlo Tree Search.
    
    This class represents a node in a Monte Carlo Tree Search, which corresponds
    to a state in the search space.
    
    Attributes:
        state: The state represented by the node.
        parent: The parent node.
        action: The action that led to this node.
        children: The child nodes.
        visits: The number of times the node has been visited.
        value: The value of the node.
        metadata: Additional metadata for the node.
    
    TODO(Issue #9): Add support for node pruning
    TODO(Issue #9): Implement node validation
    """
    
    def __init__(
        self,
        state: S,
        parent: Optional['MCTSNode[S, A]'] = None,
        action: Optional[A] = None
    ) -> None:
        """
        Initialize the node.
        
        Args:
            state: The state represented by the node.
            parent: The parent node.
            action: The action that led to this node.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.children: Dict[A, 'MCTSNode[S, A]'] = {}
        self.visits = 0
        self.value = 0.0
        self.metadata: Dict[str, Any] = {}
    
    def is_leaf(self) -> bool:
        """
        Check if the node is a leaf node.
        
        Returns:
            True if the node is a leaf node, False otherwise.
        """
        return len(self.children) == 0
    
    def is_fully_expanded(self, available_actions: Set[A]) -> bool:
        """
        Check if the node is fully expanded.
        
        Args:
            available_actions: The available actions from the node's state.
            
        Returns:
            True if the node is fully expanded, False otherwise.
        """
        return all(action in self.children for action in available_actions)
    
    def add_child(self, action: A, child_state: S) -> 'MCTSNode[S, A]':
        """
        Add a child node.
        
        Args:
            action: The action that leads to the child node.
            child_state: The state of the child node.
            
        Returns:
            The child node.
        """
        child = MCTSNode(child_state, self, action)
        self.children[action] = child
        return child
    
    def update(self, value: float) -> None:
        """
        Update the node with a new value.
        
        Args:
            value: The value to update with.
        """
        self.visits += 1
        self.value += (value - self.value) / self.visits
    
    def get_ucb_value(self, exploration_weight: float = 1.0) -> float:
        """
        Compute the UCB value of the node.
        
        Args:
            exploration_weight: The exploration weight.
            
        Returns:
            The UCB value.
        """
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.value
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits) if self.parent else 0.0
        
        return exploitation + exploration
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the node.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the node.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.mcts")
class ActionSelectionStrategy(Generic[S, A], ABC):
    """
    Strategy for selecting actions in Monte Carlo Tree Search.
    
    This class defines the interface for action selection strategies in MCTS,
    which determine how actions are selected during the selection phase.
    
    Attributes:
        name: The name of the strategy.
        metadata: Additional metadata for the strategy.
    
    TODO(Issue #9): Add support for more selection strategies
    TODO(Issue #9): Implement strategy validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the action selection strategy.
        
        Args:
            name: The name of the strategy.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def select_action(self, node: MCTSNode[S, A], available_actions: Set[A]) -> A:
        """
        Select an action from a node.
        
        Args:
            node: The node to select an action from.
            available_actions: The available actions from the node's state.
            
        Returns:
            The selected action.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the strategy.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the strategy.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.mcts")
class UCB1Strategy(ActionSelectionStrategy[S, A]):
    """
    UCB1 action selection strategy for Monte Carlo Tree Search.
    
    This class implements the UCB1 action selection strategy, which balances
    exploration and exploitation using the UCB1 formula.
    
    Attributes:
        name: The name of the strategy.
        metadata: Additional metadata for the strategy.
        exploration_weight: The exploration weight.
    
    TODO(Issue #9): Add support for adaptive exploration weight
    TODO(Issue #9): Implement strategy validation
    """
    
    def __init__(self, exploration_weight: float = 1.0, name: str = "ucb1_strategy") -> None:
        """
        Initialize the UCB1 action selection strategy.
        
        Args:
            exploration_weight: The exploration weight.
            name: The name of the strategy.
        """
        super().__init__(name)
        
        self.exploration_weight = exploration_weight
        self.metadata["exploration_weight"] = exploration_weight
    
    def select_action(self, node: MCTSNode[S, A], available_actions: Set[A]) -> A:
        """
        Select an action using the UCB1 formula.
        
        Args:
            node: The node to select an action from.
            available_actions: The available actions from the node's state.
            
        Returns:
            The selected action.
        """
        # If the node is not fully expanded, select an unexplored action
        unexplored_actions = [action for action in available_actions if action not in node.children]
        if unexplored_actions:
            return random.choice(unexplored_actions)
        
        # Otherwise, select the action with the highest UCB value
        return max(
            node.children.items(),
            key=lambda item: item[1].get_ucb_value(self.exploration_weight)
        )[0]


@tag("monte_carlo.mcts")
class RolloutPolicy(Generic[S, A], ABC):
    """
    Policy for rollouts in Monte Carlo Tree Search.
    
    This class defines the interface for rollout policies in MCTS,
    which determine how actions are selected during the simulation phase.
    
    Attributes:
        name: The name of the policy.
        metadata: Additional metadata for the policy.
    
    TODO(Issue #9): Add support for more rollout policies
    TODO(Issue #9): Implement policy validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the rollout policy.
        
        Args:
            name: The name of the policy.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def select_action(self, state: S, available_actions: Set[A]) -> A:
        """
        Select an action for a state.
        
        Args:
            state: The state to select an action for.
            available_actions: The available actions from the state.
            
        Returns:
            The selected action.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the policy.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the policy.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("monte_carlo.mcts")
class RandomRolloutPolicy(RolloutPolicy[S, A]):
    """
    Random rollout policy for Monte Carlo Tree Search.
    
    This class implements a random rollout policy, which selects actions
    uniformly at random during the simulation phase.
    
    Attributes:
        name: The name of the policy.
        metadata: Additional metadata for the policy.
    
    TODO(Issue #9): Add support for weighted random selection
    TODO(Issue #9): Implement policy validation
    """
    
    def __init__(self, name: str = "random_rollout_policy") -> None:
        """
        Initialize the random rollout policy.
        
        Args:
            name: The name of the policy.
        """
        super().__init__(name)
    
    def select_action(self, state: S, available_actions: Set[A]) -> A:
        """
        Select an action uniformly at random.
        
        Args:
            state: The state to select an action for.
            available_actions: The available actions from the state.
            
        Returns:
            The selected action.
        """
        return random.choice(list(available_actions))


@tag("monte_carlo.mcts")
class MonteCarloTreeSearch(Generic[S, A]):
    """
    Monte Carlo Tree Search for decision-making.
    
    This class implements Monte Carlo Tree Search, which is a search algorithm
    for finding optimal decisions in a given domain by taking random samples
    in the decision space and building a search tree.
    
    Attributes:
        name: The name of the search.
        metadata: Additional metadata for the search.
        root: The root node of the search tree.
        selection_strategy: The action selection strategy.
        rollout_policy: The rollout policy.
        max_depth: The maximum depth of the search tree.
        max_iterations: The maximum number of iterations.
    
    TODO(Issue #9): Add support for MCTS diagnostics
    TODO(Issue #9): Implement MCTS validation
    """
    
    def __init__(
        self,
        initial_state: S,
        selection_strategy: ActionSelectionStrategy[S, A],
        rollout_policy: RolloutPolicy[S, A],
        max_depth: int = 10,
        max_iterations: int = 1000,
        name: str = "monte_carlo_tree_search"
    ) -> None:
        """
        Initialize the Monte Carlo Tree Search.
        
        Args:
            initial_state: The initial state.
            selection_strategy: The action selection strategy.
            rollout_policy: The rollout policy.
            max_depth: The maximum depth of the search tree.
            max_iterations: The maximum number of iterations.
            name: The name of the search.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}
        
        self.root = MCTSNode(initial_state)
        self.selection_strategy = selection_strategy
        self.rollout_policy = rollout_policy
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        
        self.metadata["max_depth"] = max_depth
        self.metadata["max_iterations"] = max_iterations
    
    def search(
        self,
        get_available_actions: Callable[[S], Set[A]],
        get_next_state: Callable[[S, A], S],
        is_terminal: Callable[[S], bool],
        get_reward: Callable[[S], float],
        num_iterations: Optional[int] = None
    ) -> A:
        """
        Perform the search.
        
        Args:
            get_available_actions: Function that returns the available actions for a state.
            get_next_state: Function that returns the next state given a state and an action.
            is_terminal: Function that checks if a state is terminal.
            get_reward: Function that returns the reward for a state.
            num_iterations: The number of iterations to perform. If None, uses max_iterations.
            
        Returns:
            The best action.
        """
        iterations = num_iterations or self.max_iterations
        
        for _ in range(iterations):
            # Selection and expansion
            node = self._select_and_expand(self.root, get_available_actions, get_next_state, is_terminal)
            
            # Simulation
            reward = self._simulate(node.state, get_available_actions, get_next_state, is_terminal, get_reward)
            
            # Backpropagation
            self._backpropagate(node, reward)
        
        # Return the best action
        return self._get_best_action()
    
    def _select_and_expand(
        self,
        node: MCTSNode[S, A],
        get_available_actions: Callable[[S], Set[A]],
        get_next_state: Callable[[S, A], S],
        is_terminal: Callable[[S], bool]
    ) -> MCTSNode[S, A]:
        """
        Select a node to expand and expand it.
        
        Args:
            node: The node to start selection from.
            get_available_actions: Function that returns the available actions for a state.
            get_next_state: Function that returns the next state given a state and an action.
            is_terminal: Function that checks if a state is terminal.
            
        Returns:
            The expanded node.
        """
        # If the node is terminal, return it
        if is_terminal(node.state):
            return node
        
        # Get available actions
        available_actions = get_available_actions(node.state)
        
        # If the node is not fully expanded, expand it
        if not node.is_fully_expanded(available_actions):
            # Select an unexplored action
            unexplored_actions = [action for action in available_actions if action not in node.children]
            action = random.choice(unexplored_actions)
            
            # Get the next state
            next_state = get_next_state(node.state, action)
            
            # Add a child node
            return node.add_child(action, next_state)
        
        # Otherwise, select a child node
        action = self.selection_strategy.select_action(node, available_actions)
        return self._select_and_expand(node.children[action], get_available_actions, get_next_state, is_terminal)
    
    def _simulate(
        self,
        state: S,
        get_available_actions: Callable[[S], Set[A]],
        get_next_state: Callable[[S, A], S],
        is_terminal: Callable[[S], bool],
        get_reward: Callable[[S], float]
    ) -> float:
        """
        Simulate a rollout from a state.
        
        Args:
            state: The state to start the rollout from.
            get_available_actions: Function that returns the available actions for a state.
            get_next_state: Function that returns the next state given a state and an action.
            is_terminal: Function that checks if a state is terminal.
            get_reward: Function that returns the reward for a state.
            
        Returns:
            The reward from the rollout.
        """
        depth = 0
        current_state = state
        
        while not is_terminal(current_state) and depth < self.max_depth:
            # Get available actions
            available_actions = get_available_actions(current_state)
            
            # If there are no available actions, break
            if not available_actions:
                break
            
            # Select an action
            action = self.rollout_policy.select_action(current_state, available_actions)
            
            # Get the next state
            current_state = get_next_state(current_state, action)
            
            depth += 1
        
        # Return the reward for the final state
        return get_reward(current_state)
    
    def _backpropagate(self, node: MCTSNode[S, A], reward: float) -> None:
        """
        Backpropagate the reward up the tree.
        
        Args:
            node: The node to start backpropagation from.
            reward: The reward to backpropagate.
        """
        while node is not None:
            node.update(reward)
            node = node.parent
    
    def _get_best_action(self) -> A:
        """
        Get the best action from the root node.
        
        Returns:
            The best action.
        """
        # Return the action with the highest value
        return max(
            self.root.children.items(),
            key=lambda item: item[1].value
        )[0]
    
    def update_root(self, action: A, next_state: S) -> None:
        """
        Update the root node after taking an action.
        
        Args:
            action: The action taken.
            next_state: The resulting state.
        """
        if action in self.root.children:
            # If the action has been explored, make the child the new root
            self.root = self.root.children[action]
            self.root.parent = None
            self.root.action = None
        else:
            # Otherwise, create a new root
            self.root = MCTSNode(next_state)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the search.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the search.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
