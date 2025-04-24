"""Unit tests for the migration script.

This module contains tests for the migration script that helps users
migrate from dukat to augment_adam.

Note: The tests in this file intentionally contain references to 'dukat'
as they are testing the migration script that replaces these references.
"""

import os
import tempfile
import unittest
from pathlib import Path

# Import the migration script
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))
from migrate import update_file


class TestMigrationScript(unittest.TestCase):
    """Test the migration script."""

    def test_update_imports(self):
        """Test updating imports."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
            f.write("from dukat.core import Assistant\n")
            f.write("import dukat.memory\n")
            f.flush()

            # Update the file
            update_file(f.name)

            # Read the updated content
            with open(f.name, "r") as updated_f:
                content = updated_f.read()

            # Check that imports were updated
            self.assertIn("from augment_adam.core import Assistant", content)
            self.assertIn("import augment_adam.memory", content)

            # Clean up
            os.unlink(f.name)

    def test_update_paths(self):
        """Test updating paths."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
            f.write('config_path = "~/.dukat/config.yaml"\n')
            f.write('memory_path = "~/.dukat/memory"\n')
            f.flush()

            # Update the file
            update_file(f.name)

            # Read the updated content
            with open(f.name, "r") as updated_f:
                content = updated_f.read()

            # Check that paths were updated
            self.assertIn('config_path = "~/.augment_adam/config.yaml"', content)
            self.assertIn('memory_path = "~/.augment_adam/memory"', content)

            # Clean up
            os.unlink(f.name)

    def test_update_collection_names(self):
        """Test updating collection names."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
            f.write('collection_name = "dukat_memory"\n')
            f.write("collection_name = 'dukat_concepts'\n")
            f.flush()

            # Update the file
            update_file(f.name)

            # Read the updated content
            with open(f.name, "r") as updated_f:
                content = updated_f.read()

            # Check that collection names were updated
            self.assertIn('collection_name = "augment_adam_memory"', content)
            self.assertIn("collection_name = 'augment_adam_concepts'", content)

            # Clean up
            os.unlink(f.name)

    def test_update_class_names(self):
        """Test updating class names."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
            f.write("from dukat.core.errors import DukatError\n")
            f.write("raise DukatError('Something went wrong')\n")
            f.write("executor = ParallelTaskExecutor()\n")
            f.write("registry = PluginRegistry()\n")
            f.write("registry = get_plugin_registry()\n")
            f.flush()

            # Update the file
            update_file(f.name)

            # Read the updated content
            with open(f.name, "r") as updated_f:
                content = updated_f.read()

            # Check that class names were updated
            self.assertIn("from augment_adam.core.errors import AugmentAdamError", content)
            self.assertIn("raise AugmentAdamError('Something went wrong')", content)
            self.assertIn("executor = ParallelExecutor()", content)
            self.assertIn("registry = PluginManager()", content)
            self.assertIn("registry = get_plugin_manager()", content)

            # Clean up
            os.unlink(f.name)

    def test_update_cli_commands(self):
        """Test updating CLI commands."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as f:
            f.write("# CLI Usage\n")
            f.write("```bash\n")
            f.write("dukat\n")
            f.write("dukat web\n")
            f.write("```\n")
            f.flush()

            # Update the file
            update_file(f.name)

            # Read the updated content
            with open(f.name, "r") as updated_f:
                content = updated_f.read()

            # Check that CLI commands were updated
            self.assertIn("augment-adam", content)
            self.assertIn("augment-adam web", content)

            # Clean up
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
