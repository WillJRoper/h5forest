"""Tests for application-level keybindings."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.bindings import H5KeyBindings


def _init_app_bindings(app):
    """Initialize app bindings using H5KeyBindings class."""
    bindings = H5KeyBindings(app)
    bindings._init_normal_mode_bindings()
    bindings._init_tree_bindings()  # For expand/collapse attributes

    # Return dict of hotkeys matching old interface
    return {
        "dataset_mode": bindings.dataset_mode_label,
        "goto_mode": bindings.goto_mode_label,
        "hist_mode": bindings.hist_mode_label,
        "plotting_mode": bindings.plotting_mode_label,
        "window_mode": bindings.window_mode_label,
        "search": bindings.search_label,
        "restore_tree": bindings.restore_tree_label,
        "copy_key": bindings.copy_key_label,
        "exit": bindings.exit_label,
        "exit_mode": bindings.exit_mode_label,
        "expand_attrs": bindings.expand_attrs_label,
    }


class TestAppBindings:
    """Test cases for application-level keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()

        # Set up config with default keymaps
        add_config_mock(app)

        # Set up mode flags
        app.flag_normal_mode = True
        app._flag_normal_mode = True
        app._flag_jump_mode = False
        app._flag_dataset_mode = False
        app._flag_window_mode = False
        app._flag_plotting_mode = False
        app._flag_hist_mode = False
        app._flag_search_mode = False
        app.flag_expanded_attrs = False

        # Set up tree and buffer
        app.tree = MagicMock()
        app.tree.root = MagicMock()
        app.tree.root.children = []
        app.tree.root.open_node = MagicMock()
        app.tree.root.close_node = MagicMock()
        app.tree.get_tree_text = MagicMock(return_value="tree text")
        app.tree.original_tree_text = None
        app.tree.original_tree_text_split = None
        app.tree.original_nodes_by_row = None
        app.tree.filtered_node_rows = []

        app.tree_buffer = MagicMock()
        app.tree_buffer.set_document = MagicMock()

        # Set up search content
        app.search_content = MagicMock()
        app.search_content.text = ""
        app.search_content.buffer = MagicMock()
        app.search_content.buffer.cursor_position = 0

        # Set up focus management
        app.shift_focus = MagicMock()
        app.tree_content = MagicMock()
        app.tree_content.content = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()

        # Set up keybindings
        app.kb = KeyBindings()

        # Set up layout
        app.app = MagicMock()
        app.app.layout = MagicMock()
        app.app.layout.has_focus = MagicMock(return_value=True)

        # Set up print method for feedback
        app.print = MagicMock()

        # Set up current node
        app.current_row = 0
        mock_node = MagicMock()
        mock_node.path = "/test/hdf5/path"
        app.tree.get_current_node = MagicMock(return_value=mock_node)

        # Set up tree_has_focus property
        app.tree_has_focus = True

        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        event = MagicMock()
        event.app = MagicMock()
        event.app.exit = MagicMock()
        event.app.invalidate = MagicMock()
        return event

    def test_init_app_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_app_bindings returns a dict of hotkeys."""
        hot_keys = _init_app_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        assert len(hot_keys) == 11

    def test_exit_app_handler(self, mock_app, mock_event):
        """Test the exit_app handler."""
        _init_app_bindings(mock_app)

        # Find the exit_app handler (bound to 'q' with normal mode filter)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("q",) and b.filter is not None
        ]
        # Should have at least one 'q' binding
        assert len(bindings) > 0

        # Get the first one (should be the normal mode exit)
        handler = bindings[0].handler
        handler(mock_event)

        # Verify app.exit was called
        mock_event.app.exit.assert_called_once()

    # Removed test_exit_app_ctrl_q since 'c-q' is not bound in the
    # new binding system

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_leader_mode(self, mock_h5forest_class, mock_app, mock_event):
        """Test entering goto/jump mode."""
        # Make H5Forest() return mock_app
        mock_h5forest_class.return_value = mock_app

        _init_app_bindings(mock_app)

        # Find the 'g' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("g",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify mode flags changed
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_jump_mode is True

    @patch("h5forest.h5_forest.H5Forest")
    def test_dataset_leader_mode(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test entering dataset mode."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Find the 'd' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("d",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify mode flags changed
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_dataset_mode is True

    @patch("h5forest.h5_forest.H5Forest")
    def test_window_leader_mode(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test entering window mode."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Find the 'w' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("w",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify mode flags changed
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_window_mode is True

    @patch("h5forest.h5_forest.H5Forest")
    def test_plotting_leader_mode(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test entering plotting mode."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Find the 'p' binding with filter
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify mode flags changed
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_plotting_mode is True

    @patch("h5forest.h5_forest.H5Forest")
    def test_hist_leader_mode(self, mock_h5forest_class, mock_app, mock_event):
        """Test entering histogram mode."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Find the 'H' binding (uppercase)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("H",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify mode flags changed
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_hist_mode is True

    @patch("h5forest.h5_forest.H5Forest")
    def test_exit_leader_mode(self, mock_h5forest_class, mock_app, mock_event):
        """Test exiting leader mode."""
        mock_h5forest_class.return_value = mock_app
        # Set up non-normal mode
        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app._flag_jump_mode = True

        _init_app_bindings(mock_app)

        # Find the 'q' binding with NOT normal mode filter
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("q",) and b.filter is not None
        ]
        # Should have multiple 'q' bindings (one for exit, one for exit_leader)
        assert len(bindings) >= 2

        # Get the one that's not the exit_app handler
        # (the exit_leader_mode handler should call return_to_normal_mode)
        handler = bindings[-1].handler  # Last one is exit_leader_mode
        handler(mock_event)

        # Verify return to normal mode was called
        mock_app.return_to_normal_mode.assert_called_once()
        mock_app.default_focus.assert_called_once()
        mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_expand_attributes(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test expanding attributes."""
        mock_h5forest_class.return_value = mock_app
        mock_app.flag_expanded_attrs = False

        _init_app_bindings(mock_app)

        # Find the 'A' binding for expand
        bindings = [b for b in mock_app.kb.bindings if b.keys == ("A",)]
        assert len(bindings) >= 1

        # The first 'A' binding should be expand (when not expanded)
        handler = bindings[0].handler
        handler(mock_event)

        # Verify flag was set
        assert mock_app.flag_expanded_attrs is True
        mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_collapse_attributes(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test collapsing attributes."""
        mock_h5forest_class.return_value = mock_app
        mock_app.flag_expanded_attrs = True

        _init_app_bindings(mock_app)

        # Find the 'A' bindings
        bindings = [b for b in mock_app.kb.bindings if b.keys == ("A",)]
        assert len(bindings) >= 1

        # The second 'A' binding should be collapse (when expanded)
        handler = bindings[-1].handler
        handler(mock_event)

        # Verify flag was cleared
        assert mock_app.flag_expanded_attrs is False
        mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_search_leader_mode(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test entering search mode."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Find the 's' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("s",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler

        # Mock threading to capture the thread target
        mock_path = "h5forest.bindings.search_funcs.threading.Thread"
        with patch(mock_path) as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            handler(mock_event)

            # Verify mode flags changed
            assert mock_app._flag_normal_mode is False
            assert mock_app._flag_search_mode is True

            # Verify search content was cleared and focused
            assert mock_app.search_content.text == ""
            assert mock_app.search_content.buffer.cursor_position == 0
            mock_app.shift_focus.assert_called_once_with(
                mock_app.search_content
            )

            # Verify get_all_paths was called
            mock_app.tree.get_all_paths.assert_called_once()

            # Verify thread started if index is building
            if mock_app.tree.index_building:
                mock_thread.assert_called_once()
                mock_thread_instance.start.assert_called_once()

            mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_search_leader_mode_with_index_building(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test search mode when index building triggers auto-update."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Set up index building scenario
        mock_app.tree.index_building = True
        mock_app.tree.unpack_thread = MagicMock()
        mock_app.search_content.text = "test query"
        mock_app.tree.filter_tree = MagicMock(return_value="filtered text")
        mock_app.app.loop = MagicMock()
        mock_app.app.loop.call_soon_threadsafe = MagicMock()

        # Mock WaitIndicator
        mock_indicator = MagicMock()

        # Find the 's' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("s",) and b.filter is not None
        ]
        handler = bindings[0].handler

        # Mock threading but capture and execute the thread target
        thread_path = "h5forest.bindings.search_funcs.threading.Thread"
        with patch(thread_path) as mock_thread:
            with patch(
                "h5forest.bindings.search_funcs.WaitIndicator"
            ) as mock_wait_cls:
                mock_wait_cls.return_value = mock_indicator

                # Capture the thread target function
                thread_target = None

                def capture_thread(*args, **kwargs):
                    nonlocal thread_target
                    thread_target = kwargs.get("target")
                    mock_inst = MagicMock()
                    return mock_inst

                mock_thread.side_effect = capture_thread

                # Call the handler
                handler(mock_event)

                # After handler clears search text, simulate user typing
                mock_app.search_content.text = "test query"

                # Now execute the captured thread target
                if thread_target:
                    thread_target()

                    # Verify WaitIndicator was created and started
                    mock_wait_cls.assert_called_once_with(
                        mock_app, "Constructing search database..."
                    )
                    mock_indicator.start.assert_called_once()

                    # Verify thread was joined
                    mock_app.tree.unpack_thread.join.assert_called_once()

                    # Verify indicator was stopped
                    mock_indicator.stop.assert_called_once()

                    # Verify auto-update was triggered
                    mock_app.app.loop.call_soon_threadsafe.assert_called_once()

                    # Execute the update_search callback (lines 112-124)
                    call_args = mock_app.app.loop.call_soon_threadsafe
                    update_callback = call_args.call_args[0][0]
                    update_callback()

                    # Verify the update happened
                    query = "test query"
                    mock_app.tree.filter_tree.assert_called_once_with(query)
                    mock_app.tree_buffer.set_document.assert_called_once()
                    mock_app.app.invalidate.assert_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_search_leader_mode_no_query(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test search when index completes but no query entered."""
        mock_h5forest_class.return_value = mock_app
        _init_app_bindings(mock_app)

        # Set up index building scenario with empty query
        mock_app.tree.index_building = True
        mock_app.tree.unpack_thread = MagicMock()
        mock_app.search_content.text = ""  # Empty query
        mock_app.tree.filter_tree = MagicMock(return_value="filtered text")
        mock_app.app.loop = MagicMock()
        mock_app.app.loop.call_soon_threadsafe = MagicMock()

        # Mock WaitIndicator
        mock_indicator = MagicMock()

        # Find the 's' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("s",) and b.filter is not None
        ]
        handler = bindings[0].handler

        thread_path = "h5forest.bindings.search_funcs.threading.Thread"
        with patch(thread_path) as mock_thread:
            with patch("h5forest.utils.WaitIndicator") as mock_wait_cls:
                mock_wait_cls.return_value = mock_indicator

                # Capture the thread target function
                thread_target = None

                def capture_thread(*args, **kwargs):
                    nonlocal thread_target
                    thread_target = kwargs.get("target")
                    mock_inst = MagicMock()
                    return mock_inst

                mock_thread.side_effect = capture_thread

                # Call the handler
                handler(mock_event)

                # Execute the thread target
                if thread_target:
                    thread_target()

                    # Execute the update_search callback
                    call_args = mock_app.app.loop.call_soon_threadsafe
                    update_callback = call_args.call_args[0][0]
                    update_callback()

                    # With empty query, filter_tree should NOT be called
                    mock_app.tree.filter_tree.assert_not_called()
                    # set_document should not be called either
                    mock_app.tree_buffer.set_document.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_restore_tree_to_initial(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test restoring tree to initial state."""
        mock_h5forest_class.return_value = mock_app
        # Set up some saved state
        mock_app.tree.original_tree_text = "saved text"
        mock_app.tree.original_tree_text_split = ["line1", "line2"]
        mock_app.tree.original_nodes_by_row = [MagicMock()]
        mock_app.tree.filtered_node_rows = [1, 2, 3]

        # Add some children to root
        child1 = MagicMock()
        child2 = MagicMock()
        mock_app.tree.root.children = [child1, child2]

        _init_app_bindings(mock_app)

        # Find the 'r' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("r",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify saved state was cleared
        assert mock_app.tree.original_tree_text is None
        assert mock_app.tree.original_tree_text_split is None
        assert mock_app.tree.original_nodes_by_row is None
        assert mock_app.tree.filtered_node_rows == []

        # Verify children were closed
        child1.close_node.assert_called_once()
        child2.close_node.assert_called_once()

        # Verify children list was cleared and root was reopened
        assert mock_app.tree.root.children == []
        mock_app.tree.root.open_node.assert_called_once()

        # Verify tree was rebuilt
        mock_app.tree.get_tree_text.assert_called_once()

        # Verify buffer was updated
        mock_app.tree_buffer.set_document.assert_called_once()
        call_args = mock_app.tree_buffer.set_document.call_args
        doc = call_args[0][0]
        assert isinstance(doc, Document)
        assert doc.text == "tree text"
        assert doc.cursor_position == 0
        assert call_args[1]["bypass_readonly"] is True

        # Verify invalidate was called
        mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_linux(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copying HDF5 key to clipboard on Linux."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Set up subprocess mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(return_value=(b"", b""))
        mock_popen.return_value = mock_process

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify current node was retrieved
        mock_app.tree.get_current_node.assert_called_once_with(
            mock_app.current_row
        )

        # Verify xclip was called with correct arguments
        mock_popen.assert_called_once_with(
            ["xclip", "-selection", "clipboard"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Verify communicate was called with the path (without leading slashes)
        mock_process.communicate.assert_called_once_with(
            input=b"test/hdf5/path"
        )

        # Verify feedback was shown
        mock_app.print.assert_called_once_with(
            "Copied test/hdf5/path into the clipboard"
        )

        # Verify invalidate was called
        mock_event.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_macos(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copying HDF5 key to clipboard on macOS."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as macOS
        mock_platform.return_value = "Darwin"

        # Set up subprocess mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(return_value=(b"", b""))
        mock_popen.return_value = mock_process

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify pbcopy was called
        mock_popen.assert_called_once_with(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_windows(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copying HDF5 key to clipboard on Windows."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Windows
        mock_platform.return_value = "Windows"

        # Set up subprocess mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(return_value=(b"", b""))
        mock_popen.return_value = mock_process

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify clip was called
        mock_popen.assert_called_once_with(
            ["clip"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_failed_returncode(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copy key when clipboard operation fails."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Set up subprocess mock with failed returncode
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate = MagicMock(return_value=(b"", b"error"))
        mock_popen.return_value = mock_process

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was shown
        mock_app.print.assert_called_once_with(
            "Error: Failed to copy to clipboard"
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_clipboard_error(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copy key when clipboard tool is not available on Linux."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Simulate xclip not being found
        mock_popen.side_effect = FileNotFoundError()

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was shown
        mock_app.print.assert_called_once_with(
            "Error: xclip not found. Install with: apt install xclip"
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_clipboard_error_non_linux(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copy key when clipboard tool is not available on non-Linux."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as macOS
        mock_platform.return_value = "Darwin"

        # Simulate pbcopy not being found
        mock_popen.side_effect = FileNotFoundError()

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was shown
        mock_app.print.assert_called_once_with(
            "Error: Clipboard tool not available"
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_general_exception(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copy key when a general exception occurs."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Simulate a general exception
        mock_popen.side_effect = RuntimeError("Unexpected error")

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was shown
        mock_app.print.assert_called_once_with(
            "Error copying to clipboard: Unexpected error"
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_root_path(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copying root path (edge case)."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Set up subprocess mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(return_value=(b"", b""))
        mock_popen.return_value = mock_process

        # Set up node with root path
        mock_node = MagicMock()
        mock_node.path = "/"
        mock_app.tree.get_current_node.return_value = mock_node

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify empty string is copied for root path
        mock_process.communicate.assert_called_once_with(input=b"")

        # Verify feedback was shown
        mock_app.print.assert_called_once_with("Copied  into the clipboard")

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.normal_funcs.subprocess.Popen")
    @patch("h5forest.bindings.normal_funcs.platform.system")
    def test_copy_key_multiple_leading_slashes(
        self,
        mock_platform,
        mock_popen,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test copying path with multiple leading slashes."""
        mock_h5forest_class.return_value = mock_app
        # Set up platform as Linux
        mock_platform.return_value = "Linux"

        # Set up subprocess mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(return_value=(b"", b""))
        mock_popen.return_value = mock_process

        # Set up node with multiple leading slashes
        mock_node = MagicMock()
        mock_node.path = "//01/000_z015p000/Galaxy/M200"
        mock_app.tree.get_current_node.return_value = mock_node

        _init_app_bindings(mock_app)

        # Find the 'c' binding
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify all leading slashes are removed
        mock_process.communicate.assert_called_once_with(
            input=b"01/000_z015p000/Galaxy/M200"
        )

        # Verify feedback was shown
        mock_app.print.assert_called_once_with(
            "Copied 01/000_z015p000/Galaxy/M200 into the clipboard"
        )

    def test_all_expected_keys_bound(self, mock_app):
        """Test that all expected keys are bound."""
        _init_app_bindings(mock_app)

        # Expected keys
        expected_keys = [
            "q",  # exit / exit leader
            "g",  # goto mode
            "d",  # dataset mode
            "w",  # window mode
            "p",  # plotting mode
            "H",  # histogram mode
            "A",  # expand/collapse attributes
            "s",  # search mode
            "r",  # restore tree
            "c",  # copy key
        ]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

    def test_handlers_wrapped_with_error_handler(self, mock_app):
        """Test that the bindings class is properly initialized."""
        # With the refactored binding system, error handling is built
        # into the class
        bindings = H5KeyBindings(mock_app)
        assert bindings is not None
        assert hasattr(bindings, "bind_function")

    def test_hotkeys_structure(self, mock_app):
        """Test that hotkeys dict has correct structure."""
        hot_keys = _init_app_bindings(mock_app)

        # Should be a dict with Label values
        assert len(hot_keys) == 11

        # All values should be Labels
        for key, value in hot_keys.items():
            assert isinstance(key, str), f"Invalid key type: {type(key)}"
            assert isinstance(value, Label), (
                f"Invalid value type: {type(value)}"
            )


class TestGetCurrentHotkeys:
    """Test the get_current_hotkeys method for different modes."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()
        add_config_mock(app)

        # Set up default mode flags
        app.flag_normal_mode = True
        app._flag_normal_mode = True
        app._flag_jump_mode = False
        app._flag_dataset_mode = False
        app._flag_window_mode = False
        app._flag_plotting_mode = False
        app._flag_hist_mode = False
        app._flag_search_mode = False
        app.flag_expanded_attrs = False
        app.flag_dataset_mode = False
        app.flag_search_mode = False
        app.flag_window_mode = False
        app.flag_jump_mode = False
        app.flag_hist_mode = False
        app.flag_plotting_mode = False

        # Set up tree
        app.tree = MagicMock()
        app.tree_has_focus = True
        app.dataset_values_has_content = False
        app.histogram_config_has_focus = False
        app.plot_config_has_focus = False

        # Set up plotters
        app.histogram_plotter = MagicMock()
        app.histogram_plotter.data_assigned = False
        app.scatter_plotter = MagicMock()
        app.scatter_plotter.data_assigned = False

        # Set up keybindings
        app.kb = KeyBindings()

        return app

    def test_get_current_hotkeys_expanded_attrs(self, mock_app):
        """Test hotkeys when attributes are expanded."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_expanded_attrs = True
        mock_app.tree_has_focus = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)
        # The shrink attrs label should be in the labels list
        current_labels = (
            hotkeys.labels() if callable(hotkeys.labels) else hotkeys.labels
        )
        assert any("Shrink" in str(label.text) for label in current_labels)

    def test_get_current_hotkeys_dataset_mode(self, mock_app):
        """Test hotkeys in dataset mode."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_dataset_mode = True
        mock_app._flag_dataset_mode = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_dataset_mode_with_values(self, mock_app):
        """Test hotkeys in dataset mode with values shown."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_dataset_mode = True
        mock_app._flag_dataset_mode = True
        mock_app.dataset_values_has_content = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_search_mode(self, mock_app):
        """Test hotkeys in search mode."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_search_mode = True
        mock_app._flag_search_mode = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_window_mode(self, mock_app):
        """Test hotkeys in window mode."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_window_mode = True
        mock_app._flag_window_mode = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_jump_mode(self, mock_app):
        """Test hotkeys in jump mode."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_jump_mode = True
        mock_app._flag_jump_mode = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_hist_mode_tree_focused(self, mock_app):
        """Test hotkeys in histogram mode with tree focused."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_hist_mode = True
        mock_app._flag_hist_mode = True
        mock_app.tree_has_focus = True
        mock_app.histogram_config_has_focus = False

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_hist_mode_hist_focused(self, mock_app):
        """Test hotkeys in histogram mode with hist focused."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_hist_mode = True
        mock_app._flag_hist_mode = True
        mock_app.tree_has_focus = False
        mock_app.histogram_config_has_focus = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_hist_mode_with_data(self, mock_app):
        """Test hotkeys in histogram mode with data assigned."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_hist_mode = True
        mock_app._flag_hist_mode = True
        mock_app.histogram_plotter.data_assigned = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_plot_mode_tree_focused(self, mock_app):
        """Test hotkeys in plot mode with tree focused."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_plotting_mode = True
        mock_app._flag_plotting_mode = True
        mock_app.tree_has_focus = True
        mock_app.plot_config_has_focus = False

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_plot_mode_plot_focused(self, mock_app):
        """Test hotkeys in plot mode with plot focused."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_plotting_mode = True
        mock_app._flag_plotting_mode = True
        mock_app.tree_has_focus = False
        mock_app.plot_config_has_focus = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)

    def test_get_current_hotkeys_plot_mode_with_data(self, mock_app):
        """Test hotkeys in plot mode with data assigned."""
        from h5forest.utils import DynamicLabelLayout

        mock_app.flag_normal_mode = False
        mock_app._flag_normal_mode = False
        mock_app.flag_plotting_mode = True
        mock_app._flag_plotting_mode = True
        mock_app.scatter_plotter.data_assigned = True

        bindings = H5KeyBindings(mock_app)
        hotkeys = bindings.get_current_hotkeys()

        # Should return a DynamicLabelLayout
        assert isinstance(hotkeys, DynamicLabelLayout)


class TestGetModeTitle:
    """Test the get_mode_title method."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()
        add_config_mock(app)

        # Set up default mode flags
        app.flag_normal_mode = True
        app.flag_jump_mode = False
        app.flag_dataset_mode = False
        app.flag_window_mode = False
        app.flag_plotting_mode = False
        app.flag_hist_mode = False
        app.flag_search_mode = False

        app.kb = KeyBindings()

        return app

    def test_get_mode_title_normal_mode(self, mock_app):
        """Test mode title in normal mode."""
        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Normal Mode"

    def test_get_mode_title_jump_mode(self, mock_app):
        """Test mode title in jump mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_jump_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Goto Mode"

    def test_get_mode_title_dataset_mode(self, mock_app):
        """Test mode title in dataset mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_dataset_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Dataset Mode"

    def test_get_mode_title_window_mode(self, mock_app):
        """Test mode title in window mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_window_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Window Mode"

    def test_get_mode_title_plotting_mode(self, mock_app):
        """Test mode title in plotting mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_plotting_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Plotting Mode"

    def test_get_mode_title_hist_mode(self, mock_app):
        """Test mode title in histogram mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_hist_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Histogram Mode"

    def test_get_mode_title_search_mode(self, mock_app):
        """Test mode title in search mode."""
        mock_app.flag_normal_mode = False
        mock_app.flag_search_mode = True

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Search Mode"

    def test_get_mode_title_unknown_mode(self, mock_app):
        """Test mode title when no mode is active."""
        mock_app.flag_normal_mode = False
        mock_app.flag_jump_mode = False
        mock_app.flag_dataset_mode = False
        mock_app.flag_window_mode = False
        mock_app.flag_plotting_mode = False
        mock_app.flag_hist_mode = False
        mock_app.flag_search_mode = False

        bindings = H5KeyBindings(mock_app)
        title = bindings.get_mode_title()
        assert title == "Unknown Mode"
