
Template API
==========

This document provides reference documentation for the Template API.

Overview
-------

The Template API manages templates for various outputs.

Core Components
-------------

* **TemplateEngine**: The main template engine class
* **Template**: Base class for templates
* **TemplateLoader**: Loads templates
* **TemplateRenderer**: Renders templates

Usage
----

.. code-block:: python

    from augment_adam.utils.templates import TemplateEngine

    # Initialize template engine
    engine = TemplateEngine()

    # Register a template
    engine.register_template("greeting", "Hello, {{ name }}!")

    # Render a template
    result = engine.render("greeting", {"name": "World"})
    print(result)  # "Hello, World!"

    # Register a template from a file
    engine.register_template_file("email", "templates/email.jinja2")

    # Render a template from a file
    result = engine.render("email", {
        "recipient": "John",
        "sender": "Jane",
        "subject": "Hello",
        "body": "This is a test email."
    })
    print(result)

API Reference
-----------

.. automodule:: augment_adam.utils.templates
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/template_engine` - Template Engine documentation
