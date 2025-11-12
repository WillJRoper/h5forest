"""Tests for goto/jump mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.bindings import H5KeyBindings


def _init_goto_bindings(app):
    """Initialize jump bindings using H5KeyBindings class."""
    bindings = H5KeyBindings(app)
    bindings._init_jump_bindings()

    # Return list of hotkeys matching old interface
    return [
        bindings.goto_top_label,
        bindings.goto_bottom_label,
        bindings.goto_parent_label,
        bindings.jump_to_key_label,
        bindings.exit_mode_label,
        bindings.exit_label,
    ]


class TestJumpBindings:
    """Test cases for goto/jump mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()
        app.flag_jump_mode = True
        app.tree = MagicMock()
        app.tree.tree_text = "line1\nline2\nline3"
        app.tree.tree_text_split = ["line1", "line2", "line3"]
        app.tree.length = 20
        app.tree.height = 3
        app.current_row = 1
        app.current_column = 5
        app.current_position = 10
        app.set_cursor_position = MagicMock()
        app.return_to_normal_mode = MagicMock()
        app.default_focus = MagicMock()
        app.print = MagicMock()
        app.input = MagicMock()
        app.user_input = ""
        app.kb = KeyBindings()
        # Add config mock
        add_config_mock(app)

        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        return MagicMock()

    @patch("h5forest.h5_forest.H5Forest")
    def test_init_goto_bindings_returns_hotkeys(
        self, mock_h5forest_class, mock_app
    ):
        """Test that _init_goto_bindings returns a list of Labels."""
        mock_h5forest_class.return_value = mock_app

        hot_keys = _init_goto_bindings(mock_app)
        assert isinstance(hot_keys, list)
        assert len(hot_keys) == 6
        for item in hot_keys:
            assert isinstance(item, Label)

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_top(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to top of tree."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("t",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.set_cursor_position.assert_called_once_with(
            mock_app.tree.tree_text, new_cursor_pos=0
        )
        mock_app.return_to_normal_mode.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_top_g_key(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to top with 'g' key."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("g",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.set_cursor_position.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_bottom(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to bottom of tree."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("b",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.set_cursor_position.assert_called_once_with(
            mock_app.tree.tree_text, new_cursor_pos=mock_app.tree.length
        )

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_bottom_G_key(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test going to bottom with 'G' key."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("G",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.set_cursor_position.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_parent(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to parent node."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        node = MagicMock()
        parent = MagicMock()
        node.parent = parent
        node.path = "/group/subgroup"
        # Set current position properly
        mock_app.current_row = 2
        mock_app.current_column = 5
        mock_app.current_position = 20
        mock_app.tree.tree_text_split = ["line1", "line2", "line3"]
        mock_app.tree.get_current_node = MagicMock(
            side_effect=[node, MagicMock(), parent]
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify set_cursor_position was called with non-negative position
        mock_app.set_cursor_position.assert_called_once()
        call_args = mock_app.set_cursor_position.call_args[0]
        # Position should be clamped to 0 if negative
        assert call_args[1] >= 0
        mock_app.return_to_normal_mode.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_parent_negative_position(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test goto parent with negative position calculation."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        node = MagicMock()
        parent = MagicMock()
        node.parent = parent
        node.path = "/group/subgroup"
        # Set position to trigger negative: pos = 2 - (5 + 1) = -4
        mock_app.current_row = 0
        mock_app.current_column = 5
        mock_app.current_position = 2
        mock_app.tree.tree_text_split = ["line1", "line2", "line3"]
        mock_app.tree.get_current_node = MagicMock(
            side_effect=[node, MagicMock(), parent]
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify position was clamped to 0
        mock_app.set_cursor_position.assert_called_once()
        call_args = mock_app.set_cursor_position.call_args[0]
        assert call_args[1] == 0

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_parent_at_root(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test going to parent when at root."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        node = MagicMock()
        node.parent = None
        node.path = "/"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/ is a root Group!")
        mock_app.set_cursor_position.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_next(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to next node."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        node = MagicMock()
        node.depth = 2
        next_node = MagicMock()
        next_node.depth = 1
        mock_app.tree.get_current_node = MagicMock(
            side_effect=[node, next_node]
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("n",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.set_cursor_position.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_next_at_end(self, mock_h5forest_class, mock_app, mock_event):
        """Test going to next when at end of tree."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        mock_app.current_row = mock_app.tree.height - 1
        node = MagicMock()
        node.depth = 1
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("n",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.return_to_normal_mode.assert_called_once()
        mock_app.set_cursor_position.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_goto_next_not_found(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test going to next when next node not found."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        node = MagicMock()
        node.depth = 1
        same_depth_node = MagicMock()
        same_depth_node.depth = 2
        mock_app.tree.get_current_node = MagicMock(
            side_effect=[node, same_depth_node, same_depth_node]
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("n",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("Next Group can't be found")

    @patch("h5forest.h5_forest.H5Forest")
    def test_jump_to_key(self, mock_h5forest_class, mock_app, mock_event):
        """Test jumping to key containing user input."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("K",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.input.assert_called_once()
        callback = mock_app.input.call_args[0][1]
        # Simulate callback - need to set up properly
        mock_app.user_input = "test"
        mock_app.current_row = 0
        mock_app.current_column = 5
        mock_app.current_position = 10
        node1 = MagicMock()
        node1.name = "test_node"  # Found on first iteration
        mock_app.tree.get_current_node = MagicMock(return_value=node1)
        callback()
        mock_app.set_cursor_position.assert_called_once()
        mock_app.default_focus.assert_called()
        mock_app.return_to_normal_mode.assert_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_jump_to_key_not_found(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test jumping to key when key not found."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("K",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        callback = mock_app.input.call_args[0][1]
        mock_app.user_input = "nonexistent"
        mock_app.current_row = mock_app.tree.height - 1
        node = MagicMock()
        node.name = "other"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        callback()
        mock_app.print.assert_called_once_with("Couldn't find matching key!")

    @patch("h5forest.h5_forest.H5Forest")
    def test_all_keys_bound(self, mock_h5forest_class, mock_app):
        """Test that all expected keys are bound."""
        mock_h5forest_class.return_value = mock_app
        _init_goto_bindings(mock_app)
        for key in ["t", "g", "b", "G", "p", "n", "K"]:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"
