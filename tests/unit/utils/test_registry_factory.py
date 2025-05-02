"""
Unit tests for augment_adam.utils.tagging.registry_factory.

This module tests the tag registry factory for creating and managing tag registries.
"""

import unittest
import pytest
import threading
from concurrent.futures import ThreadPoolExecutor

from augment_adam.utils.tagging.core import (
    Tag,
    TagCategory,
    TagRegistry,
)
from augment_adam.utils.tagging.registry_factory import (
    TagRegistryFactory,
    get_registry_factory,
    get_registry,
    IsolatedTagRegistry,
)

# Import test utilities
from tests.utils import (
    skip_if_no_module,
    timed,
    assert_dict_subset,
    assert_lists_equal_unordered,
    assert_approx_equal,
)


@pytest.mark.unit
class TestTagRegistryFactory(unittest.TestCase):
    """Test cases for the TagRegistryFactory class."""

    def setUp(self):
        """Set up the test case."""
        # Initialize objects for testing
        self.factory = TagRegistryFactory()

    def tearDown(self):
        """Tear down the test case."""
        # Clean up resources
        if hasattr(self.factory, '_test_registry'):
            self.factory._test_mode = False
            self.factory._test_registry = None

    def test_init(self):
        """Test TagRegistryFactory initialization."""
        # Check that the factory was initialized correctly
        self.assertIsInstance(self.factory._default_registry, TagRegistry)
        self.assertFalse(self.factory._test_mode)
        self.assertIsNone(self.factory._test_registry)

    def test_get_registry(self):
        """Test the get_registry method."""
        # Get the default registry
        registry = self.factory.get_registry()

        # Check that the default registry was returned
        self.assertEqual(self.factory._default_registry, registry)

    def test_create_thread_local_registry(self):
        """Test the create_thread_local_registry method."""
        # Create a thread-local registry
        registry = self.factory.create_thread_local_registry()

        # Check that a new registry was created
        self.assertIsInstance(registry, TagRegistry)
        self.assertNotEqual(self.factory._default_registry, registry)

        # Check that the thread-local registry is returned by get_registry
        self.assertEqual(registry, self.factory.get_registry())

        # Clear the thread-local registry
        self.factory.clear_thread_local_registry()

        # Check that the default registry is returned by get_registry
        self.assertEqual(self.factory._default_registry, self.factory.get_registry())

    def test_enter_test_mode(self):
        """Test the enter_test_mode method."""
        # Enter test mode
        registry = self.factory.enter_test_mode()

        # Check that test mode was entered
        self.assertTrue(self.factory._test_mode)
        self.assertIsInstance(self.factory._test_registry, TagRegistry)
        self.assertEqual(registry, self.factory._test_registry)

        # Check that the test registry is returned by get_registry
        self.assertEqual(registry, self.factory.get_registry())

        # Exit test mode
        self.factory.exit_test_mode()

        # Check that test mode was exited
        self.assertFalse(self.factory._test_mode)
        self.assertIsNone(self.factory._test_registry)

        # Check that the default registry is returned by get_registry
        self.assertEqual(self.factory._default_registry, self.factory.get_registry())

    def test_thread_safety(self):
        """Test thread safety of the factory."""
        # Create a function to run in a thread
        def thread_func():
            # Create a thread-local registry
            registry = self.factory.create_thread_local_registry()

            # Create a tag in the thread-local registry
            tag = Tag(name="thread_tag", category=TagCategory.UTILITY)
            registry.tags["thread_tag"] = tag

            # Check that the tag exists in the thread-local registry
            self.assertIn("thread_tag", registry.tags)

            # Return the registry
            return registry

        # Run the function in multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(thread_func) for _ in range(5)]
            registries = [future.result() for future in futures]

        # Check that each thread got a different registry
        for i in range(len(registries)):
            for j in range(i + 1, len(registries)):
                self.assertNotEqual(registries[i], registries[j])

        # Check that the default registry doesn't have the thread-local tags
        self.assertNotIn("thread_tag", self.factory._default_registry.tags)


