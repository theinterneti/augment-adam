"""Tests for the file manager plugin.

This module contains tests for the file manager plugin functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
import json
import yaml
import hashlib
from pathlib import Path

import pytest

from dukat.plugins.file_manager import FileManagerPlugin


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def plugin(temp_dir):
    """Create a file manager plugin for testing."""
    return FileManagerPlugin(base_dir=temp_dir)


def test_plugin_init(temp_dir):
    """Test that the plugin initializes correctly."""
    plugin = FileManagerPlugin(base_dir=temp_dir)

    assert plugin.name == "file_manager"
    assert plugin.description == "Plugin for file operations"
    assert plugin.version == "0.1.0"
    assert plugin.base_dir == temp_dir


def test_get_full_path(plugin, temp_dir):
    """Test that the plugin gets full paths correctly."""
    # Test with an empty path
    full_path = plugin._get_full_path("")
    assert full_path == temp_dir

    # Test with a relative path
    full_path = plugin._get_full_path("test.txt")
    assert full_path == os.path.join(temp_dir, "test.txt")

    # Test with a subdirectory
    full_path = plugin._get_full_path("subdir/test.txt")
    assert full_path == os.path.join(temp_dir, "subdir/test.txt")

    # Test with an absolute path
    abs_path = os.path.abspath("/tmp/test.txt")
    full_path = plugin._get_full_path(abs_path)
    assert full_path == abs_path


def test_is_safe_path(plugin, temp_dir):
    """Test that the plugin checks safe paths correctly."""
    # Test with a path within the base directory
    assert plugin._is_safe_path(os.path.join(temp_dir, "test.txt")) is True

    # Test with a path outside the base directory
    assert plugin._is_safe_path("/tmp/test.txt") is False

    # Test with a path that tries to escape the base directory
    assert plugin._is_safe_path(os.path.join(temp_dir, "../test.txt")) is False


def test_write_and_read_text_file(plugin, temp_dir):
    """Test writing and reading a text file."""
    # Write a text file
    result = plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "test.txt")
    assert result["size"] > 0

    # Check that the file exists
    assert os.path.exists(os.path.join(temp_dir, "test.txt"))

    # Read the text file
    result = plugin.execute(
        action="read",
        path="test.txt",
    )

    assert "error" not in result
    assert result["content"] == "Hello, world!"
    assert result["mime_type"] == "text/plain"
    assert result["encoding"] == "utf-8"
    assert result["size"] > 0


def test_write_and_read_json_file(plugin, temp_dir):
    """Test writing and reading a JSON file."""
    # Write a JSON file
    data = {"name": "Test", "value": 42}
    result = plugin.execute(
        action="write",
        path="test.json",
        content=json.dumps(data),
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "test.json")
    assert result["size"] > 0

    # Check that the file exists
    assert os.path.exists(os.path.join(temp_dir, "test.json"))

    # Read the JSON file
    result = plugin.execute(
        action="read",
        path="test.json",
    )

    assert "error" not in result
    assert result["content"] == data
    assert result["mime_type"] == "application/json"
    assert result["encoding"] == "utf-8"
    assert result["size"] > 0


def test_write_and_read_yaml_file(plugin, temp_dir):
    """Test writing and reading a YAML file."""
    # Write a YAML file
    data = {"name": "Test", "value": 42}
    result = plugin.execute(
        action="write",
        path="test.yaml",
        content=yaml.dump(data),
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "test.yaml")
    assert result["size"] > 0

    # Check that the file exists
    assert os.path.exists(os.path.join(temp_dir, "test.yaml"))

    # Read the YAML file
    result = plugin.execute(
        action="read",
        path="test.yaml",
    )

    assert "error" not in result
    # The file_manager.py implementation correctly parses YAML files
    assert isinstance(result["content"], dict)
    assert result["content"]["name"] == "Test"
    assert result["content"]["value"] == 42
    assert result["mime_type"] == "application/yaml"
    assert result["encoding"] == "utf-8"
    assert result["size"] > 0


def test_append_file(plugin, temp_dir):
    """Test appending to a file."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, ",
    )

    # Append to the file
    result = plugin.execute(
        action="append",
        path="test.txt",
        content="world!",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "test.txt")
    assert result["size"] > 0

    # Read the file
    result = plugin.execute(
        action="read",
        path="test.txt",
    )

    assert "error" not in result
    assert result["content"] == "Hello, world!"


