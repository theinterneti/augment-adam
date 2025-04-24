"""File manager plugin for the Dukat assistant.

This module provides a plugin for file operations, including
reading, writing, and managing files.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union, BinaryIO
import logging
import os
import shutil
from pathlib import Path
import json
import yaml
import csv
import tempfile
import mimetypes
import hashlib

from augment_adam.plugins.base import Plugin

logger = logging.getLogger(__name__)


class FileManagerPlugin(Plugin):
    """Plugin for file operations.

    This plugin provides functionality for reading, writing,
    and managing files.

    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
        base_dir: The base directory for file operations.
    """

    def __init__(
        self,
        base_dir: Optional[str] = None,
        version: str = "0.1.0",
    ):
        """Initialize the file manager plugin.

        Args:
            base_dir: The base directory for file operations.
            version: The version of the plugin.
        """
        super().__init__(
            name="file_manager",
            description="Plugin for file operations",
            version=version,
        )

        self.base_dir = base_dir or os.getcwd()

        # Register YAML mime type if not already registered
        mimetypes.add_type("application/yaml", ".yaml")
        mimetypes.add_type("application/yaml", ".yml")

        logger.info(
            f"Initialized file manager plugin with base_dir: {self.base_dir}")

    def execute(
        self,
        action: str,
        path: str,
        content: Optional[str] = None,
        encoding: str = "utf-8",
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a file operation.

        Args:
            action: The action to perform (read, write, delete, etc.).
            path: The path to the file or directory.
            content: The content to write to the file.
            encoding: The encoding to use for text files.
            **kwargs: Additional arguments for the action.

        Returns:
            The result of the operation.
        """
        # Normalize the path
        full_path = self._get_full_path(path)

        # Check if the path is within the base directory
        if not self._is_safe_path(full_path):
            error_msg = f"Path {path} is outside the base directory"
            logger.error(error_msg)
            return {"error": error_msg}

        # Perform the action
        try:
            if action == "read":
                return self.read_file(full_path, encoding=encoding)
            elif action == "write":
                return self.write_file(full_path, content, encoding=encoding)
            elif action == "append":
                return self.append_file(full_path, content, encoding=encoding)
            elif action == "delete":
                return self.delete_file(full_path)
            elif action == "list":
                recursive = kwargs.get("recursive", False)
                include_hidden = kwargs.get("include_hidden", False)
                return self.list_directory(full_path, recursive=recursive, include_hidden=include_hidden)
            elif action == "exists":
                return self.file_exists(full_path)
            elif action == "info":
                return self.file_info(full_path)
            elif action == "mkdir":
                return self.make_directory(full_path)
            elif action == "copy":
                dest_path = self._get_full_path(kwargs.get("dest", ""))
                if not self._is_safe_path(dest_path):
                    error_msg = f"Destination path {kwargs.get('dest', '')} is outside the base directory"
                    logger.error(error_msg)
                    return {"error": error_msg}
                return self.copy_file(full_path, dest_path)
            elif action == "move":
                dest_path = self._get_full_path(kwargs.get("dest", ""))
                if not self._is_safe_path(dest_path):
                    error_msg = f"Destination path {kwargs.get('dest', '')} is outside the base directory"
                    logger.error(error_msg)
                    return {"error": error_msg}
                return self.move_file(full_path, dest_path)
            else:
                error_msg = f"Unknown action: {action}"
                logger.error(error_msg)
                return {"error": error_msg}

        except Exception as e:
            error_msg = f"Error performing {action} on {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _get_full_path(self, path: str) -> str:
        """Get the full path for a file or directory.

        Args:
            path: The relative path.

        Returns:
            The full path.
        """
        # Handle empty path
        if not path:
            return self.base_dir

        # Handle absolute paths
        if os.path.isabs(path):
            return path

        # Handle relative paths
        return os.path.join(self.base_dir, path)

    def _is_safe_path(self, path: str) -> bool:
        """Check if a path is within the base directory.

        Args:
            path: The path to check.

        Returns:
            True if the path is safe, False otherwise.
        """
        # Resolve the paths to handle symlinks and relative paths
        base_path = os.path.abspath(self.base_dir)
        full_path = os.path.abspath(path)

        # Check if the path is within the base directory
        return full_path.startswith(base_path)

    def read_file(
        self,
        path: str,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Read a file.

        Args:
            path: The path to the file.
            encoding: The encoding to use for text files.

        Returns:
            The content of the file.
        """
        # Check if the file exists
        if not os.path.exists(path):
            error_msg = f"File {path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        # Check if the path is a file
        if not os.path.isfile(path):
            error_msg = f"Path {path} is not a file"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # Detect the file type
            mime_type, _ = mimetypes.guess_type(path)

            # Handle different file types
            if mime_type and mime_type.startswith("text/"):
                # Text file
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()

                return {
                    "content": content,
                    "mime_type": mime_type,
                    "encoding": encoding,
                    "size": os.path.getsize(path),
                }

            elif mime_type and mime_type.startswith("application/json"):
                # JSON file
                with open(path, "r", encoding=encoding) as f:
                    content = json.load(f)

                return {
                    "content": content,
                    "mime_type": mime_type,
                    "encoding": encoding,
                    "size": os.path.getsize(path),
                }

            elif mime_type and (mime_type.startswith("application/yaml") or path.endswith((".yaml", ".yml"))):
                # YAML file
                with open(path, "r", encoding=encoding) as f:
                    content = yaml.safe_load(f)

                return {
                    "content": content,
                    "mime_type": mime_type or "application/yaml",
                    "encoding": encoding,
                    "size": os.path.getsize(path),
                }

            elif mime_type and mime_type.startswith("text/csv"):
                # CSV file
                rows = []
                with open(path, "r", encoding=encoding, newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows.append(row)

                return {
                    "content": rows,
                    "mime_type": mime_type,
                    "encoding": encoding,
                    "size": os.path.getsize(path),
                }

            else:
                # Binary file
                with open(path, "rb") as f:
                    content = f.read()

                # Calculate hash for binary files
                file_hash = hashlib.md5(content).hexdigest()

                return {
                    "content": f"Binary file ({os.path.getsize(path)} bytes, MD5: {file_hash})",
                    "mime_type": mime_type or "application/octet-stream",
                    "encoding": "binary",
                    "size": os.path.getsize(path),
                    "hash": file_hash,
                }

        except Exception as e:
            error_msg = f"Error reading file {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Write to a file.

        Args:
            path: The path to the file.
            content: The content to write to the file.
            encoding: The encoding to use for text files.

        Returns:
            The result of the operation.
        """
        # Create the directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            # Detect the file type
            mime_type, _ = mimetypes.guess_type(path)

            # Handle different file types
            if mime_type and mime_type.startswith("application/json"):
                # JSON file
                if isinstance(content, str):
                    # Parse the JSON string
                    try:
                        content_obj = json.loads(content)
                    except json.JSONDecodeError:
                        # If parsing fails, write as plain text
                        with open(path, "w", encoding=encoding) as f:
                            f.write(content)
                    else:
                        # Write the parsed JSON
                        with open(path, "w", encoding=encoding) as f:
                            json.dump(content_obj, f, indent=2)
                else:
                    # Write the object as JSON
                    with open(path, "w", encoding=encoding) as f:
                        json.dump(content, f, indent=2)

            elif mime_type and (mime_type.startswith("application/yaml") or path.endswith((".yaml", ".yml"))):
                # YAML file
                if isinstance(content, str):
                    # Try to parse the YAML string
                    try:
                        content_obj = yaml.safe_load(content)
                    except yaml.YAMLError:
                        # If parsing fails, write as plain text
                        with open(path, "w", encoding=encoding) as f:
                            f.write(content)
                    else:
                        # Write the parsed YAML
                        with open(path, "w", encoding=encoding) as f:
                            yaml.dump(content_obj, f, default_flow_style=False)
                else:
                    # Write the object as YAML
                    with open(path, "w", encoding=encoding) as f:
                        yaml.dump(content, f, default_flow_style=False)

            else:
                # Text file
                with open(path, "w", encoding=encoding) as f:
                    f.write(content)

            return {
                "success": True,
                "path": path,
                "size": os.path.getsize(path),
            }

        except Exception as e:
            error_msg = f"Error writing to file {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def append_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Append to a file.

        Args:
            path: The path to the file.
            content: The content to append to the file.
            encoding: The encoding to use for text files.

        Returns:
            The result of the operation.
        """
        # Create the directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            # Append to the file
            with open(path, "a", encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "path": path,
                "size": os.path.getsize(path),
            }

        except Exception as e:
            error_msg = f"Error appending to file {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file or directory.

        Args:
            path: The path to the file or directory.

        Returns:
            The result of the operation.
        """
        # Check if the path exists
        if not os.path.exists(path):
            error_msg = f"Path {path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # Delete the file or directory
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

            return {
                "success": True,
                "path": path,
            }

        except Exception as e:
            error_msg = f"Error deleting {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def list_directory(
        self,
        path: str,
        recursive: bool = False,
        include_hidden: bool = False,
    ) -> Dict[str, Any]:
        """List the contents of a directory.

        Args:
            path: The path to the directory.
            recursive: Whether to list subdirectories recursively.
            include_hidden: Whether to include hidden files and directories.

        Returns:
            The contents of the directory.
        """
        # Check if the path exists
        if not os.path.exists(path):
            error_msg = f"Path {path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        # Check if the path is a directory
        if not os.path.isdir(path):
            error_msg = f"Path {path} is not a directory"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # List the directory contents
            if recursive:
                items = []
                # First, collect all directories and files
                all_dirs = []
                all_files = []

                for root, dirs, files in os.walk(path):
                    # Skip hidden directories if not included
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]

                    # Add directories
                    for d in dirs:
                        # Skip hidden directories if not included
                        if not include_hidden and d.startswith("."):
                            continue

                        dir_path = os.path.join(root, d)
                        rel_path = os.path.relpath(dir_path, path)
                        all_dirs.append({
                            "name": d,
                            "path": rel_path,
                            "type": "directory",
                            "size": 0,
                        })

                    # Add files
                    for f in files:
                        # Skip hidden files if not included
                        if not include_hidden and f.startswith("."):
                            continue

                        file_path = os.path.join(root, f)
                        rel_path = os.path.relpath(file_path, path)
                        all_files.append({
                            "name": f,
                            "path": rel_path,
                            "type": "file",
                            "size": os.path.getsize(file_path),
                        })

                # Combine directories and files
                items = all_dirs + all_files
            else:
                items = []
                for item in os.listdir(path):
                    # Skip hidden items if not included
                    if not include_hidden and item.startswith("."):
                        continue

                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        items.append({
                            "name": item,
                            "path": item,
                            "type": "directory",
                            "size": 0,
                        })
                    else:
                        items.append({
                            "name": item,
                            "path": item,
                            "type": "file",
                            "size": os.path.getsize(item_path),
                        })

            return {
                "items": items,
                "path": path,
                "count": len(items),
            }

        except Exception as e:
            error_msg = f"Error listing directory {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def file_exists(self, path: str) -> Dict[str, Any]:
        """Check if a file or directory exists.

        Args:
            path: The path to the file or directory.

        Returns:
            Whether the file or directory exists.
        """
        exists = os.path.exists(path)

        if exists:
            if os.path.isfile(path):
                return {
                    "exists": True,
                    "type": "file",
                    "path": path,
                    "size": os.path.getsize(path),
                }
            else:
                return {
                    "exists": True,
                    "type": "directory",
                    "path": path,
                }
        else:
            return {
                "exists": False,
                "path": path,
            }

    def file_info(self, path: str) -> Dict[str, Any]:
        """Get information about a file or directory.

        Args:
            path: The path to the file or directory.

        Returns:
            Information about the file or directory.
        """
        # Check if the path exists
        if not os.path.exists(path):
            error_msg = f"Path {path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # Get file or directory information
            stat_info = os.stat(path)

            info = {
                "path": path,
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "permissions": stat_info.st_mode,
            }

            if os.path.isfile(path):
                info["type"] = "file"
                mime_type, _ = mimetypes.guess_type(path)
                info["mime_type"] = mime_type or "application/octet-stream"

                # Calculate hash for small files
                if stat_info.st_size < 10 * 1024 * 1024:  # 10 MB
                    with open(path, "rb") as f:
                        content = f.read()
                    info["hash"] = hashlib.md5(content).hexdigest()
            else:
                info["type"] = "directory"
                info["items"] = len(os.listdir(path))

            return info

        except Exception as e:
            error_msg = f"Error getting info for {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def make_directory(self, path: str) -> Dict[str, Any]:
        """Create a directory.

        Args:
            path: The path to the directory.

        Returns:
            The result of the operation.
        """
        try:
            # Create the directory
            os.makedirs(path, exist_ok=True)

            return {
                "success": True,
                "path": path,
            }

        except Exception as e:
            error_msg = f"Error creating directory {path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def copy_file(self, src_path: str, dest_path: str) -> Dict[str, Any]:
        """Copy a file or directory.

        Args:
            src_path: The path to the source file or directory.
            dest_path: The path to the destination file or directory.

        Returns:
            The result of the operation.
        """
        # Check if the source path exists
        if not os.path.exists(src_path):
            error_msg = f"Source path {src_path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # Create the destination directory if it doesn't exist
            dest_dir = os.path.dirname(dest_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            # Copy the file or directory
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
            else:
                shutil.copytree(src_path, dest_path)

            return {
                "success": True,
                "src_path": src_path,
                "dest_path": dest_path,
            }

        except Exception as e:
            error_msg = f"Error copying {src_path} to {dest_path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def move_file(self, src_path: str, dest_path: str) -> Dict[str, Any]:
        """Move a file or directory.

        Args:
            src_path: The path to the source file or directory.
            dest_path: The path to the destination file or directory.

        Returns:
            The result of the operation.
        """
        # Check if the source path exists
        if not os.path.exists(src_path):
            error_msg = f"Source path {src_path} does not exist"
            logger.error(error_msg)
            return {"error": error_msg}

        try:
            # Create the destination directory if it doesn't exist
            dest_dir = os.path.dirname(dest_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            # Move the file or directory
            shutil.move(src_path, dest_path)

            return {
                "success": True,
                "src_path": src_path,
                "dest_path": dest_path,
            }

        except Exception as e:
            error_msg = f"Error moving {src_path} to {dest_path}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
