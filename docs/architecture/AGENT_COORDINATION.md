# Agent Coordination

## Overview

This document describes the architecture of the Agent Coordination system in Augment Adam. The Agent Coordination system enables multiple agents to work together effectively, sharing information and coordinating their actions to solve complex problems.

## Architecture Diagram

The Agent Coordination architecture consists of several components that work together to enable effective collaboration between agents.

```
                  +----------------+
                  | CoordinationHub |
                  +-------+--------+
                          |
          +---------------+---------------+
          |               |               |
+---------v------+ +------v-------+ +-----v--------+
|  TeamManager   | | WorkflowEngine| |MessageBroker  |
+-------+-------+ +------+-------+ +-----+--------+
        |                |               |
+-------v-------+ +------v-------+ +-----v--------+
|    Team       | |   Workflow    | |   Message    |
|               | |               | |              |
+---------------+ +--------------+ +--------------+
```

## Components

### Coordination Hub

The Coordination Hub is the central component of the Agent Coordination system. It manages teams of agents, workflows, and communication between agents.

#### Responsibilities

- Manage teams of agents
- Execute workflows
- Route messages between agents
- Monitor agent performance
- Handle errors and exceptions

#### Interfaces

- `create_team(name: str, agents: List[Agent]) -> Team`: Create a team of agents.
- `execute_workflow(workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]`: Execute a workflow with the given inputs.
- `send_message(sender: Agent, recipient: Agent, content: str, metadata: Optional[Dict[str, Any]] = None) -> str`: Send a message from one agent to another.

#### Implementation

The Coordination Hub is implemented as a class that coordinates teams, workflows, and messages:

```python
from typing import Dict, List, Any, Optional

from augment_adam.ai_agent import Agent
from augment_adam.ai_agent.coordination.team import Team, TeamManager
from augment_adam.ai_agent.coordination.workflow import Workflow, WorkflowEngine
from augment_adam.ai_agent.coordination.message import Message, MessageBroker

class CoordinationHub:
    """Hub for coordinating agents, teams, workflows, and messages."""
    
    def __init__(self):
        """Initialize the coordination hub."""
        self.team_manager = TeamManager()
        self.workflow_engine = WorkflowEngine()
        self.message_broker = MessageBroker()
        
    def create_team(self, name: str, agents: List[Agent]) -> Team:
        """Create a team of agents.
        
        Args:
            name: Name of the team.
            agents: List of agents in the team.
            
        Returns:
            The created team.
        """
        return self.team_manager.create_team(name, agents)
    
    def execute_workflow(self, workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with the given inputs.
        
        Args:
            workflow: Workflow to execute.
            inputs: Inputs for the workflow.
            
        Returns:
            Outputs from the workflow.
        """
        return self.workflow_engine.execute(workflow, inputs)
    
    def send_message(self, sender: Agent, recipient: Agent, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a message from one agent to another.
        
        Args:
            sender: Agent sending the message.
            recipient: Agent receiving the message.
            content: Content of the message.
            metadata: Optional metadata for the message.
            
        Returns:
            ID of the message.
        """
        message = Message(sender=sender, recipient=recipient, content=content, metadata=metadata or {})
        return self.message_broker.send(message)
```

### Team Manager

The Team Manager is responsible for creating and managing teams of agents. It handles team creation, agent assignment, and team coordination.

#### Responsibilities

- Create and manage teams
- Assign agents to teams
- Monitor team performance
- Handle team-level coordination

#### Interfaces

- `create_team(name: str, agents: List[Agent]) -> Team`: Create a team of agents.
- `get_team(name: str) -> Optional[Team]`: Get a team by name.
- `add_agent_to_team(team: Team, agent: Agent) -> None`: Add an agent to a team.
- `remove_agent_from_team(team: Team, agent: Agent) -> None`: Remove an agent from a team.

#### Implementation

The Team Manager is implemented as a class that manages teams of agents:

