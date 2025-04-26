
Template Engine
===============

This document provides information about the template engine.

.. include:: ../../docs/architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_

Template Engine Architecture
----------------------------

.. mermaid::

    graph TD
        Data[Data] --> |Input| TemplateEngine[Template Engine]
        TemplateEngine --> |Loads| TemplateLoader[Template Loader]
        TemplateLoader --> |Loads| Template[Template]
        
        Template --> |Parse| TemplateParser[Template Parser]
        TemplateParser --> |Create| AST[Abstract Syntax Tree]
        
        Data --> |Provide| ContextBuilder[Context Builder]
        ContextBuilder --> |Build| RenderContext[Render Context]
        
        AST --> |Render| TemplateRenderer[Template Renderer]
        RenderContext --> |Provide| TemplateRenderer
        
        TemplateRenderer --> |Output| RenderedOutput[Rendered Output]
        
        subgraph Template Engine
            TemplateLoader
            TemplateParser
            ContextBuilder
            TemplateRenderer
        end

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/template` - Template API reference
