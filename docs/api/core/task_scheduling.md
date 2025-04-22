# Task Scheduling

The task scheduling system allows scheduling tasks to run at specific times or periodically.

## Overview

The task scheduling system provides the following capabilities:

- Schedule tasks to run at a specific time
- Schedule tasks to run periodically with a configurable interval
- Cancel scheduled tasks
- Get information about scheduled tasks
- Limit the number of runs for periodic tasks

## Components

### TaskScheduler

The main class for task scheduling.

```python
from dukat.core.task_scheduler import TaskScheduler
from datetime import datetime, timedelta

# Create a scheduler
scheduler = TaskScheduler()

# Schedule a one-time task
task_id = await scheduler.schedule_task(
    func=my_function,
    args=[arg1, arg2],
    kwargs={"key": "value"},
    schedule_time=datetime.now() + timedelta(minutes=5),
    description="Run my_function in 5 minutes",
)

# Schedule a periodic task
task_id = await scheduler.schedule_task(
    func=my_function,
    args=[arg1, arg2],
    kwargs={"key": "value"},
    schedule_time=datetime.now(),
    interval=timedelta(minutes=10),
    max_runs=5,
    description="Run my_function every 10 minutes, 5 times",
)

# Cancel a scheduled task
cancelled = await scheduler.cancel_task(task_id)

# Get information about a scheduled task
task_info = await scheduler.get_task(task_id)

# Get information about all scheduled tasks
all_tasks = await scheduler.get_all_tasks()
```

### ScheduledTask

Represents a scheduled task.

```python
from dukat.core.task_scheduler import ScheduledTask
from datetime import datetime, timedelta

# Create a one-time task
task = ScheduledTask(
    func=my_function,
    task_id="task1",
    schedule_time=datetime.now() + timedelta(minutes=5),
)

# Create a periodic task
task = ScheduledTask(
    func=my_function,
    task_id="task2",
    schedule_time=datetime.now(),
    interval=timedelta(minutes=10),
    max_runs=5,
)
```

## Integration with AsyncAssistant

The AsyncAssistant class provides methods to use the task scheduling system:

```python
from dukat.core.async_assistant import get_async_assistant
from datetime import datetime, timedelta

# Create an async assistant
assistant = await get_async_assistant(
    model_name="llama3:8b",
)

# Schedule a periodic task
periodic_task_id = await assistant.schedule_periodic_task(
    func=my_function,
    interval=timedelta(minutes=10),
    args=[arg1, arg2],
    kwargs={"key": "value"},
    max_runs=5,
    description="Run my_function every 10 minutes, 5 times",
)

# Schedule a one-time task
scheduled_task_id = await assistant.schedule_task_at_time(
    func=my_function,
    schedule_time=datetime.now() + timedelta(minutes=5),
    args=[arg1, arg2],
    kwargs={"key": "value"},
    description="Run my_function in 5 minutes",
)

# Cancel a scheduled task
cancelled = await assistant.cancel_scheduled_task(scheduled_task_id)
```

## Examples

See the `examples/async_processing.py` file for a complete example of using the task scheduling system.

## Best Practices

1. **Task IDs**: Use unique task IDs to avoid conflicts.
2. **Error Handling**: Implement proper error handling in scheduled tasks.
3. **Resource Usage**: Be mindful of resource usage when scheduling periodic tasks.
4. **Cancellation**: Always cancel tasks that are no longer needed.
5. **Monitoring**: Monitor scheduled tasks to ensure they are running as expected.
