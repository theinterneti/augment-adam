# Asynchronous Programming and Event Loops

This document provides guidance on working with asynchronous code and event loops in the Dukat project.

## Overview

Dukat makes extensive use of asynchronous programming with `asyncio` to provide non-blocking operations. Understanding how event loops work is essential for developing and testing asynchronous code.

## Event Loops

An event loop is the core of every asyncio application. It runs asynchronous tasks and callbacks, performs network IO operations, and runs subprocesses.

### Key Concepts

1. **Event Loop**: The central execution mechanism that manages and distributes the execution of different tasks.
2. **Tasks**: Units of work that are scheduled to run on the event loop.
3. **Futures**: Objects that represent the result of work that has not yet completed.
4. **Coroutines**: Special functions that can be paused and resumed, allowing other code to run while waiting for I/O operations.

## Working with Event Loops in Dukat

### Getting the Current Event Loop

Always use `asyncio.get_event_loop()` to get the current event loop:

```python
import asyncio

async def my_function():
    # Get the current event loop
    loop = asyncio.get_event_loop()
    
    # Use the loop to create futures, tasks, etc.
    future = loop.create_future()
```

### Creating Futures

When creating futures, always use the current event loop:

```python
# Correct way
loop = asyncio.get_event_loop()
future = loop.create_future()

# Avoid this
future = asyncio.Future()  # This might use a different loop
```

### Transferring Results Between Event Loops

When working with futures from different event loops, use callbacks to transfer results:

```python
# Create a new future in the current event loop
current_loop = asyncio.get_event_loop()
new_future = current_loop.create_future()

# Set up a callback to transfer the result
def done_callback(fut):
    try:
        if fut.cancelled():
            new_future.cancel()
        elif fut.exception() is not None:
            new_future.set_exception(fut.exception())
        else:
            new_future.set_result(fut.result())
    except Exception as e:
        if not new_future.done():
            new_future.set_exception(e)

# Add the callback to the original future
original_future.add_done_callback(done_callback)

# Wait for the new future
result = await new_future
```

## Common Patterns

### Task Queue

The `TaskQueue` class in Dukat manages a queue of tasks that are executed asynchronously. It uses the event loop to create futures and tasks:

```python
from augment_adam.core.task_queue import TaskQueue

# Create a task queue with the current event loop
loop = asyncio.get_event_loop()
queue = TaskQueue(max_workers=5, loop=loop)

# Start the queue
await queue.start()

# Add a task
task = await queue.add_task(
    func=my_function,
    args=[arg1, arg2],
)

# Wait for the task to complete
result = await queue.wait_for_task(task.task_id)
```

### AsyncAssistant

The `AsyncAssistant` class integrates with the task queue system and uses the event loop to manage asynchronous operations:

```python
from augment_adam.core.async_assistant import get_async_assistant

# Get an async assistant (uses the current event loop)
assistant = await get_async_assistant(
    model_name="llama3:8b",
)

# Generate a response asynchronously
response = await assistant.generate_response(
    message="Hello, how are you?",
)
```

## Best Practices

1. **Always Use the Current Event Loop**: Get the current event loop using `asyncio.get_event_loop()` rather than creating a new one.

2. **Pass the Event Loop Explicitly**: When creating objects that need an event loop, pass it explicitly as a parameter.

3. **Handle Event Loop Differences**: When working with futures or tasks from different event loops, use callbacks to transfer results.

4. **Avoid Blocking Operations**: Don't use blocking operations in asynchronous code. Use `loop.run_in_executor()` for CPU-bound tasks.

5. **Clean Up Resources**: Always clean up resources when they're no longer needed, especially when stopping event loops.

6. **Error Handling**: Implement proper error handling for asynchronous operations, including timeouts and cancellation.

## Testing Asynchronous Code

Testing asynchronous code requires special consideration. See the [Testing Asynchronous Code](../../TESTING.md#testing-asynchronous-code) section in the testing documentation for guidance.

## Common Issues and Solutions

### Issue: "Task got Future attached to a different loop"

This error occurs when a future created in one event loop is used in a different event loop.

**Solution**: Always create futures using the current event loop, and use callbacks to transfer results between event loops.

### Issue: "This event loop is already running"

This error occurs when trying to run an event loop that's already running.

**Solution**: Use `asyncio.create_task()` to schedule coroutines on the running event loop instead of trying to run a new one.

### Issue: "Task was destroyed but it is pending"

This warning occurs when a task is garbage collected while it's still pending.

**Solution**: Always await tasks or store them in a list to prevent them from being garbage collected.

## References

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Dukat Task Queue Documentation](task_scheduling.md)
- [Dukat AsyncAssistant Documentation](../core.md#asyncassistant)
