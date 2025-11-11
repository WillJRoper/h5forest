"""Tests for dataset prompt workflows."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from h5forest.dataset_prompts import (
    prompt_for_chunked_dataset,
    prompt_for_chunking_preference,
    prompt_for_dataset_operation,
    prompt_for_large_dataset,
)


class TestDatasetPrompts:
    """Test cases for dataset prompt workflows."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()
        app.prompt_yn = MagicMock()
        app.print = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()
        add_config_mock(app)
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

    @patch("h5py.File")
    def test_prompt_for_chunked_dataset_with_file_access(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test prompt_for_chunked_dataset with successful file access."""
        callback = MagicMock()

        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = (100, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Should prompt with chunk count
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # The message should contain chunk count (100 chunks: 10x10)
        assert "100 chunks" in prompt_msg

    @patch("h5py.File")
    def test_prompt_for_chunked_dataset_without_chunks(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test prompt for chunked node when dataset.chunks is None."""
        callback = MagicMock()

        # Mock the h5py dataset without chunks
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = None  # No chunks

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        prompt_for_chunked_dataset(mock_app, mock_chunked_node, callback)

        # Should prompt with "1 chunks" since chunks is None
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # Message should contain "1 chunks" when chunks is None
        assert "1 chunks" in prompt_msg

    @patch("h5py.File")
    def test_prompt_for_large_dataset_with_file_access(
        self, mock_h5py_file, mock_app, mock_large_node
    ):
        """Test prompt_for_large_dataset with successful file access."""
        callback = MagicMock()

        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 250000000  # 250M elements
        mock_dataset.dtype.itemsize = 8  # 8 bytes each = 2GB total

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        prompt_for_large_dataset(mock_app, mock_large_node, callback)

        # Should prompt because size > 1GB
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        assert "2.00 GB" in prompt_msg

    def test_prompt_for_dataset_operation_abort_path(
        self, mock_app, mock_chunked_node
    ):
        """Test the abort path in prompt_for_dataset_operation."""
        callback = MagicMock()

        prompt_for_dataset_operation(mock_app, mock_chunked_node, callback)

        # Get first prompt callbacks
        first_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to chunk-by-chunk
        first_on_no()

        # Get second prompt callbacks
        second_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' to load all (abort)
        second_on_no()

        # Should print abort message and return to normal mode
        assert mock_app.print.call_count >= 1
        abort_calls = [
            call
            for call in mock_app.print.call_args_list
            if "Operation aborted" in str(call)
        ]
        assert len(abort_calls) >= 1
        mock_app.return_to_normal_mode.assert_called()

    def test_after_chunk_prompt_callback_abort(self, mock_app):
        """Test after_chunk_prompt callback with load_all=False."""
        from h5forest.dataset_prompts import prompt_for_dataset_operation

        callback = MagicMock()
        mock_node = MagicMock()
        mock_node.is_chunked = False

        # Create a reference to after_chunk_prompt by capturing it
        captured_callback = None

        def capture_callback(
            app, node, operation_callback, return_to_normal=True
        ):
            nonlocal captured_callback
            captured_callback = operation_callback
            # Don't call the original, just capture the callback

        # Patch to capture the callback
        with patch(
            "h5forest.dataset_prompts.prompt_for_chunked_dataset",
            side_effect=capture_callback,
        ):
            prompt_for_dataset_operation(mock_app, mock_node, callback)

        # Now call the captured callback with use_chunks=False, load_all=False
        if captured_callback:
            captured_callback(use_chunks=False, load_all=False)

            # Should print abort message
            mock_app.print.assert_called_with("Operation aborted.")
            mock_app.return_to_normal_mode.assert_called()

    def test_prompt_for_dataset_operation_with_always_chunk(
        self, mock_app, mock_node
    ):
        """Test dataset operation when always_chunk config is enabled."""
        # Configure mock to enable always_chunk
        mock_app.config.always_chunk_datasets.return_value = True

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call the function
        prompt_for_dataset_operation(mock_app, mock_node, callback)

        # Should call the callback immediately with use_chunks=True
        callback.assert_called_once_with(use_chunks=True)

        # Should not show any prompts
        mock_app.prompt_yn.assert_not_called()

    def test_prompt_for_chunking_preference_always_chunk(
        self, mock_app, mock_node
    ):
        """Test chunking preference with always_chunk config enabled."""
        # Configure mock to enable always_chunk
        mock_app.config.always_chunk_datasets.return_value = True

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of nodes
        prompt_for_chunking_preference(mock_app, [mock_node], callback)

        # Should call the callback immediately with use_chunks=True
        callback.assert_called_once_with(use_chunks=True)

        # Should not show any prompts
        mock_app.prompt_yn.assert_not_called()

    def test_prompt_for_chunking_preference_no_chunked_nodes(
        self, mock_app, mock_node
    ):
        """Test chunking preference with no chunked nodes."""
        # Ensure node is not chunked
        mock_node.is_chunked = False

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of non-chunked nodes
        prompt_for_chunking_preference(mock_app, [mock_node], callback)

        # Should call the callback immediately with use_chunks=False
        callback.assert_called_once_with(use_chunks=False)

        # Should not show any prompts
        mock_app.prompt_yn.assert_not_called()

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_with_chunked_nodes(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test chunking preference with chunked nodes."""
        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = (100, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of chunked nodes
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Should prompt user
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # The message should contain chunk count
        assert "100 chunks" in prompt_msg

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_user_says_yes(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test chunking preference when user chooses to use chunks."""
        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = (100, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of chunked nodes
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Get the yes callback
        on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y'
        on_yes()

        # Should call callback with use_chunks=True
        callback.assert_called_once_with(use_chunks=True)
        mock_app.default_focus.assert_called()

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_user_says_no(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test chunking preference when user chooses to load all."""
        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = (100, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of chunked nodes
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Get the no callback from first prompt
        on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' (triggers second prompt)
        on_no()

        # Should have prompted again
        assert mock_app.prompt_yn.call_count == 2

        # Get the yes callback from second prompt
        second_on_yes = mock_app.prompt_yn.call_args[0][1]

        # Simulate user pressing 'y' on second prompt
        second_on_yes()

        # Should call callback with use_chunks=False
        callback.assert_called_once_with(use_chunks=False)
        mock_app.default_focus.assert_called()

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_multiple_nodes(
        self, mock_h5py_file, mock_app
    ):
        """Test chunking preference with multiple chunked nodes."""
        # Create two chunked nodes
        node1 = MagicMock()
        node1.is_chunked = True
        node1.filepath = "/test/file.h5"
        node1.path = "/dataset1"
        node1.nbytes = 100 * 10**6

        node2 = MagicMock()
        node2.is_chunked = True
        node2.filepath = "/test/file.h5"
        node2.path = "/dataset2"
        node2.nbytes = 200 * 10**6

        # Mock the h5py datasets
        mock_dataset1 = Mock()
        mock_dataset1.size = 1000000
        mock_dataset1.dtype.itemsize = 8
        mock_dataset1.shape = (1000, 1000)
        mock_dataset1.chunks = (100, 100)

        mock_dataset2 = Mock()
        mock_dataset2.size = 2000000
        mock_dataset2.dtype.itemsize = 8
        mock_dataset2.shape = (2000, 1000)
        mock_dataset2.chunks = (200, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(
            side_effect=lambda key: {
                "/dataset1": mock_dataset1,
                "/dataset2": mock_dataset2,
            }[key]
        )
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with multiple nodes
        prompt_for_chunking_preference(mock_app, [node1, node2], callback)

        # Should prompt user with combined information
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # Message should contain total footprint (0.024 GB ≈ 0.02 GB)
        # and total chunk count (100 + 100 = 200)
        assert "0.02 GB" in prompt_msg
        assert "200 chunks" in prompt_msg

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_user_aborts(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test chunking preference when user aborts operation."""
        # Mock the h5py dataset
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = (100, 100)

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a list of chunked nodes
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Get the no callback from first prompt
        on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' (triggers second prompt)
        on_no()

        # Should have prompted again
        assert mock_app.prompt_yn.call_count == 2

        # Get the no callback from second prompt
        second_on_no = mock_app.prompt_yn.call_args[0][2]

        # Simulate user pressing 'n' on second prompt (abort)
        second_on_no()

        # Should NOT call the operation callback
        callback.assert_not_called()
        # Should print abort message
        mock_app.print.assert_called_with("Operation aborted.")
        mock_app.default_focus.assert_called()

    def test_prompt_for_chunking_preference_file_access_error(
        self, mock_app, mock_chunked_node
    ):
        """Test chunking preference when file access fails."""
        # Don't patch h5py.File, let it fail naturally
        # This will trigger the exception handler

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a chunked node (will fail to open file)
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Should still prompt user (using nbytes estimate)
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # Should contain size estimate from nbytes
        assert "0.50 GB" in prompt_msg
        # Should not contain chunk count (unknown)
        assert "chunks)" not in prompt_msg

    @patch("h5py.File")
    def test_prompt_for_chunking_preference_chunks_none(
        self, mock_h5py_file, mock_app, mock_chunked_node
    ):
        """Test chunking preference when dataset.chunks is None."""
        # Mock the h5py dataset with chunks=None
        mock_dataset = Mock()
        mock_dataset.size = 1000000
        mock_dataset.dtype.itemsize = 8
        mock_dataset.shape = (1000, 1000)
        mock_dataset.chunks = None  # No chunks defined

        # Mock h5py.File context manager
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.__getitem__ = Mock(return_value=mock_dataset)
        mock_h5py_file.return_value = mock_file

        # Create a callback to track if it was called
        callback = MagicMock()

        # Call with a chunked node
        prompt_for_chunking_preference(mock_app, [mock_chunked_node], callback)

        # Should prompt user without chunk count
        mock_app.prompt_yn.assert_called_once()
        prompt_msg = mock_app.prompt_yn.call_args[0][0]
        # Should contain size but no chunk count (total_chunks is 0)
        assert "0.01 GB" in prompt_msg
        # Should not contain "chunks)" since total_chunks is 0
        # and fails the > 0 check
        assert "chunks)" not in prompt_msg
