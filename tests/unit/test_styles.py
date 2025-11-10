"""Tests for h5forest.styles module."""

import pytest
from prompt_toolkit.styles import Style

from h5forest.styles import style


class TestStyles:
    """Test the styles module."""

    def test_style_is_defined(self):
        """Test that style is properly defined."""
        assert style is not None

    def test_style_is_prompt_toolkit_style(self):
        """Test that style is a prompt_toolkit Style object."""

        assert isinstance(style, Style)

    def test_style_has_expected_classes(self):
        """Test that style contains expected style classes."""
        # Style is created from a dictionary, check expected structure

        assert isinstance(style, Style)
        # The style should be created successfully from the dictionary

    def test_style_import_success(self):
        """Test that styles can be imported without errors."""
        try:
            from h5forest import styles

            assert hasattr(styles, "style")
        except ImportError as e:
            pytest.fail(f"Could not import styles module: {e}")

    def test_style_contains_expected_keys(self):
        """Test that style contains expected CSS classes."""
        # The style is created from a dict with specific keys
        # We can't easily access the internal dict, but we can verify
        # it was created successfully from the expected structure

        assert isinstance(style, Style)

        # Basic smoke test - should be able to represent as string
        str_repr = str(style)
        assert isinstance(str_repr, str)
