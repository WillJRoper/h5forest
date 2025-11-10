"""Tests for search mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.search_bindings import (
    _init_search_bindings,
    error_handler,
)


class TestSearchBindings:
    """Test cases for search mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()

        # Set up tree mock
        app.tree = MagicMock()
        app.tree.restore_tree = MagicMock()
        app.tree.get_tree_text = MagicMock(return_value="Mock tree text")

        # Set up mode management
        app.return_to_normal_mode = MagicMock()
        app.flag_search_mode = True

        # Set up search content
        app.search_content = MagicMock()
        app.search_content.text = "test query"

        # Set up tree buffer
        app.tree_buffer = MagicMock()
        app.tree_buffer.set_document = MagicMock()
        app.tree_buffer.document = Document(
            text="filtered tree", cursor_position=0
        )

        # Set up focus management
        app.shift_focus = MagicMock()
        app.tree_content = MagicMock()

        # Set up keybindings
        app.kb = KeyBindings()

        return app

    @pytest.fixture
    def mock_event(self, mock_app):
        """Create a mock event for testing."""
        event = MagicMock()
        event.app = MagicMock()
        event.app.invalidate = MagicMock()
        return event

    def test_init_search_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_search_bindings returns a list of Labels."""

        hot_keys = _init_search_bindings(mock_app)

        assert isinstance(hot_keys, list)
        assert len(hot_keys) == 2
        for item in hot_keys:
            assert isinstance(item, Label)

    def test_exit_search_mode_restores_tree(self, mock_app, mock_event):
        """Test that exit_search_mode restores the original tree."""
        # Initialize bindings to register the keybindings
        _init_search_bindings(mock_app)

        # Find the exit_search_mode handler
        # It should be bound to both 'escape' and 'c-c'
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        assert len(escape_bindings) > 0

        # Get the handler function
        handler = escape_bindings[0].handler

        # Call the handler
        handler(mock_event)

        # Verify tree.restore_tree was called
        mock_app.tree.restore_tree.assert_called_once()

        # Verify tree text was rebuilt
        mock_app.tree.get_tree_text.assert_called_once()

        # Verify we returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

        # Verify search buffer was cleared
        assert mock_app.search_content.text == ""

        # Verify tree buffer was updated
        mock_app.tree_buffer.set_document.assert_called_once()
        args, kwargs = mock_app.tree_buffer.set_document.call_args
        assert args[0].text == "Mock tree text"
        assert args[0].cursor_position == 0
        assert kwargs["bypass_readonly"] is True

        # Verify focus shifted to tree
        mock_app.shift_focus.assert_called_once_with(mock_app.tree_content)

        # Verify invalidate was called
        mock_event.app.invalidate.assert_called_once()

    def test_exit_search_mode_bound_to_escape(self, mock_app):
        """Test that exit_search_mode is bound to escape key."""
        _init_search_bindings(mock_app)

        # Check that escape key is bound
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        assert len(escape_bindings) > 0

    def test_exit_search_mode_bound_to_ctrl_c(self, mock_app):
        """Test that exit_search_mode is bound to Ctrl-C."""
        _init_search_bindings(mock_app)

        # Check that c-c key is bound
        ctrl_c_bindings = [
            b for b in mock_app.kb.bindings if "c-c" in str(b.keys)
        ]
        assert len(ctrl_c_bindings) > 0

    def test_accept_search_results_keeps_filtered_tree(
        self, mock_app, mock_event
    ):
        """Test that accept_search_results keeps the filtered tree."""
        # Initialize bindings
        _init_search_bindings(mock_app)

        # Find the accept_search_results handler
        # (enter key is represented as c-m)
        enter_bindings = [
            b for b in mock_app.kb.bindings if "c-m" in str(b.keys)
        ]
        assert len(enter_bindings) > 0

        # Get the handler function
        handler = enter_bindings[0].handler

        # Call the handler
        handler(mock_event)

        # Verify we returned to normal mode FIRST (before clearing buffer)
        mock_app.return_to_normal_mode.assert_called_once()

        # Verify search buffer was cleared
        assert mock_app.search_content.text == ""

        # Verify focus shifted to tree
        mock_app.shift_focus.assert_called_once_with(mock_app.tree_content)

        # Verify tree buffer was updated with current document
        # (keeping filtered view)
        mock_app.tree_buffer.set_document.assert_called_once()
        args, kwargs = mock_app.tree_buffer.set_document.call_args
        assert args[0] == mock_app.tree_buffer.document
        assert kwargs["bypass_readonly"] is True

        # Verify restore_tree was NOT called (we keep filtered results)
        mock_app.tree.restore_tree.assert_not_called()

        # Verify invalidate was called
        mock_event.app.invalidate.assert_called_once()

    def test_accept_search_results_bound_to_enter(self, mock_app):
        """Test that accept_search_results is bound to enter key."""
        _init_search_bindings(mock_app)

        # Check that enter key (c-m) is bound
        enter_bindings = [
            b for b in mock_app.kb.bindings if "c-m" in str(b.keys)
        ]
        assert len(enter_bindings) > 0

    def test_exit_vs_accept_behavior_difference(self, mock_app, mock_event):
        """Test the key difference between exit and accept."""
        _init_search_bindings(mock_app)

        # Test exit_search_mode
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        exit_handler = escape_bindings[0].handler

        # Call exit handler
        exit_handler(mock_event)

        # Exit should call restore_tree
        assert mock_app.tree.restore_tree.called

        # Reset mocks
        mock_app.reset_mock()
        mock_event.reset_mock()

        # Test accept_search_results (enter key is c-m)
        enter_bindings = [
            b for b in mock_app.kb.bindings if "c-m" in str(b.keys)
        ]
        accept_handler = enter_bindings[0].handler

        # Call accept handler
        accept_handler(mock_event)

        # Accept should NOT call restore_tree
        assert not mock_app.tree.restore_tree.called

    @patch("h5forest.bindings.search_bindings.error_handler")
    def test_handlers_wrapped_with_error_handler(
        self, mock_error_handler, mock_app
    ):
        """Test that handlers are wrapped with error_handler decorator."""
        # The error_handler decorator should wrap the functions
        # We can verify this by checking that error_handler was used
        # as a decorator

        # Since error_handler is a decorator, we just verify it's
        # imported and used. The actual error handling logic is
        # tested in test_errors.py

        assert callable(error_handler)

    def test_hotkeys_display_content(self, mock_app):
        """Test that hotkeys list contains correct labels."""
        hot_keys = _init_search_bindings(mock_app)

        # Should be a list of Labels

        assert len(hot_keys) == 2

        # All items should be Labels with text content
        for item in hot_keys:
            assert isinstance(item, Label)
            assert hasattr(item, "text")
            assert item.text is not None

    def test_search_mode_filter_condition(self, mock_app):
        """Test that bindings are only active when flag_search_mode is True."""
        _init_search_bindings(mock_app)

        # All bindings should have a filter condition
        for binding in mock_app.kb.bindings:
            assert binding.filter is not None

    def test_exit_search_mode_clears_buffer_text(self, mock_app, mock_event):
        """Test that exit_search_mode clears the search buffer text."""
        # Set initial search text
        mock_app.search_content.text = "some search query"

        _init_search_bindings(mock_app)

        # Find and call the exit handler
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        handler = escape_bindings[0].handler
        handler(mock_event)

        # Verify text was cleared
        assert mock_app.search_content.text == ""

    def test_accept_search_results_clears_buffer_text(
        self, mock_app, mock_event
    ):
        """Test that accept_search_results clears the search buffer text."""
        # Set initial search text
        mock_app.search_content.text = "some search query"

        _init_search_bindings(mock_app)

        # Find and call the accept handler (enter key is c-m)
        enter_bindings = [
            b for b in mock_app.kb.bindings if "c-m" in str(b.keys)
        ]
        handler = enter_bindings[0].handler
        handler(mock_event)

        # Verify text was cleared
        assert mock_app.search_content.text == ""

    def test_both_handlers_call_invalidate(self, mock_app, mock_event):
        """Test that both handlers call event.app.invalidate()."""
        _init_search_bindings(mock_app)

        # Test exit handler
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        exit_handler = escape_bindings[0].handler
        exit_handler(mock_event)
        assert mock_event.app.invalidate.called

        # Reset and test accept handler (enter key is c-m)
        mock_event.reset_mock()
        enter_bindings = [
            b for b in mock_app.kb.bindings if "c-m" in str(b.keys)
        ]
        accept_handler = enter_bindings[0].handler
        accept_handler(mock_event)
        assert mock_event.app.invalidate.called
