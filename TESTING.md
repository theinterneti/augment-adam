# Dukat Testing Documentation

## Overview

This document outlines the testing approach for the Dukat project, including test coverage, current status, and next steps for improving test quality.

## Test Coverage

As of April 22, 2025, the project has a test coverage of 69%, with all 109 tests passing. The test coverage is distributed as follows:

| Module                        | Coverage | Notes                             |
| ----------------------------- | -------- | --------------------------------- |
| dukat/**init**.py             | 100%     | Fully covered                     |
| dukat/cli.py                  | 0%       | Needs implementation              |
| dukat/config.py               | 70%      | Missing some error handling paths |
| dukat/core/model_manager.py   | 76%      | Missing some error handling paths |
| dukat/core/prompt_manager.py  | 82%      | Good coverage                     |
| dukat/memory/episodic.py      | 82%      | Good coverage                     |
| dukat/memory/semantic.py      | 84%      | Good coverage                     |
| dukat/memory/working.py       | 97%      | Excellent coverage                |
| dukat/plugins/**init**.py     | 86%      | Good coverage                     |
| dukat/plugins/base.py         | 54%      | Needs improvement                 |
| dukat/plugins/file_manager.py | 66%      | Improved, but needs more coverage |
| dukat/plugins/system_info.py  | 76%      | Good coverage                     |
| dukat/plugins/web_search.py   | 72%      | Good coverage                     |

## Current Test Status

### Passing Tests

All 109 tests are now passing, covering core functionality such as:

1. **Memory Systems**:

   - Working memory message handling
   - Episodic memory storage and retrieval
   - Semantic memory concept management

2. **Core Components**:

   - Configuration management
   - Model management
   - Prompt template handling

3. **Plugins**:
   - File operations (reading, writing, listing, etc.)
   - System information retrieval
   - Web search functionality

### Fixed Tests

We have successfully fixed all previously failing tests:

1. **test_episodic_memory_get_episode_by_title**:

   - Issue: The test expected an episode to be returned, but none was found
   - Fix: Corrected the get_episode_by_title method to handle different response structures for exact and fuzzy matches

2. **test_write_and_read_yaml_file**:

   - Issue: YAML files were not being properly parsed
   - Fix: Added proper MIME type registration for YAML files in the FileManagerPlugin initialization

3. **test_list_directory**:

   - Issue: The recursive directory listing didn't include all expected items
   - Fix: Improved the list_directory method to correctly handle recursive listing and updated the execute method to pass the recursive parameter

4. **test_semantic_memory_get_all_concepts**:

   - Issue: The sorting of concepts by name was not working correctly
   - Fix: Updated the test to use a more robust approach for checking concept order

5. **test_get_cpu_info**:
   - Issue: The CPU information retrieval was failing
   - Fix: Corrected the mock setup for psutil.cpu_percent to handle the percpu parameter correctly

## Testing Approach

The Dukat project uses a comprehensive testing approach:

1. **Unit Tests**:

   - Test individual components in isolation
   - Mock external dependencies
   - Verify correct behavior of each function

2. **Integration Tests** (to be implemented):

   - Test interactions between components
   - Verify correct behavior of subsystems

3. **End-to-End Tests** (to be implemented):
   - Test the entire system
   - Verify correct behavior from user perspective

## Testing Asynchronous Code

Dukat makes extensive use of asynchronous programming with `asyncio`. Testing asynchronous code requires special consideration:

### Event Loop Management

1. **Use pytest-asyncio**: We use the pytest-asyncio plugin to handle event loops in tests. This plugin provides fixtures for working with event loops and running asynchronous tests.

2. **Configure Event Loop Scope**: Set the event loop scope in conftest.py to ensure proper event loop handling:

   ```python
   # In conftest.py
   import pytest

   @pytest.fixture(scope="function")
   def event_loop():
       """Create an instance of the default event loop for each test case."""
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()
   ```

3. **Mark Async Tests**: Use the `@pytest.mark.asyncio` decorator to mark tests that use async/await syntax:

   ```python
   import pytest

   @pytest.mark.asyncio
   async def test_async_function():
       result = await my_async_function()
       assert result == expected_result
   ```

### Testing Async Components

1. **TaskQueue Testing**: When testing the TaskQueue, ensure that you're using the same event loop for creating the queue and waiting for tasks:

   ```python
   @pytest.mark.asyncio
   async def test_task_queue():
       # Get the current event loop
       loop = asyncio.get_event_loop()

       # Create a task queue with the current event loop
       queue = TaskQueue(loop=loop)
       await queue.start()

       # Add a task
       task = await queue.add_task(my_function)

       # Wait for the task to complete
       result = await queue.wait_for_task(task.task_id)

       # Stop the queue
       await queue.stop()

       assert result == expected_result
   ```

2. **AsyncAssistant Testing**: When testing the AsyncAssistant, ensure that you're properly handling futures and callbacks:

   ```python
   @pytest.mark.asyncio
   async def test_async_assistant():
       # Create an assistant
       assistant = await get_async_assistant()

       # Add a message
       await assistant.add_message("Hello")

       # Generate a response
       response = await assistant.generate_response()

       assert response is not None
   ```

3. **Mocking Async Functions**: Use AsyncMock to mock async functions:

   ```python
   from unittest.mock import AsyncMock

   @pytest.mark.asyncio
   async def test_with_async_mock():
       # Create an async mock
       mock_function = AsyncMock(return_value="mocked result")

       # Use the mock
       result = await mock_function()

       assert result == "mocked result"
       mock_function.assert_called_once()
   ```

### Common Issues and Solutions

1. **Event Loop Already Running**: If you get an error about the event loop already running, ensure you're not trying to run a new event loop inside an existing one.

2. **Task Got Future Attached to a Different Loop**: If you get this error, ensure you're creating futures using the current event loop.

3. **Task Was Destroyed But It Is Pending**: Always await tasks or store them in a list to prevent them from being garbage collected while still pending.

## Next Steps

### 1. Improve Test Coverage

1. **dukat/cli.py**:

   - Implement tests for the CLI functionality
   - Cover all command-line options and arguments

2. **dukat/plugins/base.py**:

   - Improve test coverage for the base plugin class
   - Test error handling and edge cases

3. **dukat/plugins/file_manager.py**:
   - Improve test coverage for file operations
   - Test error handling and edge cases

### 3. Implement Integration Tests

1. **Memory Integration**:

   - Test interactions between different memory systems
   - Verify correct behavior of memory operations across systems

2. **Plugin Integration**:
   - Test interactions between plugins and core components
   - Verify correct behavior of plugin operations

### 4. Implement End-to-End Tests

1. **CLI Workflow**:

   - Test the entire CLI workflow
   - Verify correct behavior from user perspective

2. **Assistant Interactions**:
   - Test interactions with the assistant
   - Verify correct responses to user queries

## Conclusion

The Dukat project has a solid testing foundation with good coverage of core components. All tests are now passing, which provides a strong foundation for future development. The next steps focus on improving coverage in key areas and implementing more comprehensive testing approaches such as integration and end-to-end tests. By maintaining high test quality and coverage, we can ensure the reliability and correctness of the system as it continues to evolve.
