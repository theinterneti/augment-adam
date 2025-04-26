# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'Augment Adam'
copyright = '2023-2024, Augment Code'
author = 'Augment Code Team'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',  # Built-in Sphinx extension for viewing source code
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.mermaid',
    'sphinx_copybutton',    # Add copy button to code blocks
    'sphinx_design',        # Enhanced design components
    'sphinx_togglebutton',  # Add toggle buttons
    'sphinx_tabs.tabs'      # Add tabbed content
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Enable Markdown support
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Main document
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_static_path = ['_static']

# Mermaid diagrams
mermaid_version = "10.4.0"
