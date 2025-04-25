"""Unit tests for the template engine.

This module contains unit tests for the template engine in augment_adam.utils.template_engine.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from jinja2 import Template, Environment
from augment_adam.utils.template_engine import (
    TemplateEngine, Tag, TagManager, get_template_engine,
    render_template, render_code_template, render_test_template,
    render_doc_template, get_docstring
)


class TestTag:
    """Tests for the Tag class."""
    
    def test_init(self):
        """Test Tag initialization."""
        # Arrange
        parent = Tag("parent", {})
        
        # Act
        tag = Tag("test", {}, parent)
        
        # Assert
        assert tag.name == "test"
        assert tag.parent == parent
        assert tag in parent.children
    
    def test_str(self):
        """Test Tag string representation."""
        # Arrange
        tag = Tag("test", {})
        
        # Act
        result = str(tag)
        
        # Assert
        assert result == "test"
    
    def test_repr(self):
        """Test Tag repr representation."""
        # Arrange
        tag = Tag("test", {})
        
        # Act
        result = repr(tag)
        
        # Assert
        assert "Tag" in result
        assert "test" in result
    
    def test_get_full_path_no_parent(self):
        """Test get_full_path with no parent."""
        # Arrange
        tag = Tag("test", {})
        
        # Act
        result = tag.get_full_path()
        
        # Assert
        assert result == "test"
    
    def test_get_full_path_with_parent(self):
        """Test get_full_path with parent."""
        # Arrange
        parent = Tag("parent", {})
        tag = Tag("test", {}, parent)
        
        # Act
        result = tag.get_full_path()
        
        # Assert
        assert result == "parent.test"
    
    def test_get_full_path_with_grandparent(self):
        """Test get_full_path with grandparent."""
        # Arrange
        grandparent = Tag("grandparent", {})
        parent = Tag("parent", {}, grandparent)
        tag = Tag("test", {}, parent)
        
        # Act
        result = tag.get_full_path()
        
        # Assert
        assert result == "grandparent.parent.test"
    
    def test_has_attribute(self):
        """Test has_attribute."""
        # Arrange
        tag = Tag("test", {"key": "value"})
        
        # Act & Assert
        assert tag.has_attribute("key") is True
        assert tag.has_attribute("nonexistent") is False
    
    def test_get_attribute(self):
        """Test get_attribute."""
        # Arrange
        tag = Tag("test", {"key": "value"})
        
        # Act & Assert
        assert tag.get_attribute("key") == "value"
        assert tag.get_attribute("nonexistent") is None
        assert tag.get_attribute("nonexistent", "default") == "default"
    
    def test_set_attribute(self):
        """Test set_attribute."""
        # Arrange
        tag = Tag("test", {})
        
        # Act
        tag.set_attribute("key", "value")
        
        # Assert
        assert tag.attributes["key"] == "value"
    
    def test_is_child_of_string(self):
        """Test is_child_of with string parent."""
        # Arrange
        parent = Tag("parent", {})
        tag = Tag("test", {}, parent)
        
        # Act & Assert
        assert tag.is_child_of("parent") is True
        assert tag.is_child_of("nonexistent") is False
    
    def test_is_child_of_tag(self):
        """Test is_child_of with Tag parent."""
        # Arrange
        parent = Tag("parent", {})
        tag = Tag("test", {}, parent)
        
        # Act & Assert
        assert tag.is_child_of(parent) is True
        assert tag.is_child_of(Tag("nonexistent", {})) is False
    
    def test_is_child_of_grandparent(self):
        """Test is_child_of with grandparent."""
        # Arrange
        grandparent = Tag("grandparent", {})
        parent = Tag("parent", {}, grandparent)
        tag = Tag("test", {}, parent)
        
        # Act & Assert
        assert tag.is_child_of("grandparent") is True


class TestTagManager:
    """Tests for the TagManager class."""
    
    def test_init(self):
        """Test TagManager initialization."""
        # Act
        manager = TagManager()
        
        # Assert
        assert isinstance(manager.tags, dict)
    
    def test_create_tag(self):
        """Test create_tag."""
        # Arrange
        manager = TagManager()
        
        # Act
        tag = manager.create_tag("test", {})
        
        # Assert
        assert tag.name == "test"
        assert manager.tags["test"] == tag
    
    def test_create_tag_with_parent_string(self):
        """Test create_tag with parent string."""
        # Arrange
        manager = TagManager()
        manager.create_tag("parent", {})
        
        # Act
        tag = manager.create_tag("test", {}, "parent")
        
        # Assert
        assert tag.parent == manager.tags["parent"]
        assert tag in manager.tags["parent"].children
    
    def test_create_tag_with_parent_tag(self):
        """Test create_tag with parent tag."""
        # Arrange
        manager = TagManager()
        parent = manager.create_tag("parent", {})
        
        # Act
        tag = manager.create_tag("test", {}, parent)
        
        # Assert
        assert tag.parent == parent
        assert tag in parent.children
    
    def test_create_tag_with_attributes(self):
        """Test create_tag with attributes."""
        # Arrange
        manager = TagManager()
        
        # Act
        tag = manager.create_tag("test", {"key": "value"})
        
        # Assert
        assert tag.attributes["key"] == "value"
    
    def test_create_tag_duplicate(self):
        """Test create_tag with duplicate name."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test", {})
        
        # Act & Assert
        with pytest.raises(ValueError):
            manager.create_tag("test", {})
    
    def test_create_tag_nonexistent_parent(self):
        """Test create_tag with nonexistent parent."""
        # Arrange
        manager = TagManager()
        
        # Act & Assert
        with pytest.raises(ValueError):
            manager.create_tag("test", {}, "nonexistent")
    
    def test_get_tag(self):
        """Test get_tag."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test", {})
        
        # Act & Assert
        assert manager.get_tag("test") is not None
        assert manager.get_tag("nonexistent") is None
    
    def test_get_or_create_tag_existing(self):
        """Test get_or_create_tag with existing tag."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test", {})
        
        # Act
        tag = manager.get_or_create_tag("test", {})
        
        # Assert
        assert tag == manager.tags["test"]
    
    def test_get_or_create_tag_new(self):
        """Test get_or_create_tag with new tag."""
        # Arrange
        manager = TagManager()
        
        # Act
        tag = manager.get_or_create_tag("test", {})
        
        # Assert
        assert tag.name == "test"
        assert manager.tags["test"] == tag
    
    def test_delete_tag(self):
        """Test delete_tag."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test", {})
        
        # Act
        manager.delete_tag("test")
        
        # Assert
        assert "test" not in manager.tags
    
    def test_delete_tag_with_children(self):
        """Test delete_tag with children."""
        # Arrange
        manager = TagManager()
        manager.create_tag("parent", {})
        manager.create_tag("child", {}, "parent")
        
        # Act
        manager.delete_tag("parent")
        
        # Assert
        assert "parent" not in manager.tags
        assert "child" not in manager.tags
    
    def test_delete_tag_nonexistent(self):
        """Test delete_tag with nonexistent tag."""
        # Arrange
        manager = TagManager()
        
        # Act & Assert
        with pytest.raises(ValueError):
            manager.delete_tag("nonexistent")
    
    def test_get_tags_by_attribute(self):
        """Test get_tags_by_attribute."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test1", {"key": "value1"})
        manager.create_tag("test2", {"key": "value2"})
        manager.create_tag("test3", {"other": "value"})
        
        # Act
        tags = manager.get_tags_by_attribute("key")
        
        # Assert
        assert len(tags) == 2
        assert all(tag.has_attribute("key") for tag in tags)
    
    def test_get_tags_by_attribute_with_value(self):
        """Test get_tags_by_attribute with value."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test1", {"key": "value1"})
        manager.create_tag("test2", {"key": "value2"})
        
        # Act
        tags = manager.get_tags_by_attribute("key", "value1")
        
        # Assert
        assert len(tags) == 1
        assert tags[0].name == "test1"
    
    def test_get_children(self):
        """Test get_children."""
        # Arrange
        manager = TagManager()
        manager.create_tag("parent", {})
        manager.create_tag("child1", {}, "parent")
        manager.create_tag("child2", {}, "parent")
        
        # Act
        children = manager.get_children("parent")
        
        # Assert
        assert len(children) == 2
        assert all(tag.parent == manager.tags["parent"] for tag in children)
    
    def test_get_children_nonexistent(self):
        """Test get_children with nonexistent tag."""
        # Arrange
        manager = TagManager()
        
        # Act & Assert
        with pytest.raises(ValueError):
            manager.get_children("nonexistent")
    
    def test_get_all_tags(self):
        """Test get_all_tags."""
        # Arrange
        manager = TagManager()
        manager.create_tag("test1", {})
        manager.create_tag("test2", {})
        
        # Act
        tags = manager.get_all_tags()
        
        # Assert
        assert len(tags) == 2
        assert all(isinstance(tag, Tag) for tag in tags)
    
    def test_get_root_tags(self):
        """Test get_root_tags."""
        # Arrange
        manager = TagManager()
        manager.create_tag("root1", {})
        manager.create_tag("root2", {})
        manager.create_tag("child", {}, "root1")
        
        # Act
        tags = manager.get_root_tags()
        
        # Assert
        assert len(tags) == 2
        assert all(tag.parent is None for tag in tags)
    
    def test_load_from_json(self, tmp_path):
        """Test load_from_json."""
        # Arrange
        manager = TagManager()
        json_file = tmp_path / "tags.json"
        json_file.write_text("""
        {
            "tag1": {
                "attributes": {"key": "value"}
            },
            "tag2": {
                "attributes": {},
                "parent": "tag1"
            }
        }
        """)
        
        # Act
        manager.load_from_json(json_file)
        
        # Assert
        assert "tag1" in manager.tags
        assert "tag2" in manager.tags
        assert manager.tags["tag2"].parent == manager.tags["tag1"]
    
    def test_save_to_json(self, tmp_path):
        """Test save_to_json."""
        # Arrange
        manager = TagManager()
        manager.create_tag("tag1", {"key": "value"})
        manager.create_tag("tag2", {}, "tag1")
        json_file = tmp_path / "tags.json"
        
        # Act
        manager.save_to_json(json_file)
        
        # Assert
        assert json_file.exists()
        content = json_file.read_text()
        assert "tag1" in content
        assert "tag2" in content
        assert "parent" in content


class TestTemplateEngine:
    """Tests for the TemplateEngine class."""
    
    def test_init(self, tmp_path):
        """Test TemplateEngine initialization."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Act
        engine = TemplateEngine(str(templates_dir))
        
        # Assert
        assert engine.templates_dir == str(templates_dir)
        assert isinstance(engine.env, Environment)
        assert isinstance(engine.tag_manager, TagManager)
    
    def test_render_template(self, tmp_path):
        """Test render_template."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "test.j2"
        template_file.write_text("Hello, {{ name }}!")
        engine = TemplateEngine(str(templates_dir))
        
        # Act
        result = engine.render_template("test.j2", {"name": "World"})
        
        # Assert
        assert result == "Hello, World!"
    
    def test_render_string_template(self):
        """Test render_string_template."""
        # Arrange
        engine = TemplateEngine()
        
        # Act
        result = engine.render_string_template("Hello, {{ name }}!", {"name": "World"})
        
        # Assert
        assert result == "Hello, World!"
    
    def test_get_docstring(self, tmp_path):
        """Test get_docstring."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "docstring_template.j2"
        template_file.write_text("""
        {% if docstring_type == "function" %}
        \"\"\"{{ summary }}
        
        {% if description %}{{ description }}
        
        {% endif %}
        Args:
        {% for param in parameters %}
            {{ param.name }}: {{ param.description }}
        {% endfor %}
        \"\"\"
        {% endif %}
        """)
        engine = TemplateEngine(str(templates_dir))
        
        # Act
        result = engine.get_docstring("function", "Test function", 
                                     description="This is a test function",
                                     parameters=[{"name": "param", "description": "A parameter"}])
        
        # Assert
        assert "Test function" in result
        assert "This is a test function" in result
        assert "param: A parameter" in result
    
    @patch("augment_adam.utils.template_engine.TemplateEngine.render_template")
    def test_render_code_template(self, mock_render_template):
        """Test render_code_template."""
        # Arrange
        engine = TemplateEngine()
        mock_render_template.return_value = "rendered template"
        
        # Act
        result = engine.render_code_template("test.j2", {"key": "value"})
        
        # Assert
        mock_render_template.assert_called_once_with("code/test.j2", {"key": "value"})
        assert result == "rendered template"
    
    @patch("augment_adam.utils.template_engine.TemplateEngine.render_template")
    def test_render_test_template(self, mock_render_template):
        """Test render_test_template."""
        # Arrange
        engine = TemplateEngine()
        mock_render_template.return_value = "rendered template"
        
        # Act
        result = engine.render_test_template("test.j2", {"key": "value"})
        
        # Assert
        mock_render_template.assert_called_once_with("tests/test.j2", {"key": "value"})
        assert result == "rendered template"
    
    @patch("augment_adam.utils.template_engine.TemplateEngine.render_template")
    def test_render_doc_template(self, mock_render_template):
        """Test render_doc_template."""
        # Arrange
        engine = TemplateEngine()
        mock_render_template.return_value = "rendered template"
        
        # Act
        result = engine.render_doc_template("test.j2", {"key": "value"})
        
        # Assert
        mock_render_template.assert_called_once_with("docs/test.j2", {"key": "value"})
        assert result == "rendered template"
    
    def test_to_camel_case(self):
        """Test _to_camel_case."""
        # Arrange
        engine = TemplateEngine()
        
        # Act & Assert
        assert engine._to_camel_case("hello world") == "helloWorld"
        assert engine._to_camel_case("hello_world") == "helloWorld"
        assert engine._to_camel_case("HelloWorld") == "helloWorld"
    
    def test_to_snake_case(self):
        """Test _to_snake_case."""
        # Arrange
        engine = TemplateEngine()
        
        # Act & Assert
        assert engine._to_snake_case("hello world") == "hello_world"
        assert engine._to_snake_case("helloWorld") == "hello_world"
        assert engine._to_snake_case("HelloWorld") == "hello_world"
    
    def test_to_pascal_case(self):
        """Test _to_pascal_case."""
        # Arrange
        engine = TemplateEngine()
        
        # Act & Assert
        assert engine._to_pascal_case("hello world") == "HelloWorld"
        assert engine._to_pascal_case("hello_world") == "HelloWorld"
        assert engine._to_pascal_case("helloWorld") == "HelloWorld"
    
    def test_to_kebab_case(self):
        """Test _to_kebab_case."""
        # Arrange
        engine = TemplateEngine()
        
        # Act & Assert
        assert engine._to_kebab_case("hello world") == "hello-world"
        assert engine._to_kebab_case("hello_world") == "hello-world"
        assert engine._to_kebab_case("helloWorld") == "hello-world"
    
    def test_extract_metadata(self):
        """Test _extract_metadata."""
        # Arrange
        engine = TemplateEngine()
        content = """
        {# @tags: tag1, tag2 #}
        {# @description: This is a description #}
        {# @variables: var1:str, var2:int #}
        """
        
        # Act
        metadata = engine._extract_metadata(content)
        
        # Assert
        assert metadata["tags"] == ["tag1", "tag2"]
        assert metadata["description"] == "This is a description"
        assert metadata["variables"] == {"var1": "str", "var2": "int"}
    
    def test_get_template_metadata(self, tmp_path):
        """Test get_template_metadata."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "test.j2"
        template_file.write_text("""
        {# @tags: tag1, tag2 #}
        {# @description: This is a description #}
        Hello, {{ name }}!
        """)
        engine = TemplateEngine(str(templates_dir))
        engine._load_template_metadata()
        
        # Act
        metadata = engine.get_template_metadata("test.j2")
        
        # Assert
        assert metadata["tags"] == ["tag1", "tag2"]
        assert metadata["description"] == "This is a description"
    
    def test_get_templates_by_tag(self, tmp_path):
        """Test get_templates_by_tag."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_file1 = templates_dir / "test1.j2"
        template_file1.write_text("""
        {# @tags: tag1, tag2 #}
        Hello, {{ name }}!
        """)
        template_file2 = templates_dir / "test2.j2"
        template_file2.write_text("""
        {# @tags: tag2, tag3 #}
        Hello, {{ name }}!
        """)
        engine = TemplateEngine(str(templates_dir))
        engine._load_template_metadata()
        
        # Act
        templates = engine.get_templates_by_tag("tag2")
        
        # Assert
        assert len(templates) == 2
        assert "test1.j2" in templates
        assert "test2.j2" in templates


def test_get_template_engine():
    """Test get_template_engine."""
    # Act
    engine1 = get_template_engine()
    engine2 = get_template_engine()
    
    # Assert
    assert engine1 is engine2  # Singleton


@patch("augment_adam.utils.template_engine.get_template_engine")
def test_render_template(mock_get_template_engine):
    """Test render_template."""
    # Arrange
    mock_engine = Mock()
    mock_get_template_engine.return_value = mock_engine
    mock_engine.render_template.return_value = "rendered template"
    
    # Act
    result = render_template("test.j2", {"key": "value"})
    
    # Assert
    mock_engine.render_template.assert_called_once_with("test.j2", {"key": "value"})
    assert result == "rendered template"


@patch("augment_adam.utils.template_engine.get_template_engine")
def test_render_code_template(mock_get_template_engine):
    """Test render_code_template."""
    # Arrange
    mock_engine = Mock()
    mock_get_template_engine.return_value = mock_engine
    mock_engine.render_code_template.return_value = "rendered template"
    
    # Act
    result = render_code_template("test.j2", {"key": "value"})
    
    # Assert
    mock_engine.render_code_template.assert_called_once_with("test.j2", {"key": "value"})
    assert result == "rendered template"


@patch("augment_adam.utils.template_engine.get_template_engine")
def test_render_test_template(mock_get_template_engine):
    """Test render_test_template."""
    # Arrange
    mock_engine = Mock()
    mock_get_template_engine.return_value = mock_engine
    mock_engine.render_test_template.return_value = "rendered template"
    
    # Act
    result = render_test_template("test.j2", {"key": "value"})
    
    # Assert
    mock_engine.render_test_template.assert_called_once_with("test.j2", {"key": "value"})
    assert result == "rendered template"


@patch("augment_adam.utils.template_engine.get_template_engine")
def test_render_doc_template(mock_get_template_engine):
    """Test render_doc_template."""
    # Arrange
    mock_engine = Mock()
    mock_get_template_engine.return_value = mock_engine
    mock_engine.render_doc_template.return_value = "rendered template"
    
    # Act
    result = render_doc_template("test.j2", {"key": "value"})
    
    # Assert
    mock_engine.render_doc_template.assert_called_once_with("test.j2", {"key": "value"})
    assert result == "rendered template"


@patch("augment_adam.utils.template_engine.get_template_engine")
def test_get_docstring(mock_get_template_engine):
    """Test get_docstring."""
    # Arrange
    mock_engine = Mock()
    mock_get_template_engine.return_value = mock_engine
    mock_engine.get_docstring.return_value = "docstring"
    
    # Act
    result = get_docstring("function", "summary", key="value")
    
    # Assert
    mock_engine.get_docstring.assert_called_once_with("function", "summary", key="value")
    assert result == "docstring"
