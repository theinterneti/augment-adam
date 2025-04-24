# Parallel Execution

The parallel execution system allows running multiple tasks concurrently with dependency management, resource allocation, and circuit breaker patterns for resilience.

## Overview

The parallel execution system provides the following capabilities:

- Execute multiple tasks in parallel with configurable concurrency limits
- Define dependencies between tasks to ensure proper execution order
- Allocate and manage resources for tasks (CPU, memory, network, etc.)
- Track progress of task execution
- Implement circuit breakers to prevent cascading failures
- Handle errors and retries

## Components

### ParallelTaskExecutor

The main class for parallel task execution.

```python
from dukat.core.parallel_executor import ParallelTaskExecutor

# Create an executor with a maximum concurrency of 3
executor = ParallelTaskExecutor(max_concurrency=3)

# Add tasks to the executor
await executor.add_task(task1)
await executor.add_task(task2, dependencies=["task1"])
await executor.add_task(task3, resource_requirements=[
    ResourceRequirement(ResourceType.CPU, amount=0.5)
])

# Execute all tasks
results = await executor.execute_all()
```

### ResourcePool

Manages resource allocation for tasks.

```python
from dukat.core.parallel_executor import ResourcePool, ResourceRequirement, ResourceType

# Create a resource pool
pool = ResourcePool()

# Allocate resources
requirements = [
    ResourceRequirement(ResourceType.CPU, amount=0.5),
    ResourceRequirement(ResourceType.MEMORY, amount=0.3),
]

allocated = await pool.allocate("task1", requirements)

# Release resources
await pool.release("task1")
```

### DependencyGraph

Manages dependencies between tasks.

```python
from dukat.core.parallel_executor import DependencyGraph

# Create a dependency graph
graph = DependencyGraph()

# Add dependencies
graph.add_dependency("task2", "task1")  # task2 depends on task1
graph.add_dependency("task3", "task1")  # task3 depends on task1
graph.add_dependency("task4", "task2")  # task4 depends on task2
graph.add_dependency("task4", "task3")  # task4 depends on task3

# Get tasks that are ready to execute
ready_tasks = graph.get_ready_tasks(completed_tasks={"task1"})
# ready_tasks = {"task2", "task3"}
```

### CircuitBreaker

Implements the circuit breaker pattern to prevent cascading failures.

```python
from dukat.core.circuit_breaker import CircuitBreaker, CircuitBreakerState

# Create a circuit breaker
breaker = CircuitBreaker(
    name="api_service",
    failure_threshold=5,
    timeout_seconds=60.0,
)

# Use the circuit breaker
if breaker.allow_request():
    try:
        # Make the request
        result = await make_api_request()
        
        # Record success
        breaker.success()
        
        return result
    except Exception as e:
        # Record failure
        breaker.failure(e)
        
        # Re-raise the exception
        raise
else:
    # Circuit is open, fail fast
    raise CircuitBreakerError("Circuit breaker is open")
```

## Integration with AsyncAssistant

The AsyncAssistant class provides methods to use the parallel execution system:

```python
from dukat.core.async_assistant import get_async_assistant

# Create an async assistant with parallel execution capabilities
assistant = await get_async_assistant(
    model_name="llama3:8b",
    max_parallel_tasks=3,
)

# Execute tasks in parallel
tasks = [
    {
        "func": task_1,
        "task_id": "task_1",
        "description": "Task 1",
    },
    {
        "func": task_2,
        "task_id": "task_2",
        "description": "Task 2",
        "dependencies": ["task_1"],  # This task depends on task_1
    },
]

results = await assistant.execute_tasks_in_parallel(tasks)
```

## Examples

See the `examples/async_processing.py` file for a complete example of using the parallel execution system.

## Best Practices

1. **Define Dependencies Carefully**: Ensure there are no cycles in the dependency graph.
2. **Resource Requirements**: Specify resource requirements for tasks to avoid resource contention.
3. **Circuit Breakers**: Use circuit breakers for external dependencies to prevent cascading failures.
4. **Progress Tracking**: Use progress trackers to monitor task execution.
5. **Error Handling**: Implement proper error handling and retry mechanisms.
