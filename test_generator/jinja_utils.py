from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import os

def render_template(template_name: str, context: Dict[str, Any], template_dir: str = None) -> str:
    """
    Render a Jinja2 template with the given context.
    :param template_name: Name of the template file (e.g., 'hypothesis_template.j2')
    :param context: Dictionary of variables to render in the template
    :param template_dir: Directory containing templates (defaults to '../templates')
    :return: Rendered template as a string
    """
    if template_dir is None:
        template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    return template.render(context)
