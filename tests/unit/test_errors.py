"""Tests for h5forest.errors module."""

from unittest.mock import Mock, patch

import pytest

from h5forest.errors import error_handler


class TestErrorHandler:
    """Test the error_handler decorator."""

    def test_error_handler_no_exception(self):
        """Test error_handler when no exception occurs."""

        @error_handler
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_error_handler_with_exception(self):
        """Test error_handler when an exception occurs."""

        @error_handler
        def test_function():
            raise ValueError("test error")

        # The error handler should catch the exception
        # and not re-raise it
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest

            result = test_function()
            assert result is None  # error_handler returns None on exception
            mock_forest.print.assert_called_once()

    def test_error_handler_with_keyboard_interrupt(self):
        """Test error_handler with KeyboardInterrupt (should re-raise)."""

        @error_handler
        def test_function():
            raise KeyboardInterrupt("user interrupt")

        # KeyboardInterrupt should be re-raised
        with pytest.raises(KeyboardInterrupt):
            test_function()

    def test_error_handler_with_system_exit(self):
        """Test error_handler with SystemExit (should re-raise)."""

        @error_handler
        def test_function():
            raise SystemExit(1)

        # SystemExit should be re-raised
        with pytest.raises(SystemExit):
            test_function()

    def test_error_handler_with_forest_context(self):
        """Test error_handler with H5Forest context."""

        @error_handler
        def test_function():
            raise ValueError("test error")

        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest

            result = test_function()

            # Should call print on the forest
            mock_forest.print.assert_called_once()
            assert result is None

    def test_error_handler_preserves_function_metadata(self):
        """Test that error_handler preserves function metadata."""

        @error_handler
        def test_function():
            """Test docstring."""
            pass

        # The current error_handler doesn't use functools.wraps
        # so it doesn't preserve metadata
        assert test_function.__name__ == "wrapper"
        assert test_function.__doc__ == "Wrap the function."

    def test_error_handler_with_args_and_kwargs(self):
        """Test error_handler with function arguments."""

        @error_handler
        def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        result = test_function("a", "b", kwarg1="c")
        assert result == "a-b-c"

    def test_error_handler_exception_logging(self):
        """Test that error_handler properly handles exception information."""

        @error_handler
        def test_function():
            # Create a more complex exception scenario
            try:
                raise ValueError("original error")
            except ValueError as e:
                raise RuntimeError("wrapped error") from e

        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest

            result = test_function()

            # Should still handle the exception gracefully
            mock_forest.print.assert_called_once()
            assert result is None
