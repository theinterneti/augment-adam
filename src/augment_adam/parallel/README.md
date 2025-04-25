# Parallel Processing

## Overview

This module provides tools for executing tasks in parallel, with support for thread-based, process-based, and asynchronous execution. It includes features for task parallelization, result synchronization, resource management, task dependencies, and error handling.

## Components

### Base

The base module provides the core interfaces and classes for parallel processing:

- **Task**: Represents a task for parallel processing
- **TaskStatus**: Enum for task status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
- **TaskResult**: Represents the result of a task
- **TaskExecutor**: Base class for task executors
- **ParallelExecutor**: Base class for parallel executors

### Thread

The thread module provides thread-based parallel processing:

- **ThreadPoolExecutor**: Executor for thread-based parallel processing
- **ThreadTask**: Task for thread-based parallel processing

### Process

The process module provides process-based parallel processing:

- **ProcessPoolExecutor**: Executor for process-based parallel processing
- **ProcessTask**: Task for process-based parallel processing

### Async

The async module provides asynchronous parallel processing:

- **AsyncExecutor**: Executor for asynchronous parallel processing
- **AsyncTask**: Task for asynchronous parallel processing

### Workflow

The workflow module provides tools for defining and executing workflows with task dependencies:

- **Workflow**: Represents a workflow with tasks and dependencies
- **WorkflowExecutor**: Executes workflows, respecting task dependencies
- **WorkflowTask**: Task in a workflow
- **TaskDependency**: Dependency between tasks

### Utils

The utils module provides utility functions and classes for parallel processing:

- **ResourceMonitor**: Monitors system resources
- **ResourceThrottler**: Throttles resource usage
- **ResultAggregator**: Aggregates results from parallel tasks
- **ErrorHandler**: Handles errors in parallel execution

## Usage

### Thread-based Parallel Processing

```python
from augment_adam.parallel import ThreadPoolExecutor

# Create executor
executor = ThreadPoolExecutor(max_workers=4)

# Submit a function for execution
task_id = executor.submit_function(lambda x: x * 2, 5)

# Wait for result
result = executor.wait_for_result(task_id)
print(result.value)  # Output: 10

# Apply a function to a list of items in parallel
results = executor.map(lambda x: x * 2, [1, 2, 3, 4, 5])
print([r.value for r in results])  # Output: [2, 4, 6, 8, 10]

# Shutdown executor
executor.shutdown()
```

### Process-based Parallel Processing

```python
from augment_adam.parallel import ProcessPoolExecutor

# Create executor
executor = ProcessPoolExecutor(max_workers=4)

# Submit a function for execution
task_id = executor.submit_function(lambda x: x * 2, 5)

# Wait for result
result = executor.wait_for_result(task_id)
print(result.value)  # Output: 10

# Apply a function to a list of items in parallel
results = executor.map(lambda x: x * 2, [1, 2, 3, 4, 5])
print([r.value for r in results])  # Output: [2, 4, 6, 8, 10]

# Shutdown executor
executor.shutdown()
```

### Asynchronous Parallel Processing

```python
import asyncio
from augment_adam.parallel import AsyncExecutor

# Create executor
executor = AsyncExecutor(max_workers=4)

# Submit a function for execution
task_id = executor.submit_function(lambda x: x * 2, 5)

# Wait for result
result = executor.wait_for_result(task_id)
print(result.value)  # Output: 10

# Submit a coroutine for execution
async def async_double(x):
    await asyncio.sleep(0.1)
    return x * 2

task_id = executor.submit_coroutine(async_double, 5)

# Wait for result
result = executor.wait_for_result(task_id)
print(result.value)  # Output: 10

# Shutdown executor
executor.shutdown()
```

### Workflow with Task Dependencies

