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
        app.prompt_yn = MagicMock()
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

    def test_prompt_for_chunked_dataset_not_chunked(self, mock_app, mock_node):
        """Test prompt with non-chunked dataset proceeds immediately."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_node, callback)

        # Should call callback immediately without prompting
        callback.assert_called_once_with(use_chunks=False, load_all=True)
        mock_app.prompt_yn.assert_not_called()

    def test_prompt_for_chunked_dataset_yes_to_chunks(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says chunk-by-chunk."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Should prompt for chunk-by-chunk processing
        mock_app.prompt_yn.assert_called_once()
        on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y'
        on_yes()

        # Should call callback with use_chunks=True
        callback.assert_called_once_with(use_chunks=True, load_all=False)
        mock_app.default_focus.assert_called()
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_no_then_yes(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says no then yes."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get first prompt callbacks
        on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to chunk-by-chunk
        on_no()

        # Should prompt again for loading all
        assert mock_app.prompt_yn.call_count == 2
        second_on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y' to load all
        second_on_yes()

        # Should call callback with load_all=True
        callback.assert_called_once_with(use_chunks=False, load_all=True)
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_chunked_dataset_no_then_no(
        self, mock_app, mock_chunked_node
    ):
        """Test prompt with chunked dataset, user says no twice (abort)."""
        callback = MagicMock()

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Get first prompt callbacks
        first_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to chunk-by-chunk
        first_on_no()

        # Get second prompt callbacks
        second_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to load all
        second_on_no()

        # Should not call the operation callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_large_dataset_file_error(self, mock_app, mock_node):
        """Test prompt with file access error falls back to nbytes."""
        callback = MagicMock()
        # Create a node with large nbytes
        mock_node.nbytes = 2 * 10**9  # 2 GB
        # Make filepath invalid to trigger exception
        mock_node.filepath = "/nonexistent/file.h5"

        prompt_for_large_dataset(mock_app, mock_node, callback)

        # Should still prompt because nbytes > 1GB
        mock_app.prompt_yn.assert_called_once()

    def test_prompt_for_dataset_operation_chunked_load_all(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user chooses load all."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_chunked_node, callback)

        # Get first prompt callbacks
        first_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to chunk-by-chunk
        first_on_no()

        # Get second prompt callbacks
        second_on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y' to load all
        second_on_yes()

        # Should call callback with use_chunks=False
        callback.assert_called_once_with(use_chunks=False)

    def test_prompt_for_large_dataset_small(self, mock_app, mock_node):
        """Test prompt with small dataset proceeds immediately."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_node, callback)

        # Should call callback immediately without prompting
        callback.assert_called_once()
        mock_app.prompt_yn.assert_not_called()

    def test_prompt_for_large_dataset_large_yes(
        self, mock_app, mock_large_node
    ):
        """Test prompt with large dataset, user confirms."""
        callback = MagicMock()

        prompt_for_large_dataset(mock_app, mock_large_node, callback)

        # Should prompt for confirmation
        mock_app.prompt_yn.assert_called_once()
        on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y'
        on_yes()

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

        # Get prompt callbacks
        on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n'
        on_no()

        # Should not call callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
        mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_dataset_operation_not_chunked_small(
        self, mock_app, mock_node
    ):
        """Test combined prompt with non-chunked small dataset."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_node, callback)

        # Should call callback immediately
        callback.assert_called_once_with(use_chunks=False)
        mock_app.prompt_yn.assert_not_called()

    def test_prompt_for_dataset_operation_chunked_yes(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user chooses chunks."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_chunked_node, callback)

        # Should prompt for chunked processing
        mock_app.prompt_yn.assert_called_once()
        on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y' to chunk-by-chunk
        on_yes()

        # Should call callback with use_chunks=True
        callback.assert_called_once_with(use_chunks=True)

    def test_prompt_for_dataset_operation_chunked_no_abort(
        self, mock_app, mock_chunked_node
    ):
        """Test combined prompt with chunked dataset, user aborts."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_chunked_node, callback)

        # Get first prompt callbacks
        first_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to chunk-by-chunk
        first_on_no()

        # Get second prompt callbacks
        second_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to load all
        second_on_no()

        # Should not call the operation callback
        callback.assert_not_called()
        mock_app.print.assert_called_with("Operation aborted.")