@pytest.mark.unit
class TestRegistryFactoryFunctions(unittest.TestCase):
    """Test cases for the registry factory functions."""

    def setUp(self):
        """Set up the test case."""
        # Initialize objects for testing
        pass

    def tearDown(self):
        """Tear down the test case."""
        # Clean up resources
        factory = get_registry_factory()
        if hasattr(factory, '_test_registry'):
            factory._test_mode = False
            factory._test_registry = None

    def test_get_registry_factory(self):
        """Test the get_registry_factory function."""
        # Get the registry factory
        factory = get_registry_factory()

        # Check that a TagRegistryFactory was returned
        self.assertIsInstance(factory, TagRegistryFactory)

        # Check that the same factory is returned on subsequent calls
        factory2 = get_registry_factory()
        self.assertIs(factory, factory2)

    def test_get_registry(self):
        """Test the get_registry function."""
        # Get the registry
        registry = get_registry()

        # Check that a TagRegistry was returned
        self.assertIsInstance(registry, TagRegistry)

        # Check that the same registry is returned by the factory
        factory = get_registry_factory()
        self.assertIs(registry, factory.get_registry())


@pytest.mark.unit
class TestIsolatedTagRegistry(unittest.TestCase):
    """Test cases for the IsolatedTagRegistry class."""

    def setUp(self):
        """Set up the test case."""
        # Initialize objects for testing
        self.factory = get_registry_factory()

    def tearDown(self):
        """Tear down the test case."""
        # Clean up resources
        if hasattr(self.factory, '_test_registry'):
            self.factory._test_mode = False
            self.factory._test_registry = None

    def test_isolated_registry(self):
        """Test the IsolatedTagRegistry context manager."""
        # Get the default registry
        default_registry = get_registry()

        # Create a tag in the default registry with a unique name
        tag_name = f"default_tag_{id(self)}"
        default_registry.create_tag(tag_name, TagCategory.UTILITY)

        # Use the IsolatedTagRegistry context manager
        with IsolatedTagRegistry() as isolated_registry:
            # Check that a different registry was returned
            self.assertIsInstance(isolated_registry, TagRegistry)
            self.assertNotEqual(default_registry, isolated_registry)

            # Check that the isolated registry is returned by get_registry
            self.assertEqual(isolated_registry, get_registry())

            # Create a tag in the isolated registry with a unique name
            isolated_tag_name = f"isolated_tag_{id(self)}"
            isolated_registry.create_tag(isolated_tag_name, TagCategory.UTILITY)

            # Check that the tag exists in the isolated registry
            self.assertIn(isolated_tag_name, isolated_registry.tags)

            # Check that the tag doesn't exist in the default registry
            self.assertNotIn(isolated_tag_name, default_registry.tags)

        # Check that the default registry is returned by get_registry after exiting the context
        self.assertEqual(default_registry, get_registry())

        # Check that the isolated tag doesn't exist in the default registry
        self.assertNotIn(isolated_tag_name, default_registry.tags)

    def test_thread_local_isolated_registry(self):
        """Test the IsolatedTagRegistry context manager with thread_local=True."""
        # Get the default registry
        default_registry = get_registry()

        # Create a tag in the default registry with a unique name
        tag_name = f"default_tag_{id(self)}"
        default_registry.create_tag(tag_name, TagCategory.UTILITY)

        # Use the IsolatedTagRegistry context manager with thread_local=True
        with IsolatedTagRegistry(thread_local=True) as isolated_registry:
            # Check that a different registry was returned
            self.assertIsInstance(isolated_registry, TagRegistry)
            self.assertNotEqual(default_registry, isolated_registry)

            # Check that the isolated registry is returned by get_registry
            self.assertEqual(isolated_registry, get_registry())

            # Create a tag in the isolated registry with a unique name
            isolated_tag_name = f"thread_local_tag_{id(self)}"
            isolated_registry.create_tag(isolated_tag_name, TagCategory.UTILITY)

            # Check that the tag exists in the isolated registry
            self.assertIn(isolated_tag_name, isolated_registry.tags)

            # Check that the tag doesn't exist in the default registry
            self.assertNotIn(isolated_tag_name, default_registry.tags)

        # Check that the default registry is returned by get_registry after exiting the context
        self.assertEqual(default_registry, get_registry())

        # Check that the isolated tag doesn't exist in the default registry
        self.assertNotIn(isolated_tag_name, default_registry.tags)


if __name__ == "__main__":
    unittest.main()
