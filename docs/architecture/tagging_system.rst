Tagging System
=============

.. include:: TAGGING_SYSTEM.md
   :parser: myst_parser.sphinx_

Thread Safety
------------

The tagging system is designed to be thread-safe, with features to handle concurrent tag creation and access:

- The ``force`` parameter in ``create_tag`` allows for safe retrieval of existing tags
- The ``safe_tag`` decorator handles race conditions in hierarchical tag creation
- Thread-local registries can be used for isolation
- The ``IsolatedTagRegistry`` context manager provides test isolation

Testing with Tags
----------------

For testing, use the ``IsolatedTagRegistry`` context manager to create an isolated tag registry:

.. code-block:: python

   from augment_adam.testing.utils.tag_utils import IsolatedTagRegistry

   def test_something():
       with IsolatedTagRegistry():
           # Create and use tags without affecting the global registry
           tag = create_tag("test_tag", TagCategory.TEST)