```python
from typing import Dict, List, Any, Optional

from augment_adam.ai_agent import Agent
from augment_adam.ai_agent.coordination.team import Team

class TeamManager:
    """Manager for teams of agents."""
    
    def __init__(self):
        """Initialize the team manager."""
        self.teams = {}
        
    def create_team(self, name: str, agents: List[Agent]) -> Team:
        """Create a team of agents.
        
        Args:
            name: Name of the team.
            agents: List of agents in the team.
            
        Returns:
            The created team.
        """
        team = Team(name=name, agents=agents)
        self.teams[name] = team
        return team
    
    def get_team(self, name: str) -> Optional[Team]:
        """Get a team by name.
        
        Args:
            name: Name of the team.
            
        Returns:
            The team, or None if not found.
        """
        return self.teams.get(name)
    
    def add_agent_to_team(self, team: Team, agent: Agent) -> None:
        """Add an agent to a team.
        
        Args:
            team: Team to add the agent to.
            agent: Agent to add to the team.
        """
        team.add_agent(agent)
        
    def remove_agent_from_team(self, team: Team, agent: Agent) -> None:
        """Remove an agent from a team.
        
        Args:
            team: Team to remove the agent from.
            agent: Agent to remove from the team.
        """
        team.remove_agent(agent)
```

### Workflow Engine

The Workflow Engine is responsible for executing workflows. It handles workflow execution, step coordination, and error handling.

#### Responsibilities

- Execute workflows
- Coordinate workflow steps
- Handle workflow errors
- Monitor workflow performance

#### Interfaces

- `execute(workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]`: Execute a workflow with the given inputs.
- `register_workflow(workflow: Workflow) -> None`: Register a workflow with the engine.
- `get_workflow(name: str) -> Optional[Workflow]`: Get a workflow by name.

#### Implementation

The Workflow Engine is implemented as a class that executes workflows:

```python
from typing import Dict, List, Any, Optional

from augment_adam.ai_agent.coordination.workflow import Workflow, WorkflowStep

class WorkflowEngine:
    """Engine for executing workflows."""
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.workflows = {}
        
    def execute(self, workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with the given inputs.
        
        Args:
            workflow: Workflow to execute.
            inputs: Inputs for the workflow.
            
        Returns:
            Outputs from the workflow.
        """
        # Initialize the workflow state
        state = inputs.copy()
        
        # Execute each step in the workflow
        for step in workflow.steps:
            try:
                # Get the inputs for the step
                step_inputs = {}
                for input_name, input_source in step.inputs.items():
                    if input_source in state:
                        step_inputs[input_name] = state[input_source]
                
                # Execute the step
                step_outputs = step.execute(step_inputs)
                
                # Update the workflow state with the step outputs
                for output_name, output_value in step_outputs.items():
                    state[f"{step.name}.{output_name}"] = output_value
            except Exception as e:
                # Handle step execution errors
                if step.error_handler:
                    # If the step has an error handler, use it
                    error_outputs = step.error_handler(e, step_inputs)
                    for output_name, output_value in error_outputs.items():
                        state[f"{step.name}.{output_name}"] = output_value
                else:
                    # Otherwise, raise the error
                    raise
        
        # Return the final workflow state
        return state
    
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow with the engine.
        
        Args:
            workflow: Workflow to register.
        """
        self.workflows[workflow.name] = workflow
        
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name.
        
        Args:
            name: Name of the workflow.
            
        Returns:
            The workflow, or None if not found.
        """
        return self.workflows.get(name)
```

### Message Broker

The Message Broker is responsible for routing messages between agents. It handles message sending, receiving, and delivery confirmation.

#### Responsibilities

- Route messages between agents
- Handle message delivery
- Confirm message receipt
- Store message history

#### Interfaces

- `send(message: Message) -> str`: Send a message.
- `receive(agent: Agent) -> List[Message]`: Receive messages for an agent.
- `get_message(message_id: str) -> Optional[Message]`: Get a message by ID.
- `get_messages_between(sender: Agent, recipient: Agent) -> List[Message]`: Get messages between two agents.

#### Implementation

The Message Broker is implemented as a class that routes messages between agents:

