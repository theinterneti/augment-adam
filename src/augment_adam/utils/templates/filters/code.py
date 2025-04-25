"""
Code-related filters for the template engine.

This module provides filters for code generation, formatting, and transformation.
"""

import re
import textwrap
from typing import List, Dict, Any, Optional, Union


def to_camel_case(s: str) -> str:
    """
    Convert a string to camelCase.
    
    Args:
        s: The input string.
        
    Returns:
        The string in camelCase.
    
    Examples:
        >>> to_camel_case("hello world")
        'helloWorld'
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("HelloWorld")
        'helloWorld'
    """
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    words = s.split()
    if not words:
        return ''
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def to_snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    
    Args:
        s: The input string.
        
    Returns:
        The string in snake_case.
    
    Examples:
        >>> to_snake_case("hello world")
        'hello_world'
        >>> to_snake_case("helloWorld")
        'hello_world'
        >>> to_snake_case("HelloWorld")
        'hello_world'
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return '_'.join(word.lower() for word in s.split())


def to_pascal_case(s: str) -> str:
    """
    Convert a string to PascalCase.
    
    Args:
        s: The input string.
        
    Returns:
        The string in PascalCase.
    
    Examples:
        >>> to_pascal_case("hello world")
        'HelloWorld'
        >>> to_pascal_case("hello_world")
        'HelloWorld'
        >>> to_pascal_case("helloWorld")
        'HelloWorld'
    """
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return ''.join(word.capitalize() for word in s.split())


def to_kebab_case(s: str) -> str:
    """
    Convert a string to kebab-case.
    
    Args:
        s: The input string.
        
    Returns:
        The string in kebab-case.
    
    Examples:
        >>> to_kebab_case("hello world")
        'hello-world'
        >>> to_kebab_case("hello_world")
        'hello-world'
        >>> to_kebab_case("helloWorld")
        'hello-world'
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return '-'.join(word.lower() for word in s.split())


def to_constant_case(s: str) -> str:
    """
    Convert a string to CONSTANT_CASE.
    
    Args:
        s: The input string.
        
    Returns:
        The string in CONSTANT_CASE.
    
    Examples:
        >>> to_constant_case("hello world")
        'HELLO_WORLD'
        >>> to_constant_case("hello_world")
        'HELLO_WORLD'
        >>> to_constant_case("helloWorld")
        'HELLO_WORLD'
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return '_'.join(word.upper() for word in s.split())


def indent(s: str, amount: int = 4, first_line: bool = True) -> str:
    """
    Indent a string by a specified amount.
    
    Args:
        s: The input string.
        amount: The number of spaces to indent by.
        first_line: Whether to indent the first line.
        
    Returns:
        The indented string.
    
    Examples:
        >>> indent("hello\\nworld", 2)
        '  hello\\n  world'
        >>> indent("hello\\nworld", 2, first_line=False)
        'hello\\n  world'
    """
    lines = s.split('\n')
    if not first_line and lines:
        return lines[0] + '\n' + '\n'.join(' ' * amount + line for line in lines[1:])
    return '\n'.join(' ' * amount + line for line in lines)


def dedent(s: str) -> str:
    """
    Dedent a string, removing common leading whitespace.
    
    Args:
        s: The input string.
        
    Returns:
        The dedented string.
    
    Examples:
        >>> dedent("    hello\\n    world")
        'hello\\nworld'
        >>> dedent("    hello\\n      world")
        'hello\\n  world'
    """
    return textwrap.dedent(s)


def wrap(s: str, width: int = 80) -> str:
    """
    Wrap a string to a specified width.
    
    Args:
        s: The input string.
        width: The maximum width of each line.
        
    Returns:
        The wrapped string.
    
    Examples:
        >>> wrap("hello world", 5)
        'hello\\nworld'
    """
    return '\n'.join(textwrap.wrap(s, width=width))


