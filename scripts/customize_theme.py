#!/usr/bin/env python3
"""
Script to customize the Sphinx theme.
"""

import os
import re
from pathlib import Path

def customize_theme():
    """Customize the Sphinx theme."""
    print("Customizing Sphinx theme...")
    
    # Create custom CSS file
    custom_css = """
/* Custom CSS for Augment Adam documentation */

/* Primary color */
:root {
    --primary-color: #007bff;
    --primary-color-light: #4da3ff;
    --primary-color-dark: #0056b3;
}

/* Links */
a {
    color: var(--primary-color);
}

a:hover {
    color: var(--primary-color-dark);
}

/* Navigation */
.wy-side-nav-search {
    background-color: var(--primary-color);
}

.wy-nav-top {
    background-color: var(--primary-color);
}

/* Code blocks */
.highlight {
    background: #f8f8f8;
}

/* Admonitions */
.admonition.note {
    background-color: #e7f2fa;
}

.admonition.warning {
    background-color: #ffedcc;
}

.admonition.danger {
    background-color: #fadddd;
}

/* Tables */
table.docutils {
    border: 1px solid #e1e4e5;
    border-collapse: collapse;
    margin-bottom: 24px;
}

table.docutils td, table.docutils th {
    border: 1px solid #e1e4e5;
    padding: 8px 16px;
}

table.docutils th {
    background-color: #f0f0f0;
}

/* Responsive design */
@media screen and (max-width: 768px) {
    .wy-nav-content-wrap {
        margin-left: 0;
    }
}
"""
    
    # Create the _static directory if it doesn't exist
    os.makedirs("docs/_static", exist_ok=True)
    
    # Write the custom CSS file
    with open("docs/_static/custom.css", "w") as f:
        f.write(custom_css)
    
    print("  Created docs/_static/custom.css")
    
    # Update conf.py to use the custom CSS file
    with open("docs/conf.py", "r") as f:
        content = f.read()
    
    # Check if html_static_path is already defined
    if "html_static_path = ['_static']" not in content:
        # Add html_static_path
        content = content.replace(
            "# Add any paths that contain custom static files (such as style sheets) here,",
            "# Add any paths that contain custom static files (such as style sheets) here,\n"
            "html_static_path = ['_static']"
        )
    
    # Check if html_css_files is already defined
    if "html_css_files = ['custom.css']" not in content:
        # Add html_css_files
        content = content.replace(
            "html_static_path = ['_static']",
            "html_static_path = ['_static']\n"
            "html_css_files = ['custom.css']"
        )
    
    # Write the updated conf.py
    with open("docs/conf.py", "w") as f:
        f.write(content)
    
    print("  Updated docs/conf.py")

def main():
    """Main function."""
    print("Customizing Sphinx theme...")
    
    # Customize theme
    customize_theme()
    
    print("Done!")

if __name__ == "__main__":
    main()