```python
from typing import Dict, List, Any, Optional
import uuid

from augment_adam.ai_agent import Agent
from augment_adam.ai_agent.coordination.message import Message

class MessageBroker:
    """Broker for routing messages between agents."""
    
    def __init__(self):
        """Initialize the message broker."""
        self.messages = {}
        self.agent_messages = {}
        
    def send(self, message: Message) -> str:
        """Send a message.
        
        Args:
            message: Message to send.
            
        Returns:
            ID of the message.
        """
        # Generate a unique ID for the message
        message_id = str(uuid.uuid4())
        message.id = message_id
        
        # Store the message
        self.messages[message_id] = message
        
        # Add the message to the recipient's message queue
        recipient_id = message.recipient.id
        if recipient_id not in self.agent_messages:
            self.agent_messages[recipient_id] = []
        self.agent_messages[recipient_id].append(message)
        
        return message_id
    
    def receive(self, agent: Agent) -> List[Message]:
        """Receive messages for an agent.
        
        Args:
            agent: Agent to receive messages for.
            
        Returns:
            List of messages for the agent.
        """
        agent_id = agent.id
        if agent_id not in self.agent_messages:
            return []
        
        # Get the agent's messages
        messages = self.agent_messages[agent_id]
        
        # Clear the agent's message queue
        self.agent_messages[agent_id] = []
        
        return messages
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID.
        
        Args:
            message_id: ID of the message.
            
        Returns:
            The message, or None if not found.
        """
        return self.messages.get(message_id)
    
    def get_messages_between(self, sender: Agent, recipient: Agent) -> List[Message]:
        """Get messages between two agents.
        
        Args:
            sender: Agent who sent the messages.
            recipient: Agent who received the messages.
            
        Returns:
            List of messages between the agents.
        """
        sender_id = sender.id
        recipient_id = recipient.id
        
        # Find messages where the sender and recipient match
        messages = []
        for message in self.messages.values():
            if message.sender.id == sender_id and message.recipient.id == recipient_id:
                messages.append(message)
        
        return messages
```



## Interfaces

### Agent Coordination Interface

The Agent Coordination system provides a simple interface for coordinating agents.

```python
from typing import Dict, List, Any, Optional

from augment_adam.ai_agent import Agent
from augment_adam.ai_agent.coordination.team import Team
from augment_adam.ai_agent.coordination.workflow import Workflow

class AgentCoordinationInterface:
    """Interface for agent coordination."""
    
    def create_team(self, name: str, agents: List[Agent]) -> Team:
        """Create a team of agents.
        
        Args:
            name: Name of the team.
            agents: List of agents in the team.
            
        Returns:
            The created team.
        """
        pass
    
    def execute_workflow(self, workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with the given inputs.
        
        Args:
            workflow: Workflow to execute.
            inputs: Inputs for the workflow.
            
        Returns:
            Outputs from the workflow.
        """
        pass
    
    def send_message(self, sender: Agent, recipient: Agent, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a message from one agent to another.
        
        Args:
            sender: Agent sending the message.
            recipient: Agent receiving the message.
            content: Content of the message.
            metadata: Optional metadata for the message.
            
        Returns:
            ID of the message.
        """
        pass
```



## Workflows

### Creating a Team

The process of creating a team of agents.

#### Steps

1. Create a coordination hub
2. Define the team name
3. Select agents for the team
4. Call the create_team method
5. The team is created and returned

#### Diagram

```
User -> CoordinationHub: create_team(name, agents)
CoordinationHub -> TeamManager: create_team(name, agents)
TeamManager -> Team: new Team(name, agents)
Team -> TeamManager: team
TeamManager -> CoordinationHub: team
CoordinationHub -> User: team
```

### Executing a Workflow

The process of executing a workflow with a team of agents.

#### Steps

1. Create a coordination hub
2. Define the workflow
3. Prepare the workflow inputs
4. Call the execute_workflow method
5. The workflow is executed and the outputs are returned

#### Diagram

```
User -> CoordinationHub: execute_workflow(workflow, inputs)
CoordinationHub -> WorkflowEngine: execute(workflow, inputs)
WorkflowEngine -> WorkflowStep: execute(step_inputs)
WorkflowStep -> WorkflowEngine: step_outputs
WorkflowEngine -> CoordinationHub: outputs
CoordinationHub -> User: outputs
```

### Sending Messages

The process of sending messages between agents.

#### Steps

1. Create a coordination hub
2. Define the sender and recipient agents
3. Prepare the message content and metadata
4. Call the send_message method
5. The message is sent and the message ID is returned

#### Diagram