def test_delete_file(plugin, temp_dir):
    """Test deleting a file."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    # Check that the file exists
    assert os.path.exists(os.path.join(temp_dir, "test.txt"))

    # Delete the file
    result = plugin.execute(
        action="delete",
        path="test.txt",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "test.txt")

    # Check that the file no longer exists
    assert not os.path.exists(os.path.join(temp_dir, "test.txt"))


def test_list_directory(plugin, temp_dir):
    """Test listing a directory."""
    # Create some files and directories
    plugin.execute(action="write", path="file1.txt", content="File 1")
    plugin.execute(action="write", path="file2.txt", content="File 2")
    plugin.execute(action="mkdir", path="subdir")
    plugin.execute(action="write", path="subdir/file3.txt", content="File 3")

    # List the directory
    result = plugin.execute(
        action="list",
        path="",
    )

    assert "error" not in result
    assert result["path"] == temp_dir
    assert result["count"] == 3

    # Check that the items are correct
    items = result["items"]
    assert len(items) == 3

    # Find each item
    file1 = next((item for item in items if item["name"] == "file1.txt"), None)
    file2 = next((item for item in items if item["name"] == "file2.txt"), None)
    subdir = next((item for item in items if item["name"] == "subdir"), None)

    assert file1 is not None
    assert file1["type"] == "file"
    assert file1["size"] > 0

    assert file2 is not None
    assert file2["type"] == "file"
    assert file2["size"] > 0

    assert subdir is not None
    assert subdir["type"] == "directory"

    # List the directory recursively
    result = plugin.execute(
        action="list",
        path="",
        recursive=True,
    )

    assert "error" not in result
    assert result["path"] == temp_dir
    # The count should match the number of items
    assert result["count"] == 4

    # Check that the items are correct
    items = result["items"]
    assert len(items) == 4  # 3 files + 1 directory

    # Find the subdirectory file
    subdir_file = next((item for item in items if item["path"] == os.path.join(
        "subdir", "file3.txt")), None)
    assert subdir_file is not None
    assert subdir_file["type"] == "file"
    assert subdir_file["size"] > 0


def test_file_exists(plugin, temp_dir):
    """Test checking if a file exists."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    # Create a directory
    plugin.execute(
        action="mkdir",
        path="subdir",
    )

    # Check if the file exists
    result = plugin.execute(
        action="exists",
        path="test.txt",
    )

    assert "error" not in result
    assert result["exists"] is True
    assert result["type"] == "file"
    assert result["path"] == os.path.join(temp_dir, "test.txt")
    assert result["size"] > 0

    # Check if the directory exists
    result = plugin.execute(
        action="exists",
        path="subdir",
    )

    assert "error" not in result
    assert result["exists"] is True
    assert result["type"] == "directory"
    assert result["path"] == os.path.join(temp_dir, "subdir")

    # Check if a non-existent file exists
    result = plugin.execute(
        action="exists",
        path="nonexistent.txt",
    )

    assert "error" not in result
    assert result["exists"] is False
    assert result["path"] == os.path.join(temp_dir, "nonexistent.txt")


