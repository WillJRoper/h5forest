"""Tests for dataset prompt workflows."""

from unittest.mock import MagicMock

import pytest

from h5forest.dataset_prompts import (
    prompt_for_chunked_dataset,
    prompt_for_dataset_operation,
    prompt_for_large_dataset,
)


class TestDatasetPrompts:
    """Test cases for dataset prompt workflows."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()
        app.user_input = ""
        app.input = MagicMock()
        app.print = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()
        return app

    @pytest.fixture
    def mock_node(self):
        """Create a mock node for testing."""
        node = MagicMock()
        node.is_chunked = False
        node.filepath = "/test/file.h5"
        node.path = "/dataset"
        node.nbytes = 500 * 10**6  # 500 MB
        return node

    @pytest.fixture
    def mock_chunked_node(self):
        """Create a mock chunked node for testing."""
        node = MagicMock()
        node.is_chunked = True
        node.filepath = "/test/file.h5"
        node.path = "/dataset"
        node.nbytes = 500 * 10**6  # 500 MB
        return node

    @pytest.fixture
    def mock_large_node(self):
        """Create a mock large node for testing."""
        node = MagicMock()
        node.is_chunked = False
        node.filepath = "/test/file.h5"
        node.path = "/dataset"
        node.nbytes = 2 * 10**9  # 2 GB
        return node

    def test_prompt_for_chunked_dataset_not_chunked(
        self, mock_app, mock_node
    ):
        """Test prompt with non-chunked dataset proceeds immediately."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_node, callback)

        # Should call callback immediately without prompting
        callback.assert_called_once_with(use_chunks=False, load_all=True)
        mock_app.input.assert_not_called()

    def test_prompt_for_chunked_dataset_yes_to_chunks(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says yes to chunk-by-chunk."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Should prompt for chunk-by-chunk processing
        mock_app.input.assert_called_once()
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying yes
        mock_app.user_input = "y"
        prompt_callback()

        # Should call callback with use_chunks=True
        callback.assert_called_once_with(use_chunks=True, load_all=False)
        mock_app.default_focus.assert_called()
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_no_then_yes(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says no then yes to load all."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get first prompt callback
        first_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to chunk-by-chunk
        mock_app.user_input = "n"
        first_prompt_callback()

        # Should prompt again for loading all
        assert mock_app.input.call_count == 2
        second_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying yes to load all
        mock_app.user_input = "yes"
        second_prompt_callback()

        # Should call callback with load_all=True
        callback.assert_called_once_with(use_chunks=False, load_all=True)
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_no_then_no(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says no twice (abort)."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get first prompt callback
        first_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to chunk-by-chunk
        mock_app.user_input = "no"
        first_prompt_callback()

        # Get second prompt callback
        second_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to load all
        mock_app.user_input = "n"
        second_prompt_callback()

        # Should not call the operation callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_invalid_input_first_prompt(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with invalid input on first prompt."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get prompt callback
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate invalid input
        mock_app.user_input = "maybe"
        prompt_callback()

        # Should print error and not call callback
        callback.assert_not_called()
        mock_app.print.assert_called()
        assert "Invalid input" in mock_app.print.call_args[0][0]
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_invalid_input_second_prompt(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with invalid input on second prompt."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get first prompt callback
        first_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to chunk-by-chunk
        mock_app.user_input = "n"
        first_prompt_callback()

        # Get second prompt callback
        second_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate invalid input
        mock_app.user_input = "maybe"
        second_prompt_callback()

        # Should print error and not call callback
        callback.assert_not_called()
        mock_app.print.assert_called()
        assert "Invalid input" in mock_app.print.call_args[0][0]

    def test_prompt_for_large_dataset_file_error(self, mock_app, mock_node):
        """Test prompt with file access error falls back to nbytes."""
        callback = MagicMock()
        # Create a node with large nbytes
        mock_node.nbytes = 2 * 10**9  # 2 GB
        # Make filepath invalid to trigger exception
        mock_node.filepath = "/nonexistent/file.h5"

        prompt_for_large_dataset(mock_app, mock_node, callback)

        # Should still prompt because nbytes > 1GB
        mock_app.input.assert_called_once()

    def test_prompt_for_dataset_operation_chunked_load_all(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user chooses load all."""
        callback = MagicMock()

        prompt_for_dataset_operation(
            mock_app, mock_chunked_node, callback
        )

        # Get first prompt callback
        first_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to chunk-by-chunk
        mock_app.user_input = "no"
        first_prompt_callback()

        # Get second prompt callback
        second_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying yes to load all
        mock_app.user_input = "y"
        second_prompt_callback()

        # Should call callback with use_chunks=False
        callback.assert_called_once_with(use_chunks=False)

    def test_prompt_for_large_dataset_small(self, mock_app, mock_node):
        """Test prompt with small dataset proceeds immediately."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_node, callback)

        # Should call callback immediately without prompting
        callback.assert_called_once()
        mock_app.input.assert_not_called()

    def test_prompt_for_large_dataset_large_yes(
        self, mock_app, mock_large_node
    ):
        """Test prompt with large dataset, user confirms."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_large_node, callback)

        # Should prompt for confirmation
        mock_app.input.assert_called_once()
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user confirming
        mock_app.user_input = "yes"
        prompt_callback()

        # Should call callback
        callback.assert_called_once()
        mock_app.default_focus.assert_called()
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_large_dataset_large_no(
        self, mock_app, mock_large_node
    ):
        """Test prompt with large dataset, user declines."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_large_node, callback)

        # Get prompt callback
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user declining
        mock_app.user_input = "n"
        prompt_callback()

        # Should not call callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_large_dataset_invalid_input(
        self, mock_app, mock_large_node
    ):
        """Test large dataset prompt with invalid input."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_large_node, callback)

        # Get prompt callback
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate invalid input
        mock_app.user_input = "sure"
        prompt_callback()

        # Should print error and not call callback
        callback.assert_not_called()
        mock_app.print.assert_called()
        assert "Invalid input" in mock_app.print.call_args[0][0]

    def test_prompt_for_dataset_operation_not_chunked_small(
        self, mock_app, mock_node
    ):
        """Test combined prompt with non-chunked small dataset."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_node, callback)

        # Should call callback immediately
        callback.assert_called_once_with(use_chunks=False)
        mock_app.input.assert_not_called()

    def test_prompt_for_dataset_operation_chunked_yes(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user chooses chunks."""
        callback = MagicMock()

        prompt_for_dataset_operation(
            mock_app, mock_chunked_node, callback
        )

        # Should prompt for chunked processing
        mock_app.input.assert_called_once()
        prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying yes to chunk-by-chunk
        mock_app.user_input = "y"
        prompt_callback()

        # Should call callback with use_chunks=True
        callback.assert_called_once_with(use_chunks=True)

    def test_prompt_for_dataset_operation_chunked_no_abort(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user aborts."""
        callback = MagicMock()

        prompt_for_dataset_operation(
            mock_app, mock_chunked_node, callback
        )

        # Get first prompt callback
        first_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to chunk-by-chunk
        mock_app.user_input = "no"
        first_prompt_callback()

        # Get second prompt callback
        second_prompt_callback = mock_app.input.call_args[0][1]

        # Simulate user saying no to load all
        mock_app.user_input = "n"
        second_prompt_callback()

        # Should not call the operation callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