```
User -> CoordinationHub: send_message(sender, recipient, content, metadata)
CoordinationHub -> MessageBroker: send(message)
MessageBroker -> Message: new Message(sender, recipient, content, metadata)
Message -> MessageBroker: message
MessageBroker -> CoordinationHub: message_id
CoordinationHub -> User: message_id
```



## Examples

### Creating a Team

Example of creating a team of agents.

```python
from augment_adam.ai_agent.coordination import CoordinationHub
from augment_adam.ai_agent import MCPAgent, WorkerAgent

# Create a coordination hub
hub = CoordinationHub()

# Create agents
mcp_agent = MCPAgent(name="MCP Agent")
worker_agent1 = WorkerAgent(name="Worker Agent 1")
worker_agent2 = WorkerAgent(name="Worker Agent 2")

# Create a team
team = hub.create_team("Problem Solving Team", [mcp_agent, worker_agent1, worker_agent2])

# Print team information
print(f"Team Name: {team.name}")
print(f"Team Agents: {[agent.name for agent in team.agents]}")
```

### Executing a Workflow

Example of executing a workflow with a team of agents.

```python
from augment_adam.ai_agent.coordination import CoordinationHub, Workflow, WorkflowStep
from augment_adam.ai_agent import MCPAgent, WorkerAgent

# Create a coordination hub
hub = CoordinationHub()

# Create agents
mcp_agent = MCPAgent(name="MCP Agent")
worker_agent1 = WorkerAgent(name="Worker Agent 1")
worker_agent2 = WorkerAgent(name="Worker Agent 2")

# Create a team
team = hub.create_team("Problem Solving Team", [mcp_agent, worker_agent1, worker_agent2])

# Define workflow steps
step1 = WorkflowStep(
    name="planning",
    agent=mcp_agent,
    inputs={"problem": "problem"},
    outputs=["plan"],
    execute=lambda inputs: {"plan": mcp_agent.plan(inputs["problem"])}
)

step2 = WorkflowStep(
    name="execution",
    agent=worker_agent1,
    inputs={"plan": "planning.plan"},
    outputs=["result"],
    execute=lambda inputs: {"result": worker_agent1.execute(inputs["plan"])}
)

step3 = WorkflowStep(
    name="verification",
    agent=worker_agent2,
    inputs={"result": "execution.result", "problem": "problem"},
    outputs=["verified"],
    execute=lambda inputs: {"verified": worker_agent2.verify(inputs["result"], inputs["problem"])}
)

# Create a workflow
workflow = Workflow(
    name="problem_solving",
    steps=[step1, step2, step3]
)

# Execute the workflow
result = hub.execute_workflow(workflow, {"problem": "What is the optimal strategy for the Prisoner's Dilemma?"})

# Print the result
print(f"Plan: {result['planning.plan']}")
print(f"Result: {result['execution.result']}")
print(f"Verified: {result['verification.verified']}")
```

### Sending Messages

Example of sending messages between agents.

```python
from augment_adam.ai_agent.coordination import CoordinationHub
from augment_adam.ai_agent import MCPAgent, WorkerAgent

# Create a coordination hub
hub = CoordinationHub()

# Create agents
mcp_agent = MCPAgent(name="MCP Agent")
worker_agent = WorkerAgent(name="Worker Agent")

# Send a message from the MCP agent to the worker agent
message_id = hub.send_message(
    sender=mcp_agent,
    recipient=worker_agent,
    content="Please analyze this data: [1, 2, 3, 4, 5]",
    metadata={"priority": "high", "task": "data_analysis"}
)

# Worker agent receives messages
messages = hub.message_broker.receive(worker_agent)

# Worker agent processes messages
for message in messages:
    print(f"Message from {message.sender.name}: {message.content}")
    print(f"Metadata: {message.metadata}")
    
    # Worker agent sends a response
    response_id = hub.send_message(
        sender=worker_agent,
        recipient=message.sender,
        content="Analysis complete. The average is 3.0.",
        metadata={"priority": "high", "task": "data_analysis", "in_response_to": message.id}
    )

# MCP agent receives messages
messages = hub.message_broker.receive(mcp_agent)

# MCP agent processes messages
for message in messages:
    print(f"Message from {message.sender.name}: {message.content}")
    print(f"Metadata: {message.metadata}")
```



