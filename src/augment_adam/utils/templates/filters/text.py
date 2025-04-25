"""
Text-related filters for the template engine.

This module provides filters for text formatting and transformation.
"""

import re
import textwrap
from typing import List, Dict, Any, Optional, Union


def pluralize(s: str) -> str:
    """
    Convert a singular word to its plural form.
    
    Args:
        s: The input string.
        
    Returns:
        The pluralized string.
    
    Examples:
        >>> pluralize("cat")
        'cats'
        >>> pluralize("box")
        'boxes'
        >>> pluralize("city")
        'cities'
    """
    if s.endswith('s') or s.endswith('x') or s.endswith('z') or s.endswith('ch') or s.endswith('sh'):
        return s + 'es'
    elif s.endswith('y') and len(s) > 1 and s[-2] not in 'aeiou':
        return s[:-1] + 'ies'
    else:
        return s + 's'


def singularize(s: str) -> str:
    """
    Convert a plural word to its singular form.
    
    Args:
        s: The input string.
        
    Returns:
        The singularized string.
    
    Examples:
        >>> singularize("cats")
        'cat'
        >>> singularize("boxes")
        'box'
        >>> singularize("cities")
        'city'
    """
    if s.endswith('ies') and len(s) > 3:
        return s[:-3] + 'y'
    elif s.endswith('es') and len(s) > 2:
        if s.endswith('ses') or s.endswith('xes') or s.endswith('zes') or s.endswith('ches') or s.endswith('shes'):
            return s[:-2]
        else:
            return s[:-1]
    elif s.endswith('s') and len(s) > 1:
        return s[:-1]
    else:
        return s


def capitalize(s: str) -> str:
    """
    Capitalize the first letter of a string.
    
    Args:
        s: The input string.
        
    Returns:
        The capitalized string.
    
    Examples:
        >>> capitalize("hello")
        'Hello'
        >>> capitalize("hello world")
        'Hello world'
    """
    if not s:
        return s
    return s[0].upper() + s[1:]


def titleize(s: str) -> str:
    """
    Capitalize the first letter of each word in a string.
    
    Args:
        s: The input string.
        
    Returns:
        The titleized string.
    
    Examples:
        >>> titleize("hello world")
        'Hello World'
        >>> titleize("hello_world")
        'Hello World'
    """
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return ' '.join(word.capitalize() for word in s.split())


def humanize(s: str) -> str:
    """
    Convert a string to a human-readable format.
    
    Args:
        s: The input string.
        
    Returns:
        The humanized string.
    
    Examples:
        >>> humanize("hello_world")
        'Hello world'
        >>> humanize("helloWorld")
        'Hello world'
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    s = ' '.join(word for word in s.split())
    return capitalize(s.lower())


def truncate(s: str, length: int = 30, suffix: str = '...') -> str:
    """
    Truncate a string to a specified length.
    
    Args:
        s: The input string.
        length: The maximum length of the string.
        suffix: The suffix to append to the truncated string.
        
    Returns:
        The truncated string.
    
    Examples:
        >>> truncate("hello world", 5)
        'hello...'
        >>> truncate("hello world", 5, suffix='')
        'hello'
    """
    if len(s) <= length:
        return s
    return s[:length - len(suffix)] + suffix


def word_wrap(s: str, width: int = 80) -> str:
    """
    Wrap a string to a specified width, preserving paragraphs.
    
    Args:
        s: The input string.
        width: The maximum width of each line.
        
    Returns:
        The wrapped string.
    
    Examples:
        >>> word_wrap("hello world", 5)
        'hello\\nworld'
    """
    paragraphs = s.split('\n\n')
    wrapped_paragraphs = [textwrap.fill(p, width=width) for p in paragraphs]
    return '\n\n'.join(wrapped_paragraphs)


def strip_html(s: str) -> str:
    """
    Remove HTML tags from a string.
    
    Args:
        s: The input string.
        
    Returns:
        The string with HTML tags removed.
    
    Examples:
        >>> strip_html("<p>hello <b>world</b></p>")
        'hello world'
    """
    return re.sub(r'<[^>]*>', '', s)


def markdown_to_html(s: str) -> str:
    """
    Convert Markdown to HTML.
    
    Args:
        s: The input Markdown string.
        
    Returns:
        The HTML string.
    
    Examples:
        >>> markdown_to_html("# Hello\\n\\nWorld")
        '<h1>Hello</h1>\\n\\n<p>World</p>'
    """
    # This is a very simple implementation
    # Headers
    s = re.sub(r'^# (.+)$', r'<h1>\1</h1>', s, flags=re.MULTILINE)
    s = re.sub(r'^## (.+)$', r'<h2>\1</h2>', s, flags=re.MULTILINE)
    s = re.sub(r'^### (.+)$', r'<h3>\1</h3>', s, flags=re.MULTILINE)
    
    # Bold and italic
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    
    # Lists
    s = re.sub(r'^- (.+)$', r'<li>\1</li>', s, flags=re.MULTILINE)
    
    # Links
    s = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', s)
    
    # Paragraphs
    s = re.sub(r'(?<!\n)\n(?!\n)(.+?)(?=\n\n|\Z)', r'<p>\1</p>', s, flags=re.DOTALL)
    
    return s


def html_to_markdown(s: str) -> str:
    """
    Convert HTML to Markdown.
    
    Args:
        s: The input HTML string.
        
    Returns:
        The Markdown string.
    
    Examples:
        >>> html_to_markdown("<h1>Hello</h1>\\n\\n<p>World</p>")
        '# Hello\\n\\nWorld'
    """
    # This is a very simple implementation
    # Headers
    s = re.sub(r'<h1>(.+?)</h1>', r'# \1', s)
    s = re.sub(r'<h2>(.+?)</h2>', r'## \1', s)
    s = re.sub(r'<h3>(.+?)</h3>', r'### \1', s)
    
    # Bold and italic
    s = re.sub(r'<strong>(.+?)</strong>', r'**\1**', s)
    s = re.sub(r'<em>(.+?)</em>', r'*\1*', s)
    
    # Lists
    s = re.sub(r'<li>(.+?)</li>', r'- \1', s)
    
    # Links
    s = re.sub(r'<a href="(.+?)">(.+?)</a>', r'[\2](\1)', s)
    
    # Paragraphs
    s = re.sub(r'<p>(.+?)</p>', r'\1', s)
    
    return s
