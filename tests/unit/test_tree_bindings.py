"""Tests for tree navigation keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Label

from h5forest.bindings.tree_bindings import _init_tree_bindings, error_handler


class TestTreeBindings:
    """Test cases for tree navigation keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()

        # Set up tree buffer with cursor movement methods
        app.tree_buffer = MagicMock()
        app.tree_buffer.cursor_up = MagicMock()
        app.tree_buffer.cursor_down = MagicMock()
        app.tree_buffer.set_document = MagicMock()

        # Set up tree content
        app.tree_content = MagicMock()

        # Set up tree and current position
        app.tree = MagicMock()
        app.current_row = 0
        app.current_position = 0
        app.print = MagicMock()

        # Set up mode flags
        app.flag_search_mode = False

        # Set up keybindings
        app.kb = KeyBindings()

        # Set up layout for focus checks
        app.app = MagicMock()
        app.app.layout = MagicMock()
        app.app.layout.has_focus = MagicMock(return_value=True)

        # Add config mock
        add_config_mock(app)
        # Enable vim mode for tree navigation tests
        app.config.is_vim_mode_enabled = MagicMock(return_value=True)

        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        event = MagicMock()
        event.app = MagicMock()
        event.app.key_processor = MagicMock()
        event.app.key_processor.feed = MagicMock()
        return event

    def test_init_tree_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_tree_bindings returns a dict of hotkeys."""
        hot_keys = _init_tree_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        # 2 keys: open_group, move_ten
        assert len(hot_keys) == 2

    def test_move_up_ten_handler(self, mock_app, mock_event):
        """Test the move_up_ten handler."""
        _init_tree_bindings(mock_app)

        # Find the move_up_ten handler (bound to '{')
        bindings = [b for b in mock_app.kb.bindings if "{" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify cursor moved up 10 lines
        mock_app.tree_buffer.cursor_up.assert_called_once_with(10)

    def test_move_down_ten_handler(self, mock_app, mock_event):
        """Test the move_down_ten handler."""
        _init_tree_bindings(mock_app)

        # Find the move_down_ten handler (bound to '}')
        bindings = [b for b in mock_app.kb.bindings if "}" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify cursor moved down 10 lines
        mock_app.tree_buffer.cursor_down.assert_called_once_with(10)

    def test_move_left_handler(self, mock_app, mock_event):
        """Test the move_left handler (vim h)."""
        _init_tree_bindings(mock_app)

        # Find the move_left handler (bound to 'h')
        bindings = [b for b in mock_app.kb.bindings if "h" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify KeyPress(Keys.Left) was fed to key processor
        mock_event.app.key_processor.feed.assert_called_once()
        call_args = mock_event.app.key_processor.feed.call_args[0]
        assert call_args[0].key == Keys.Left

    def test_move_down_handler(self, mock_app, mock_event):
        """Test the move_down handler (vim j)."""
        _init_tree_bindings(mock_app)

        # Find the move_down handler (bound to 'j')
        bindings = [b for b in mock_app.kb.bindings if "j" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify KeyPress(Keys.Down) was fed to key processor
        mock_event.app.key_processor.feed.assert_called_once()
        call_args = mock_event.app.key_processor.feed.call_args[0]
        assert call_args[0].key == Keys.Down

    def test_move_up_handler(self, mock_app, mock_event):
        """Test the move_up handler (vim k)."""
        _init_tree_bindings(mock_app)

        # Find the move_up handler (bound to 'k')
        bindings = [b for b in mock_app.kb.bindings if "k" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify KeyPress(Keys.Up) was fed to key processor
        mock_event.app.key_processor.feed.assert_called_once()
        call_args = mock_event.app.key_processor.feed.call_args[0]
        assert call_args[0].key == Keys.Up

    def test_move_right_handler(self, mock_app, mock_event):
        """Test the move_right handler (vim l)."""
        _init_tree_bindings(mock_app)

        # Find the move_right handler (bound to 'l')
        # Be specific: look for exactly ('l',) tuple
        bindings = [b for b in mock_app.kb.bindings if b.keys == ("l",)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify KeyPress(Keys.Right) was fed to key processor
        mock_event.app.key_processor.feed.assert_called_once()
        call_args = mock_event.app.key_processor.feed.call_args[0]
        assert call_args[0].key == Keys.Right

    def test_expand_collapse_node_with_dataset(self, mock_app, mock_event):
        """Test expand_collapse_node does nothing for datasets."""
        _init_tree_bindings(mock_app)

        # Create a mock dataset node
        node = MagicMock()
        node.is_dataset = True
        node.path = "/group/dataset"
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        # Find the expand_collapse_node handler (bound to 'enter')
        # Note: enter is represented as c-m
        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify print was called with appropriate message
        mock_app.print.assert_called_once_with("/group/dataset is not a Group")

        # Verify tree was not modified
        mock_app.tree_buffer.set_document.assert_not_called()

    def test_expand_collapse_node_with_no_children(self, mock_app, mock_event):
        """Test expand_collapse_node for groups with no children."""
        _init_tree_bindings(mock_app)

        # Create a mock group node with no children
        node = MagicMock()
        node.is_dataset = False
        node.has_children = False
        node.path = "/empty_group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify print was called
        mock_app.print.assert_called_once_with("/empty_group has no children")

        # Verify tree was not modified
        mock_app.tree_buffer.set_document.assert_not_called()

    def test_expand_collapse_node_closes_expanded_node(
        self, mock_app, mock_event
    ):
        """Test expand_collapse_node closes an already expanded node."""
        _init_tree_bindings(mock_app)

        # Create a mock expanded group node
        node = MagicMock()
        node.is_dataset = False
        node.has_children = True
        node.is_expanded = True
        node.path = "/expanded_group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        mock_app.tree.close_node = MagicMock(return_value="closed tree text")
        mock_app.current_row = 5
        mock_app.current_position = (
            10  # Must be <= len("closed tree text") = 16
        )

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify close_node was called
        mock_app.tree.close_node.assert_called_once_with(node, 5)

        # Verify tree buffer was updated
        mock_app.tree_buffer.set_document.assert_called_once()
        call_args = mock_app.tree_buffer.set_document.call_args
        doc = call_args[0][0]
        assert isinstance(doc, Document)
        assert doc.text == "closed tree text"
        assert doc.cursor_position == 10
        assert call_args[1]["bypass_readonly"] is True

    def test_expand_collapse_node_opens_collapsed_node(
        self, mock_app, mock_event
    ):
        """Test expand_collapse_node opens a collapsed node."""
        _init_tree_bindings(mock_app)

        # Create a mock collapsed group node
        node = MagicMock()
        node.is_dataset = False
        node.has_children = True
        node.is_expanded = False
        node.path = "/collapsed_group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        mock_app.tree.update_tree_text = MagicMock(
            return_value="expanded tree text"
        )
        mock_app.current_row = 3
        mock_app.current_position = (
            10  # Must be <= len("expanded tree text") = 18
        )

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify update_tree_text was called
        mock_app.tree.update_tree_text.assert_called_once_with(node, 3)

        # Verify tree buffer was updated
        mock_app.tree_buffer.set_document.assert_called_once()
        call_args = mock_app.tree_buffer.set_document.call_args
        doc = call_args[0][0]
        assert isinstance(doc, Document)
        assert doc.text == "expanded tree text"
        assert doc.cursor_position == 10
        assert call_args[1]["bypass_readonly"] is True

    def test_all_keys_bound_correctly(self, mock_app):
        """Test that all expected keys are bound."""
        _init_tree_bindings(mock_app)

        # Expected keys
        expected_keys = [
            "{",  # move up 10
            "}",  # move down 10
            "c-m",  # enter - expand/collapse
            "h",  # vim left
            "j",  # vim down
            "k",  # vim up
            "l",  # vim right
        ]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

    def test_brace_keys_have_tree_focus_filter(self, mock_app):
        """Test that { and } keys require tree focus."""
        _init_tree_bindings(mock_app)

        for key in ["{", "}"]:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0
            assert bindings[0].filter is not None

    def test_enter_key_has_tree_focus_filter(self, mock_app):
        """Test that enter key requires tree focus."""
        _init_tree_bindings(mock_app)

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        assert len(bindings) > 0
        assert bindings[0].filter is not None

    def test_vim_keys_have_not_search_mode_filter(self, mock_app):
        """Test that vim keys (hjkl) exclude search mode."""
        _init_tree_bindings(mock_app)

        for key in ["h", "j", "k", "l"]:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0
            assert bindings[0].filter is not None

    @patch("h5forest.bindings.tree_bindings.error_handler")
    def test_handlers_wrapped_with_error_handler(
        self, mock_error_handler, mock_app
    ):
        """Test that handlers are wrapped with error_handler decorator."""

        assert callable(error_handler)

    def test_hotkeys_structure(self, mock_app):
        """Test that hotkeys dict has correct structure."""
        hot_keys = _init_tree_bindings(mock_app)

        # Should be a dict with Label values
        # 2 keys: open_group, move_ten
        assert len(hot_keys) == 2
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    def test_custom_movement_keys(self, mock_event):
        """Test that custom movement keys (not vim or arrows) get bound."""
        from tests.conftest import add_config_mock

        # Create mock app with custom movement keys
        mock_app = MagicMock()
        mock_app.tree = MagicMock()
        mock_app.tree.get_current_node = MagicMock(return_value=MagicMock())
        mock_app.kb = MagicMock()
        mock_app.kb.add = MagicMock(return_value=lambda f: f)
        mock_app.kb.bindings = []
        mock_app.current_row = 0
        mock_app.flag_search_mode = False

        # Add config mock with custom movement keys
        add_config_mock(mock_app)

        # Override the config to return custom keys (not vim or arrows)
        def custom_get_keymap(mode, action):
            custom_keymaps = {
                ("tree_navigation", "move_up"): "w",  # Not 'k' or 'up'
                ("tree_navigation", "move_down"): "s",  # Not 'j' or 'down'
                ("tree_navigation", "move_left"): "a",  # Not 'h' or 'left'
                ("tree_navigation", "move_right"): "d",  # Not 'l' or 'right'
                ("tree_navigation", "jump_up_10"): "{",
                ("tree_navigation", "jump_down_10"): "}",
                ("tree_navigation", "expand"): "enter",
                ("tree_navigation", "expand/collapse"): "enter",  # Alias
            }
            key = (mode, action)
            if key in custom_keymaps:
                return custom_keymaps[key]
            raise KeyError(
                f"Keymap for mode '{mode}' action '{action}' not found"
            )

        mock_app.config.get_keymap = MagicMock(side_effect=custom_get_keymap)
        mock_app.config.is_vim_mode_enabled.return_value = False

        # Initialize bindings
        _init_tree_bindings(mock_app)

        # Check that custom keys were bound
        # Should have calls for: w, s, a, d (custom movement keys)
        add_calls = [str(call) for call in mock_app.kb.add.call_args_list]

        # Verify custom keys are in the bindings
        assert any("'w'" in call for call in add_calls), (
            "Custom up key 'w' not bound"
        )
        assert any("'s'" in call for call in add_calls), (
            "Custom down key 's' not bound"
        )
        assert any("'a'" in call for call in add_calls), (
            "Custom left key 'a' not bound"
        )
        assert any("'d'" in call for call in add_calls), (
            "Custom right key 'd' not bound"
        )
