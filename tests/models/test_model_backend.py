#!/usr/bin/env python3
"""
Tests for the ModelBackend interface.

This module tests the ModelBackend interface and ensures that
all required methods are defined.
"""

import unittest
from abc import ABC, abstractmethod
import inspect

from src.models.model_backend import ModelBackend


class TestModelBackend(unittest.TestCase):
    """Tests for the ModelBackend interface."""

    def test_interface_methods(self):
        """Test that all required methods are defined in the interface."""
        # Get all abstract methods
        abstract_methods = [
            name for name, method in inspect.getmembers(ModelBackend)
            if inspect.isfunction(method) and getattr(method, "__isabstractmethod__", False)
        ]

        # Check that all required methods are abstract
        required_methods = [
            "__init__",
            "generate",
            "generate_stream",
            "get_token_count",
            "embed",
            "batch_embed",
            "get_model_info",
            "is_available",
            "format_prompt",
            "share_model"
        ]

        for method in required_methods:
            self.assertIn(method, abstract_methods,
                          f"Method {method} should be abstract in ModelBackend")

    def test_method_signatures(self):
        """Test that method signatures are correct."""
        # Check __init__ signature
        init_params = inspect.signature(ModelBackend.__init__).parameters
        self.assertIn("model_id", init_params)
        self.assertIn("model_config", init_params)
        self.assertIn("cache_dir", init_params)

        # Check generate signature
        generate_params = inspect.signature(ModelBackend.generate).parameters
        self.assertIn("prompt", generate_params)
        self.assertIn("system_prompt", generate_params)
        self.assertIn("max_tokens", generate_params)
        self.assertIn("temperature", generate_params)
        self.assertIn("top_p", generate_params)
        self.assertIn("stop", generate_params)

        # Check generate_stream signature
        stream_params = inspect.signature(ModelBackend.generate_stream).parameters
        self.assertIn("prompt", stream_params)
        self.assertIn("system_prompt", stream_params)
        self.assertIn("max_tokens", stream_params)
        self.assertIn("temperature", stream_params)
        self.assertIn("top_p", stream_params)
        self.assertIn("stop", stream_params)

        # Check embed signature
        embed_params = inspect.signature(ModelBackend.embed).parameters
        self.assertIn("text", embed_params)

        # Check batch_embed signature
        batch_embed_params = inspect.signature(ModelBackend.batch_embed).parameters
        self.assertIn("texts", batch_embed_params)

        # Check format_prompt signature
        format_prompt_params = inspect.signature(ModelBackend.format_prompt).parameters
        self.assertIn("prompt", format_prompt_params)
        self.assertIn("system_prompt", format_prompt_params)

        # Check share_model signature
        share_model_params = inspect.signature(ModelBackend.share_model).parameters
        self.assertIn("target_backend", share_model_params)


if __name__ == "__main__":
    unittest.main()