## Integration with Other Components

### Memory System

The Agent Coordination system integrates with the Memory System to store and retrieve agent state, team information, and message history.

```python
from augment_adam.ai_agent.coordination import CoordinationHub
from augment_adam.ai_agent import MCPAgent, WorkerAgent
from augment_adam.memory import FAISSMemory

# Create a memory
memory = FAISSMemory(path="./data/agent_coordination")

# Create a coordination hub with memory
hub = CoordinationHub(memory=memory)

# Create agents
mcp_agent = MCPAgent(name="MCP Agent", memory=memory)
worker_agent = WorkerAgent(name="Worker Agent", memory=memory)

# Create a team
team = hub.create_team("Problem Solving Team", [mcp_agent, worker_agent])

# Send a message
message_id = hub.send_message(
    sender=mcp_agent,
    recipient=worker_agent,
    content="Please solve this problem.",
    metadata={"problem": "What is the optimal strategy for the Prisoner's Dilemma?"}
)

# The message is stored in memory
message = memory.get(message_id)
print(f"Message: {message}")
```

### Context Engine

The Agent Coordination system integrates with the Context Engine to provide relevant context for agent communication and workflow execution.

```python
from augment_adam.ai_agent.coordination import CoordinationHub
from augment_adam.ai_agent import MCPAgent, WorkerAgent
from augment_adam.context_engine import ContextEngine

# Create a context engine
context_engine = ContextEngine()

# Add documents to the context engine
context_engine.add_document(
    "The Prisoner's Dilemma is a standard example of a game analyzed in game theory "
    "that shows why two completely rational individuals might not cooperate, "
    "even if it appears that it is in their best interests to do so."
)

# Create a coordination hub with context engine
hub = CoordinationHub(context_engine=context_engine)

# Create agents with context engine
mcp_agent = MCPAgent(name="MCP Agent", context_engine=context_engine)
worker_agent = WorkerAgent(name="Worker Agent", context_engine=context_engine)

# Create a team
team = hub.create_team("Problem Solving Team", [mcp_agent, worker_agent])

# Send a message with context
message_id = hub.send_message(
    sender=mcp_agent,
    recipient=worker_agent,
    content="Please analyze the Prisoner's Dilemma.",
    metadata={"context": context_engine.get_context("Prisoner's Dilemma")}
)

# Worker agent receives the message with context
messages = hub.message_broker.receive(worker_agent)
for message in messages:
    print(f"Message: {message.content}")
    print(f"Context: {message.metadata.get('context')}")
```

### Assistant

The Agent Coordination system integrates with the Assistant to provide multi-agent capabilities.

```python
from augment_adam.core import Assistant
from augment_adam.ai_agent.coordination import CoordinationHub
from augment_adam.ai_agent import MCPAgent, WorkerAgent

# Create a coordination hub
hub = CoordinationHub()

# Create agents
mcp_agent = MCPAgent(name="MCP Agent")
worker_agent1 = WorkerAgent(name="Worker Agent 1")
worker_agent2 = WorkerAgent(name="Worker Agent 2")

# Create a team
team = hub.create_team("Problem Solving Team", [mcp_agent, worker_agent1, worker_agent2])

# Create an assistant with the coordination hub
assistant = Assistant(coordination_hub=hub)

# Chat with the assistant
response = assistant.chat("Solve this complex problem: What is the optimal strategy for the Prisoner's Dilemma?")
print(response)
```



## Future Enhancements

- **Agent Coordination Analytics**: Add analytics to track agent coordination performance and effectiveness.
- **More Coordination Patterns**: Implement more sophisticated coordination patterns, such as hierarchical teams, peer-to-peer networks, and market-based coordination.
- **Dynamic Agent Discovery**: Add support for dynamic discovery of agents based on capabilities and availability.
- **Agent Versioning**: Implement versioning for agents to ensure compatibility between different versions.
- **Agent Validation**: Add validation for agents to ensure they meet the requirements for coordination.
- **Message Encryption**: Add encryption for sensitive messages between agents.
- **Message Validation**: Implement validation for messages to ensure they meet the requirements for coordination.
- **Agent Coordination Visualization**: Add visualization tools for agent coordination to help understand and debug coordination patterns.

