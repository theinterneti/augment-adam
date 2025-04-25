"""
Base classes for documentation builders.

This module provides the base classes for documentation builders, which create
documentation files in various formats.
"""

import os
import re
import shutil
import markdown
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.builder")
class DocBuilder(ABC):
    """
    Base class for documentation builders.
    
    This class defines the interface for documentation builders, which create
    documentation files in various formats.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template_dir: The directory containing templates.
        metadata: Additional metadata for the builder.
    
    TODO(Issue #12): Add support for documentation versioning
    TODO(Issue #12): Implement documentation analytics
    """
    
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the documentation builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
        """
        self.output_dir = output_dir
        self.template_dir = template_dir
        self.metadata = metadata or {}
    
    @abstractmethod
    def build(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Build documentation from data.
        
        Args:
            data: The documentation data to build from.
            output_file: The file to save the documentation to.
        """
        pass
    
    @abstractmethod
    def build_all(self, data_list: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Build documentation for multiple data items.
        
        Args:
            data_list: The list of documentation data to build from.
            output_dir: The directory to save the documentation to.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the builder.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the builder.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("docs.builder")
class MarkdownBuilder(DocBuilder):
    """
    Builder for Markdown documentation.
    
    This class builds documentation in Markdown format, which is a lightweight
    markup language that is easy to read and write.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template_dir: The directory containing templates.
        metadata: Additional metadata for the builder.
        template: The template to use for generating documentation.
    
    TODO(Issue #12): Add support for Markdown extensions
    TODO(Issue #12): Implement Markdown analytics
    """
    
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template: Optional[Any] = None
    ) -> None:
        """
        Initialize the Markdown builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            template: The template to use for generating documentation.
        """
        super().__init__(output_dir, template_dir, metadata)
        self.template = template
    
    def build(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Build Markdown documentation from data.
        
        Args:
            data: The documentation data to build from.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Render documentation using template
        if self.template is not None:
            content = self.template.render(data)
        else:
            # Default rendering
            content = self._default_render(data)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(content)
    
    def build_all(self, data_list: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Build Markdown documentation for multiple data items.
        
        Args:
            data_list: The list of documentation data to build from.
            output_dir: The directory to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Build documentation for each data item
        for data in data_list:
            # Get output file name
            if "type" in data and "name" in data:
                output_file = os.path.join(output_dir, f"{data['type']}_{data['name']}.md")
            elif "name" in data:
                output_file = os.path.join(output_dir, f"{data['name']}.md")
            else:
                output_file = os.path.join(output_dir, f"doc_{len(os.listdir(output_dir))}.md")
            
            # Build documentation
            self.build(data, output_file)
    
    def _default_render(self, data: Dict[str, Any]) -> str:
        """
        Default rendering for Markdown documentation.
        
        Args:
            data: The documentation data to render.
            
        Returns:
            Rendered documentation as a string.
        """
        lines = []
        
        # Title
        if "name" in data:
            lines.append(f"# {data['name']}")
            lines.append("")
        
        # Description
        if "doc" in data:
            lines.append(data["doc"])
            lines.append("")
        
        # Other data
        for key, value in data.items():
            if key not in ["name", "doc"]:
                if isinstance(value, list):
                    lines.append(f"## {key.capitalize()}")
                    lines.append("")
                    
                    for item in value:
                        if isinstance(item, dict) and "name" in item:
                            lines.append(f"- {item['name']}")
                        else:
                            lines.append(f"- {item}")
                    
                    lines.append("")
                elif isinstance(value, dict):
                    lines.append(f"## {key.capitalize()}")
                    lines.append("")
                    
                    for k, v in value.items():
                        lines.append(f"- {k}: {v}")
                    
                    lines.append("")
                else:
                    lines.append(f"## {key.capitalize()}")
                    lines.append("")
                    lines.append(str(value))
                    lines.append("")
        
        return "\n".join(lines)


@tag("docs.builder")
class HtmlBuilder(DocBuilder):
    """
    Builder for HTML documentation.
    
    This class builds documentation in HTML format, which is the standard markup
    language for web pages.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template_dir: The directory containing templates.
        metadata: Additional metadata for the builder.
        template: The template to use for generating documentation.
        css_file: The CSS file to include in the HTML.
        js_file: The JavaScript file to include in the HTML.
    
    TODO(Issue #12): Add support for HTML themes
    TODO(Issue #12): Implement HTML analytics
    """
    
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template: Optional[Any] = None,
        css_file: Optional[str] = None,
        js_file: Optional[str] = None
    ) -> None:
        """
        Initialize the HTML builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            template: The template to use for generating documentation.
            css_file: The CSS file to include in the HTML.
            js_file: The JavaScript file to include in the HTML.
        """
        super().__init__(output_dir, template_dir, metadata)
        self.template = template
        self.css_file = css_file
        self.js_file = js_file
    
    def build(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Build HTML documentation from data.
        
        Args:
            data: The documentation data to build from.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Render documentation using template
        if self.template is not None:
            content = self.template.render(data)
        else:
            # Default rendering
            content = self._default_render(data)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(content)
        
        # Copy CSS file if specified
        if self.css_file and os.path.isfile(self.css_file):
            css_output = os.path.join(os.path.dirname(output_file), "style.css")
            shutil.copy(self.css_file, css_output)
        
        # Copy JavaScript file if specified
        if self.js_file and os.path.isfile(self.js_file):
            js_output = os.path.join(os.path.dirname(output_file), "script.js")
            shutil.copy(self.js_file, js_output)
    
    def build_all(self, data_list: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Build HTML documentation for multiple data items.
        
        Args:
            data_list: The list of documentation data to build from.
            output_dir: The directory to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Build documentation for each data item
        for data in data_list:
            # Get output file name
            if "type" in data and "name" in data:
                output_file = os.path.join(output_dir, f"{data['type']}_{data['name']}.html")
            elif "name" in data:
                output_file = os.path.join(output_dir, f"{data['name']}.html")
            else:
                output_file = os.path.join(output_dir, f"doc_{len(os.listdir(output_dir))}.html")
            
            # Build documentation
            self.build(data, output_file)
        
        # Create index file
        index_data = {
            "name": "Documentation Index",
            "doc": "Index of documentation files",
            "files": [
                {
                    "name": os.path.splitext(os.path.basename(f))[0],
                    "path": os.path.basename(f),
                }
                for f in os.listdir(output_dir)
                if f.endswith(".html") and f != "index.html"
            ],
        }
        
        self.build(index_data, os.path.join(output_dir, "index.html"))
    
    def _default_render(self, data: Dict[str, Any]) -> str:
        """
        Default rendering for HTML documentation.
        
        Args:
            data: The documentation data to render.
            
        Returns:
            Rendered documentation as a string.
        """
        lines = []
        
        # HTML header
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("    <meta charset=\"UTF-8\">")
        
        if "name" in data:
            lines.append(f"    <title>{data['name']}</title>")
        else:
            lines.append("    <title>Documentation</title>")
        
        if self.css_file:
            lines.append("    <link rel=\"stylesheet\" href=\"style.css\">")
        else:
            lines.append("    <style>")
            lines.append("        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }")
            lines.append("        h1 { color: #333; }")
            lines.append("        h2 { color: #666; }")
            lines.append("        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
            lines.append("        code { background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }")
            lines.append("        .container { max-width: 800px; margin: 0 auto; }")
            lines.append("    </style>")
        
        lines.append("</head>")
        lines.append("<body>")
        lines.append("    <div class=\"container\">")
        
        # Title
        if "name" in data:
            lines.append(f"        <h1>{data['name']}</h1>")
        
        # Description
        if "doc" in data:
            lines.append(f"        <p>{data['doc']}</p>")
        
        # Files (for index)
        if "files" in data:
            lines.append("        <h2>Files</h2>")
            lines.append("        <ul>")
            
            for file in data["files"]:
                lines.append(f"            <li><a href=\"{file['path']}\">{file['name']}</a></li>")
            
            lines.append("        </ul>")
        
        # Other data
        for key, value in data.items():
            if key not in ["name", "doc", "files"]:
                if isinstance(value, list):
                    lines.append(f"        <h2>{key.capitalize()}</h2>")
                    lines.append("        <ul>")
                    
                    for item in value:
                        if isinstance(item, dict) and "name" in item:
                            lines.append(f"            <li>{item['name']}</li>")
                        else:
                            lines.append(f"            <li>{item}</li>")
                    
                    lines.append("        </ul>")
                elif isinstance(value, dict):
                    lines.append(f"        <h2>{key.capitalize()}</h2>")
                    lines.append("        <ul>")
                    
                    for k, v in value.items():
                        lines.append(f"            <li>{k}: {v}</li>")
                    
                    lines.append("        </ul>")
                else:
                    lines.append(f"        <h2>{key.capitalize()}</h2>")
                    lines.append(f"        <p>{value}</p>")
        
        # HTML footer
        lines.append("    </div>")
        
        if self.js_file:
            lines.append("    <script src=\"script.js\"></script>")
        
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)


@tag("docs.builder")
class WebsiteBuilder(DocBuilder):
    """
    Builder for documentation website.
    
    This class builds a documentation website, which includes multiple HTML pages,
    navigation, search, and other features.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template_dir: The directory containing templates.
        metadata: Additional metadata for the builder.
        title: The title of the website.
        description: The description of the website.
        theme: The theme to use for the website.
    
    TODO(Issue #12): Add support for website themes
    TODO(Issue #12): Implement website analytics
    """
    
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        title: str = "Documentation",
        description: str = "Documentation for the project",
        theme: str = "default"
    ) -> None:
        """
        Initialize the website builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            title: The title of the website.
            description: The description of the website.
            theme: The theme to use for the website.
        """
        super().__init__(output_dir, template_dir, metadata)
        self.title = title
        self.description = description
        self.theme = theme
    
    def build(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Build a documentation page for the website.
        
        Args:
            data: The documentation data to build from.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Convert Markdown to HTML
        if "content" in data and data["content"].endswith(".md"):
            with open(data["content"], "r") as f:
                content = f.read()
            
            html_content = markdown.markdown(content)
        else:
            html_content = data.get("content", "")
        
        # Create HTML page
        html = self._create_page(
            title=data.get("title", self.title),
            content=html_content,
            navigation=data.get("navigation", []),
            breadcrumbs=data.get("breadcrumbs", []),
        )
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(html)
    
    def build_all(self, data_list: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Build a documentation website from multiple data items.
        
        Args:
            data_list: The list of documentation data to build from.
            output_dir: The directory to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create navigation
        navigation = []
        
        for data in data_list:
            if "title" in data and "output_file" in data:
                navigation.append({
                    "title": data["title"],
                    "url": os.path.basename(data["output_file"]),
                })
        
        # Build documentation for each data item
        for data in data_list:
            # Get output file
            if "output_file" in data:
                output_file = os.path.join(output_dir, data["output_file"])
            elif "title" in data:
                output_file = os.path.join(output_dir, self._slugify(data["title"]) + ".html")
            else:
                output_file = os.path.join(output_dir, f"page_{len(os.listdir(output_dir))}.html")
            
            # Add navigation to data
            data["navigation"] = navigation
            
            # Build documentation
            self.build(data, output_file)
        
        # Copy assets
        self._copy_assets(output_dir)
    
    def _create_page(
        self,
        title: str,
        content: str,
        navigation: List[Dict[str, str]],
        breadcrumbs: List[Dict[str, str]]
    ) -> str:
        """
        Create an HTML page for the website.
        
        Args:
            title: The title of the page.
            content: The content of the page.
            navigation: The navigation items.
            breadcrumbs: The breadcrumb items.
            
        Returns:
            The HTML page as a string.
        """
        lines = []
        
        # HTML header
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("    <meta charset=\"UTF-8\">")
        lines.append(f"    <title>{title} - {self.title}</title>")
        lines.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        lines.append(f"    <meta name=\"description\" content=\"{self.description}\">")
        lines.append("    <link rel=\"stylesheet\" href=\"assets/css/style.css\">")
        lines.append("</head>")
        lines.append("<body>")
        
        # Header
        lines.append("    <header>")
        lines.append(f"        <h1>{self.title}</h1>")
        lines.append("        <div class=\"search\">")
        lines.append("            <input type=\"text\" placeholder=\"Search...\">")
        lines.append("            <button>Search</button>")
        lines.append("        </div>")
        lines.append("    </header>")
        
        # Navigation
        lines.append("    <nav>")
        lines.append("        <ul>")
        
        for item in navigation:
            lines.append(f"            <li><a href=\"{item['url']}\">{item['title']}</a></li>")
        
        lines.append("        </ul>")
        lines.append("    </nav>")
        
        # Main content
        lines.append("    <main>")
        
        # Breadcrumbs
        if breadcrumbs:
            lines.append("        <div class=\"breadcrumbs\">")
            
            for i, item in enumerate(breadcrumbs):
                if i < len(breadcrumbs) - 1:
                    lines.append(f"            <a href=\"{item['url']}\">{item['title']}</a> &gt; ")
                else:
                    lines.append(f"            <span>{item['title']}</span>")
            
            lines.append("        </div>")
        
        # Content
        lines.append(f"        <h2>{title}</h2>")
        lines.append(f"        <div class=\"content\">{content}</div>")
        lines.append("    </main>")
        
        # Footer
        lines.append("    <footer>")
        lines.append(f"        <p>&copy; {self.title}. All rights reserved.</p>")
        lines.append("    </footer>")
        
        # JavaScript
        lines.append("    <script src=\"assets/js/script.js\"></script>")
        
        # HTML footer
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def _copy_assets(self, output_dir: str) -> None:
        """
        Copy assets to the output directory.
        
        Args:
            output_dir: The directory to copy assets to.
        """
        # Create assets directory
        assets_dir = os.path.join(output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create CSS directory
        css_dir = os.path.join(assets_dir, "css")
        os.makedirs(css_dir, exist_ok=True)
        
        # Create JavaScript directory
        js_dir = os.path.join(assets_dir, "js")
        os.makedirs(js_dir, exist_ok=True)
        
        # Create CSS file
        with open(os.path.join(css_dir, "style.css"), "w") as f:
            f.write("""
/* Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Body */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

/* Header */
header {
    background-color: #333;
    color: #fff;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 {
    font-size: 1.5rem;
}

.search input {
    padding: 0.5rem;
    border: none;
    border-radius: 3px 0 0 3px;
}

.search button {
    padding: 0.5rem;
    background-color: #666;
    color: #fff;
    border: none;
    border-radius: 0 3px 3px 0;
    cursor: pointer;
}

/* Navigation */
nav {
    background-color: #444;
    color: #fff;
}

nav ul {
    list-style: none;
    display: flex;
    padding: 0.5rem;
}

nav ul li {
    margin-right: 1rem;
}

nav ul li a {
    color: #fff;
    text-decoration: none;
}

nav ul li a:hover {
    text-decoration: underline;
}

/* Main content */
main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    background-color: #fff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.breadcrumbs {
    margin-bottom: 1rem;
    color: #666;
}

.breadcrumbs a {
    color: #666;
    text-decoration: none;
}

.breadcrumbs a:hover {
    text-decoration: underline;
}

h2 {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.content {
    margin-bottom: 2rem;
}

.content h3 {
    margin: 1.5rem 0 0.5rem;
}

.content p {
    margin-bottom: 1rem;
}

.content ul, .content ol {
    margin-bottom: 1rem;
    margin-left: 2rem;
}

.content pre {
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 1rem;
}

.content code {
    background-color: #f5f5f5;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
}

/* Footer */
footer {
    background-color: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    header {
        flex-direction: column;
    }
    
    .search {
        margin-top: 1rem;
    }
    
    nav ul {
        flex-direction: column;
    }
    
    nav ul li {
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
}
            """)
        
        # Create JavaScript file
        with open(os.path.join(js_dir, "script.js"), "w") as f:
            f.write("""
// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search input');
    const searchButton = document.querySelector('.search button');
    
    searchButton.addEventListener('click', function() {
        search(searchInput.value);
    });
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            search(searchInput.value);
        }
    });
    
    function search(query) {
        if (query.trim() === '') {
            return;
        }
        
        // Simple search implementation
        const content = document.querySelector('.content');
        const text = content.textContent.toLowerCase();
        const searchText = query.toLowerCase();
        
        if (text.includes(searchText)) {
            // Highlight matches
            const regex = new RegExp(searchText, 'gi');
            content.innerHTML = content.innerHTML.replace(regex, match => `<mark>${match}</mark>`);
            
            // Scroll to first match
            const firstMatch = document.querySelector('mark');
            if (firstMatch) {
                firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            alert('No matches found.');
        }
    }
});
            """)
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to a URL-friendly slug.
        
        Args:
            text: The text to convert.
            
        Returns:
            The slugified text.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Replace spaces with hyphens
        text = text.replace(" ", "-")
        
        # Remove non-alphanumeric characters
        text = re.sub(r"[^a-z0-9-]", "", text)
        
        # Remove duplicate hyphens
        text = re.sub(r"-+", "-", text)
        
        # Remove leading and trailing hyphens
        text = text.strip("-")
        
        return text
