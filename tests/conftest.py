"""
Global test configuration for Dukat.

This module provides fixtures and configuration for all tests.
"""

import asyncio
import pytest


# Configure pytest-asyncio to use function scope for event loops
# This addresses the warning: "The configuration option 'asyncio_default_fixture_loop_scope' is unset"
pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case.

    This fixture is used by pytest-asyncio to create a new event loop for each test.
    Setting the scope to 'function' ensures that each test gets a fresh event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Clean up pending tasks
    pending_tasks = asyncio.all_tasks(loop)
    for task in pending_tasks:
        task.cancel()
    # Run the event loop until all tasks are done
    if pending_tasks:
        loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
    loop.close()


# Configure pytest-asyncio to use function scope for event loops
def pytest_configure(config):
    """Configure pytest.

    This function is called by pytest to configure the test session.
    We use it to set the default fixture loop scope for pytest-asyncio.
    """
    config.option.asyncio_default_fixture_loop_scope = "function"