def format_docstring(docstring: str, style: str = 'google') -> str:
    """
    Format a docstring according to a specified style.
    
    Args:
        docstring: The input docstring.
        style: The style to format the docstring in ('google', 'numpy', 'sphinx').
        
    Returns:
        The formatted docstring.
    
    Examples:
        >>> format_docstring("This is a docstring.\\n\\nArgs:\\n    x: An argument.", 'google')
        'This is a docstring.\\n\\nArgs:\\n    x: An argument.'
    """
    if style == 'google':
        return docstring
    elif style == 'numpy':
        # Convert Google-style to NumPy-style
        docstring = re.sub(r'Args:', 'Parameters\n----------', docstring)
        docstring = re.sub(r'Returns:', 'Returns\n-------', docstring)
        docstring = re.sub(r'Raises:', 'Raises\n------', docstring)
        docstring = re.sub(r'Examples:', 'Examples\n--------', docstring)
        docstring = re.sub(r'Notes:', 'Notes\n-----', docstring)
        
        # Convert parameter descriptions
        def param_repl(match):
            param_name = match.group(1)
            param_desc = match.group(2)
            return f"{param_name} : \n    {param_desc}"
        
        docstring = re.sub(r'    ([^:]+): (.*)', param_repl, docstring)
        
        return docstring
    elif style == 'sphinx':
        # Convert Google-style to Sphinx-style
        docstring = re.sub(r'Args:', ':param:', docstring)
        docstring = re.sub(r'Returns:', ':returns:', docstring)
        docstring = re.sub(r'Raises:', ':raises:', docstring)
        
        # Convert parameter descriptions
        def param_repl(match):
            param_name = match.group(1)
            param_desc = match.group(2)
            return f":param {param_name}: {param_desc}"
        
        docstring = re.sub(r'    ([^:]+): (.*)', param_repl, docstring)
        
        return docstring
    else:
        return docstring


def format_type_hint(type_hint: str) -> str:
    """
    Format a type hint for Python code.
    
    Args:
        type_hint: The input type hint.
        
    Returns:
        The formatted type hint.
    
    Examples:
        >>> format_type_hint("list[str]")
        'List[str]'
        >>> format_type_hint("dict[str, int]")
        'Dict[str, int]'
    """
    # Replace built-in types with their typing equivalents
    replacements = {
        'list': 'List',
        'dict': 'Dict',
        'set': 'Set',
        'tuple': 'Tuple',
        'frozenset': 'FrozenSet',
        'deque': 'Deque',
        'defaultdict': 'DefaultDict',
        'counter': 'Counter',
        'chainmap': 'ChainMap',
    }
    
    for old, new in replacements.items():
        # Replace only if it's a standalone type or a generic type
        type_hint = re.sub(rf'\b{old}\b(?!\[)', new, type_hint)
        type_hint = re.sub(rf'\b{old}(\[)', f'{new}\\1', type_hint)
    
    return type_hint


def format_imports(imports: List[str]) -> str:
    """
    Format a list of imports according to best practices.
    
    Args:
        imports: List of import statements.
        
    Returns:
        Formatted import statements.
    
    Examples:
        >>> format_imports(["from typing import List, Dict", "import os", "import sys"])
        'import os\\nimport sys\\n\\nfrom typing import Dict, List'
    """
    standard_imports = []
    third_party_imports = []
    local_imports = []
    
    for imp in imports:
        if imp.startswith('import '):
            module = imp.split()[1].split('.')[0]
            if module in ['os', 'sys', 're', 'math', 'datetime', 'time', 'json', 'csv', 'random', 'collections', 'itertools', 'functools', 'typing']:
                standard_imports.append(imp)
            elif module in ['numpy', 'pandas', 'matplotlib', 'sklearn', 'tensorflow', 'torch', 'jinja2', 'flask', 'django', 'requests', 'bs4', 'selenium']:
                third_party_imports.append(imp)
            else:
                local_imports.append(imp)
        elif imp.startswith('from '):
            module = imp.split()[1].split('.')[0]
            if module in ['os', 'sys', 're', 'math', 'datetime', 'time', 'json', 'csv', 'random', 'collections', 'itertools', 'functools', 'typing']:
                standard_imports.append(imp)
            elif module in ['numpy', 'pandas', 'matplotlib', 'sklearn', 'tensorflow', 'torch', 'jinja2', 'flask', 'django', 'requests', 'bs4', 'selenium']:
                third_party_imports.append(imp)
            else:
                local_imports.append(imp)
    
    # Sort imports alphabetically within each group
    standard_imports.sort()
    third_party_imports.sort()
    local_imports.sort()
    
    # Combine the groups with blank lines between them
    result = []
    if standard_imports:
        result.extend(standard_imports)
    if third_party_imports:
        if result:
            result.append('')
        result.extend(third_party_imports)
    if local_imports:
        if result:
            result.append('')
        result.extend(local_imports)
    
    return '\n'.join(result)