def test_file_info(plugin, temp_dir):
    """Test getting file information."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    # Create a directory
    plugin.execute(
        action="mkdir",
        path="subdir",
    )

    # Get file information
    result = plugin.execute(
        action="info",
        path="test.txt",
    )

    assert "error" not in result
    assert result["type"] == "file"
    assert result["path"] == os.path.join(temp_dir, "test.txt")
    assert result["size"] > 0
    assert result["mime_type"] == "text/plain"
    assert "created" in result
    assert "modified" in result
    assert "accessed" in result
    assert "permissions" in result
    assert "hash" in result

    # Verify the hash
    with open(os.path.join(temp_dir, "test.txt"), "rb") as f:
        content = f.read()
    expected_hash = hashlib.md5(content).hexdigest()
    assert result["hash"] == expected_hash

    # Get directory information
    result = plugin.execute(
        action="info",
        path="subdir",
    )

    assert "error" not in result
    assert result["type"] == "directory"
    assert result["path"] == os.path.join(temp_dir, "subdir")
    assert result["items"] == 0
    assert "created" in result
    assert "modified" in result
    assert "accessed" in result
    assert "permissions" in result


def test_make_directory(plugin, temp_dir):
    """Test creating a directory."""
    # Create a directory
    result = plugin.execute(
        action="mkdir",
        path="subdir",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "subdir")

    # Check that the directory exists
    assert os.path.exists(os.path.join(temp_dir, "subdir"))
    assert os.path.isdir(os.path.join(temp_dir, "subdir"))

    # Create a nested directory
    result = plugin.execute(
        action="mkdir",
        path="subdir/nested",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["path"] == os.path.join(temp_dir, "subdir/nested")

    # Check that the nested directory exists
    assert os.path.exists(os.path.join(temp_dir, "subdir/nested"))
    assert os.path.isdir(os.path.join(temp_dir, "subdir/nested"))


def test_copy_file(plugin, temp_dir):
    """Test copying a file."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    # Copy the file
    result = plugin.execute(
        action="copy",
        path="test.txt",
        dest="copy.txt",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["src_path"] == os.path.join(temp_dir, "test.txt")
    assert result["dest_path"] == os.path.join(temp_dir, "copy.txt")

    # Check that both files exist
    assert os.path.exists(os.path.join(temp_dir, "test.txt"))
    assert os.path.exists(os.path.join(temp_dir, "copy.txt"))

    # Read the copied file
    result = plugin.execute(
        action="read",
        path="copy.txt",
    )

    assert "error" not in result
    assert result["content"] == "Hello, world!"


def test_move_file(plugin, temp_dir):
    """Test moving a file."""
    # Write a text file
    plugin.execute(
        action="write",
        path="test.txt",
        content="Hello, world!",
    )

    # Move the file
    result = plugin.execute(
        action="move",
        path="test.txt",
        dest="moved.txt",
    )

    assert "error" not in result
    assert result["success"] is True
    assert result["src_path"] == os.path.join(temp_dir, "test.txt")
    assert result["dest_path"] == os.path.join(temp_dir, "moved.txt")

    # Check that the source file no longer exists
    assert not os.path.exists(os.path.join(temp_dir, "test.txt"))

    # Check that the destination file exists
    assert os.path.exists(os.path.join(temp_dir, "moved.txt"))

    # Read the moved file
    result = plugin.execute(
        action="read",
        path="moved.txt",
    )

    assert "error" not in result
    assert result["content"] == "Hello, world!"


def test_execute_with_invalid_action(plugin):
    """Test executing with an invalid action."""
    result = plugin.execute(
        action="invalid",
        path="test.txt",
    )

    assert "error" in result
    assert "Unknown action" in result["error"]


def test_execute_with_unsafe_path(plugin, temp_dir):
    """Test executing with an unsafe path."""
    result = plugin.execute(
        action="read",
        path="../unsafe.txt",
    )

    assert "error" in result
    assert "outside the base directory" in result["error"]


def test_execute_with_nonexistent_file(plugin):
    """Test executing with a non-existent file."""
    result = plugin.execute(
        action="read",
        path="nonexistent.txt",
    )

    assert "error" in result
    assert "does not exist" in result["error"]
