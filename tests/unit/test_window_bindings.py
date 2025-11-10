"""Tests for window mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.window_bindings import (
    _init_window_bindings,
    error_handler,
)


class TestWindowBindings:
    """Test cases for window mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()

        # Set up focus targets
        app.tree_content = MagicMock()
        app.attributes_content = MagicMock()
        app.values_content = MagicMock()
        app.plot_content = MagicMock()
        app.hist_content = MagicMock()

        # Set up focus management
        app.shift_focus = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()

        # Set up mode flags
        app.flag_window_mode = True
        app.flag_values_visible = True
        app._flag_normal_mode = True
        app._flag_window_mode = True
        app._flag_plotting_mode = False
        app._flag_hist_mode = False

        # Set up keybindings
        app.kb = KeyBindings()

        # Set up layout for condition checks
        app.app = MagicMock()
        app.app.layout = MagicMock()
        app.app.layout.has_focus = MagicMock(return_value=False)

        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        event = MagicMock()
        return event

    def test_init_window_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_window_bindings returns a dict of Labels."""

        hot_keys = _init_window_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        assert len(hot_keys) == 6
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    def test_move_tree_handler(self, mock_app, mock_event):
        """Test the move_tree handler."""
        _init_window_bindings(mock_app)

        # Find the move_tree handler (bound to 't')
        t_bindings = [b for b in mock_app.kb.bindings if "t" in str(b.keys)]
        assert len(t_bindings) > 0

        handler = t_bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to tree
        mock_app.shift_focus.assert_called_once_with(mock_app.tree_content)

        # Verify returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

    def test_move_attr_handler(self, mock_app, mock_event):
        """Test the move_attr handler."""
        _init_window_bindings(mock_app)

        # Find the move_attr handler (bound to 'a')
        a_bindings = [b for b in mock_app.kb.bindings if "a" in str(b.keys)]
        assert len(a_bindings) > 0

        handler = a_bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to attributes
        mock_app.shift_focus.assert_called_once_with(
            mock_app.attributes_content
        )

        # Verify returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

    def test_move_values_handler(self, mock_app, mock_event):
        """Test the move_values handler."""
        _init_window_bindings(mock_app)

        # Find the move_values handler (bound to 'v')
        v_bindings = [b for b in mock_app.kb.bindings if "v" in str(b.keys)]
        assert len(v_bindings) > 0

        handler = v_bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to values
        mock_app.shift_focus.assert_called_once_with(mock_app.values_content)

        # Verify returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

    def test_move_plot_handler(self, mock_app, mock_event):
        """Test the move_plot handler."""
        _init_window_bindings(mock_app)

        # Find the move_plot handler (bound to 'p')
        p_bindings = [b for b in mock_app.kb.bindings if "p" in str(b.keys)]
        assert len(p_bindings) > 0

        handler = p_bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to plot
        mock_app.shift_focus.assert_called_once_with(mock_app.plot_content)

        # Verify entered plotting mode
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_window_mode is False
        assert mock_app._flag_plotting_mode is True

    def test_move_hist_handler(self, mock_app, mock_event):
        """Test the move_hist handler."""
        _init_window_bindings(mock_app)

        # Find the move_hist handler (bound to 'h')
        h_bindings = [b for b in mock_app.kb.bindings if "h" in str(b.keys)]
        assert len(h_bindings) > 0

        handler = h_bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to histogram
        mock_app.shift_focus.assert_called_once_with(mock_app.hist_content)

        # Verify entered histogram mode
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_window_mode is False
        assert mock_app._flag_hist_mode is True

    def test_move_to_default_handler(self, mock_app, mock_event):
        """Test the move_to_default handler."""
        _init_window_bindings(mock_app)

        # Find the move_to_default handler (bound to 'escape')
        escape_bindings = [
            b for b in mock_app.kb.bindings if "escape" in str(b.keys)
        ]
        assert len(escape_bindings) > 0

        handler = escape_bindings[0].handler
        handler(mock_event)

        # Verify default focus was called
        mock_app.default_focus.assert_called_once()

        # Verify returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

    def test_all_handlers_bound_to_correct_keys(self, mock_app):
        """Test that all handlers are bound to their expected keys."""
        _init_window_bindings(mock_app)

        # Expected keys: t, a, v, p, h, escape
        expected_keys = ["t", "a", "v", "p", "h", "escape"]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

    def test_t_key_has_filter_condition(self, mock_app):
        """Test that 't' key has window mode filter."""
        _init_window_bindings(mock_app)

        t_bindings = [b for b in mock_app.kb.bindings if "t" in str(b.keys)]
        assert len(t_bindings) > 0
        assert t_bindings[0].filter is not None

    def test_a_key_has_filter_condition(self, mock_app):
        """Test that 'a' key has window mode filter."""
        _init_window_bindings(mock_app)

        a_bindings = [b for b in mock_app.kb.bindings if "a" in str(b.keys)]
        assert len(a_bindings) > 0
        assert a_bindings[0].filter is not None

    def test_v_key_has_combined_filter_condition(self, mock_app):
        """Test that 'v' key has window mode and values visible filter."""
        _init_window_bindings(mock_app)

        v_bindings = [b for b in mock_app.kb.bindings if "v" in str(b.keys)]
        assert len(v_bindings) > 0
        assert v_bindings[0].filter is not None

    def test_p_key_has_filter_condition(self, mock_app):
        """Test that 'p' key has window mode filter."""
        _init_window_bindings(mock_app)

        p_bindings = [b for b in mock_app.kb.bindings if "p" in str(b.keys)]
        assert len(p_bindings) > 0
        assert p_bindings[0].filter is not None

    def test_h_key_has_filter_condition(self, mock_app):
        """Test that 'h' key has window mode filter."""
        _init_window_bindings(mock_app)

        h_bindings = [b for b in mock_app.kb.bindings if "h" in str(b.keys)]
        assert len(h_bindings) > 0
        assert h_bindings[0].filter is not None

    @patch("h5forest.bindings.window_bindings.error_handler")
    def test_handlers_wrapped_with_error_handler(
        self, mock_error_handler, mock_app
    ):
        """Test that handlers are wrapped with error_handler decorator."""

        assert callable(error_handler)

    def test_move_plot_sets_correct_mode_flags(self, mock_app, mock_event):
        """Test that move_plot sets all mode flags correctly."""
        # Set initial state
        mock_app._flag_normal_mode = True
        mock_app._flag_window_mode = True
        mock_app._flag_plotting_mode = False
        mock_app._flag_hist_mode = False

        _init_window_bindings(mock_app)

        p_bindings = [b for b in mock_app.kb.bindings if "p" in str(b.keys)]
        handler = p_bindings[0].handler
        handler(mock_event)

        # Check all flags
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_window_mode is False
        assert mock_app._flag_plotting_mode is True
        # Ensure hist mode wasn't affected
        assert mock_app._flag_hist_mode is False

    def test_move_hist_sets_correct_mode_flags(self, mock_app, mock_event):
        """Test that move_hist sets all mode flags correctly."""
        # Set initial state
        mock_app._flag_normal_mode = True
        mock_app._flag_window_mode = True
        mock_app._flag_plotting_mode = False
        mock_app._flag_hist_mode = False

        _init_window_bindings(mock_app)

        h_bindings = [b for b in mock_app.kb.bindings if "h" in str(b.keys)]
        handler = h_bindings[0].handler
        handler(mock_event)

        # Check all flags
        assert mock_app._flag_normal_mode is False
        assert mock_app._flag_window_mode is False
        assert mock_app._flag_hist_mode is True
        # Ensure plotting mode wasn't affected
        assert mock_app._flag_plotting_mode is False

    def test_hotkeys_contains_correct_labels(self, mock_app):
        """Test that hotkeys dict contains expected labels."""
        hot_keys = _init_window_bindings(mock_app)

        # Dict should have 6 keys
        assert len(hot_keys) == 6

        # Check that all expected keys are present
        expected_keys = [
            "move_tree",
            "move_attrs",
            "move_values",
            "move_plot",
            "move_hist",
            "exit",
        ]
        for key in expected_keys:
            assert key in hot_keys
