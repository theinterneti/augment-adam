"""
Testing Framework.

This module provides a comprehensive testing framework for the project,
including unit tests, integration tests, end-to-end tests, and CI/CD setup.

TODO(Issue #13): Add property-based testing
TODO(Issue #13): Implement mutation testing
TODO(Issue #13): Add performance testing
"""

from augment_adam.testing.fixtures import (
    MemoryFixture,
    ModelFixture,
    AgentFixture,
    ContextFixture,
    PluginFixture,
)

from augment_adam.testing.utils import (
    TestCase,
    TestSuite,
    TestResult,
    TestRunner,
    TestLoader,
    TestReporter,
)

from augment_adam.testing.runners import (
    UnitTestRunner,
    IntegrationTestRunner,
    E2ETestRunner,
    ParallelTestRunner,
)

from augment_adam.testing.coverage import (
    CoverageReporter,
    CoverageConfig,
)

__all__ = [
    # Fixtures
    "MemoryFixture",
    "ModelFixture",
    "AgentFixture",
    "ContextFixture",
    "PluginFixture",
    
    # Utils
    "TestCase",
    "TestSuite",
    "TestResult",
    "TestRunner",
    "TestLoader",
    "TestReporter",
    
    # Runners
    "UnitTestRunner",
    "IntegrationTestRunner",
    "E2ETestRunner",
    "ParallelTestRunner",
    
    # Coverage
    "CoverageReporter",
    "CoverageConfig",
]
