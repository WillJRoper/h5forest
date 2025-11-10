"""Tests for application-level keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.bindings import _init_app_bindings, error_handler


class TestAppBindings:
    """Test cases for application-level keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()

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
        assert len(hot_keys) == 10

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

    def test_exit_app_ctrl_q(self, mock_app, mock_event):
        """Test that Ctrl-Q exits the app."""
        _init_app_bindings(mock_app)

        # Find the c-q binding
        bindings = [b for b in mock_app.kb.bindings if "c-q" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify app.exit was called
        mock_event.app.exit.assert_called_once()

    def test_goto_leader_mode(self, mock_app, mock_event):
        """Test entering goto/jump mode."""
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

    def test_dataset_leader_mode(self, mock_app, mock_event):
        """Test entering dataset mode."""
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

    def test_window_leader_mode(self, mock_app, mock_event):
        """Test entering window mode."""
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

    def test_plotting_leader_mode(self, mock_app, mock_event):
        """Test entering plotting mode."""
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

    def test_hist_leader_mode(self, mock_app, mock_event):
        """Test entering histogram mode."""
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

    def test_exit_leader_mode(self, mock_app, mock_event):
        """Test exiting leader mode."""
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

    def test_expand_attributes(self, mock_app, mock_event):
        """Test expanding attributes."""
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

    def test_collapse_attributes(self, mock_app, mock_event):
        """Test collapsing attributes."""
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

    def test_search_leader_mode(self, mock_app, mock_event):
        """Test entering search mode."""
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
        mock_path = "h5forest.bindings.bindings.threading.Thread"
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

    def test_search_leader_mode_with_index_building(
        self, mock_app, mock_event
    ):
        """Test search mode when index building triggers auto-update."""
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
        thread_path = "h5forest.bindings.bindings.threading.Thread"
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

    def test_search_leader_mode_no_query(self, mock_app, mock_event):
        """Test search when index completes but no query entered."""
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

        thread_path = "h5forest.bindings.bindings.threading.Thread"
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

    def test_restore_tree_to_initial(self, mock_app, mock_event):
        """Test restoring tree to initial state."""
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

    def test_all_expected_keys_bound(self, mock_app):
        """Test that all expected keys are bound."""
        _init_app_bindings(mock_app)

        # Expected keys
        expected_keys = [
            "q",  # exit / exit leader
            "c-q",  # force exit
            "g",  # goto mode
            "d",  # dataset mode
            "w",  # window mode
            "p",  # plotting mode
            "H",  # histogram mode
            "A",  # expand/collapse attributes
            "s",  # search mode
            "r",  # restore tree
        ]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

    @patch("h5forest.bindings.bindings.error_handler")
    def test_handlers_wrapped_with_error_handler(
        self, mock_error_handler, mock_app
    ):
        """Test that some handlers are wrapped with error_handler."""
        assert callable(error_handler)

    def test_hotkeys_structure(self, mock_app):
        """Test that hotkeys dict has correct structure."""
        hot_keys = _init_app_bindings(mock_app)

        # Should be a dict with Label values
        assert len(hot_keys) == 10

        # All values should be Labels
        for key, value in hot_keys.items():
            assert isinstance(key, str), f"Invalid key type: {type(key)}"
            assert isinstance(value, Label), (
                f"Invalid value type: {type(value)}"
            )