```python
from augment_adam.parallel import (
    ThreadPoolExecutor,
    Workflow,
    WorkflowExecutor,
    WorkflowTask,
    DependencyType,
)

# Create tasks
task1 = WorkflowTask(func=lambda: "Task 1")
task2 = WorkflowTask(func=lambda: "Task 2")
task3 = WorkflowTask(func=lambda: "Task 3")

# Create workflow
workflow = Workflow(name="example_workflow")
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(task3)

# Add dependencies
workflow.add_dependency(task2.id, task1.id, DependencyType.SUCCESS)  # Task 2 depends on Task 1
workflow.add_dependency(task3.id, task2.id, DependencyType.SUCCESS)  # Task 3 depends on Task 2

# Create executor
thread_executor = ThreadPoolExecutor(max_workers=4)
workflow_executor = WorkflowExecutor(name="example_workflow_executor", executor=thread_executor)

# Add workflow to executor
workflow_id = workflow_executor.add_workflow(workflow)

# Execute workflow
results = workflow_executor.execute_workflow(workflow_id)

# Print results
for task_id, result in results.items():
    print(f"Task {task_id}: {result.value}")
```

### Resource Management

```python
from augment_adam.parallel import ThreadPoolExecutor
from augment_adam.parallel.utils import ResourceMonitor, ResourceThrottler

# Create resource monitor
monitor = ResourceMonitor(interval=1.0, history_size=60)
monitor.start()

# Create resource throttler
throttler = ResourceThrottler(
    monitor=monitor,
    cpu_threshold=0.8,
    memory_threshold=0.8,
    disk_threshold=0.8,
    min_concurrency=1,
    max_concurrency=10
)

# Get current resource usage
usage = monitor.get_current_usage()
print(f"CPU: {usage['cpu']:.2f}, Memory: {usage['memory']:.2f}, Disk: {usage['disk']:.2f}")

# Get average CPU usage over the last 5 checks
avg_cpu = monitor.get_average_usage("cpu", window=5)
print(f"Average CPU: {avg_cpu:.2f}")

# Update concurrency based on resource usage
concurrency = throttler.update_concurrency()
print(f"Concurrency: {concurrency}")

# Create executor with throttled concurrency
executor = ThreadPoolExecutor(max_workers=concurrency)

# Stop monitor
monitor.stop()
```

### Result Aggregation

```python
from augment_adam.parallel import ThreadPoolExecutor
from augment_adam.parallel.utils import ResultAggregator

# Create executor
executor = ThreadPoolExecutor(max_workers=4)

# Submit tasks
task_ids = [
    executor.submit_function(lambda x: x, i)
    for i in range(1, 6)
]

# Wait for results
results = executor.wait_for_all(task_ids)

# Create aggregator
aggregator = ResultAggregator(
    name="sum_aggregator",
    aggregation_function=lambda values: sum(values)
)

# Aggregate results
total = aggregator.aggregate_dict(results)
print(f"Total: {total}")  # Output: 15

# Shutdown executor
executor.shutdown()
```

### Error Handling

```python
from augment_adam.parallel import ThreadPoolExecutor
from augment_adam.parallel.utils import ErrorHandler, ErrorStrategy

# Create executor
executor = ThreadPoolExecutor(max_workers=4)

# Create error handler
error_handler = ErrorHandler(
    name="retry_handler",
    strategy=ErrorStrategy.RETRY,
    max_retries=3,
    retry_delay=1.0
)

# Submit a function that might fail
def might_fail(x):
    if x % 2 == 0:
        raise ValueError("Even number")
    return x

task_id = executor.submit_function(might_fail, 2)

# Wait for result
result = executor.wait_for_result(task_id)

# Handle error
task = executor.tasks[task_id]
continue_execution = error_handler.handle_error(task, result)

# Shutdown executor
executor.shutdown()
```

## TODOs

- Add support for distributed processing across multiple machines (Issue #10)
- Implement adaptive resource allocation based on system load (Issue #10)
- Add monitoring and visualization of parallel task execution (Issue #10)
- Implement more sophisticated scheduling algorithms (Issue #10)
- Add support for GPU acceleration (Issue #10)
- Add support for task dependencies in executors (Issue #10)
- Implement task validation (Issue #10)
- Add support for executor validation (Issue #10)
- Implement executor analytics (Issue #10)
- Add support for result validation (Issue #10)
- Implement result analytics (Issue #10)
- Add support for more error handling strategies (Issue #10)
- Implement error analytics (Issue #10)
