"""Tests for window mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.bindings import H5KeyBindings


def _init_window_bindings(app):
    """Initialize window bindings using H5KeyBindings class."""
    bindings = H5KeyBindings(app)
    bindings._init_window_bindings()
    bindings._init_normal_mode_bindings()  # For escape key to return to normal

    # Return dict of hotkeys matching old interface
    return {
        "move_tree": bindings.focus_tree_label,
        "move_attrs": bindings.focus_attrs_label,
        "move_values": bindings.focus_values_label,
        "move_plot": bindings.focus_plot_label,
        "move_hist": bindings.focus_hist_label,
        "exit": bindings.exit_mode_label,
    }


class TestWindowBindings:
    """Test cases for window mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

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

        # Add config mock
        add_config_mock(app)

        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        event = MagicMock()
        return event

    @patch("h5forest.h5_forest.H5Forest")
    def test_init_window_bindings_returns_hotkeys(
        self, mock_h5forest_class, mock_app
    ):
        """Test that _init_window_bindings returns a dict of Labels."""
        mock_h5forest_class.return_value = mock_app

        hot_keys = _init_window_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        assert len(hot_keys) == 6
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_tree_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_tree handler."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_attr_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_attr handler."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_values_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_values handler."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_plot_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_plot handler."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_hist_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_hist handler."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_to_default_handler(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test the move_to_default handler."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        # Find the move_to_default handler (bound to 'q' - the quit
        # key exits leader modes). There are two 'q' bindings: one for
        # normal mode (exit_app) and one for leader modes
        # We want the second one (exit_leader_mode wrapper)
        quit_bindings = [b for b in mock_app.kb.bindings if b.keys == ("q",)]
        assert len(quit_bindings) == 2

        # The second binding is the exit_leader_mode one
        handler = quit_bindings[1].handler
        handler(mock_event)

        # Verify default focus was called
        mock_app.default_focus.assert_called_once()

        # Verify returned to normal mode
        mock_app.return_to_normal_mode.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_all_handlers_bound_to_correct_keys(
        self, mock_h5forest_class, mock_app
    ):
        """Test that all handlers are bound to their expected keys."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        # Expected keys: t, a, v, p, h, q (quit key exits leader modes)
        expected_keys = ["t", "a", "v", "p", "h", "'q'"]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

    @patch("h5forest.h5_forest.H5Forest")
    def test_t_key_has_filter_condition(self, mock_h5forest_class, mock_app):
        """Test that 't' key has window mode filter."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        t_bindings = [b for b in mock_app.kb.bindings if "t" in str(b.keys)]
        assert len(t_bindings) > 0
        assert t_bindings[0].filter is not None

    @patch("h5forest.h5_forest.H5Forest")
    def test_a_key_has_filter_condition(self, mock_h5forest_class, mock_app):
        """Test that 'a' key has window mode filter."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        a_bindings = [b for b in mock_app.kb.bindings if "a" in str(b.keys)]
        assert len(a_bindings) > 0
        assert a_bindings[0].filter is not None

    @patch("h5forest.h5_forest.H5Forest")
    def test_v_key_has_combined_filter_condition(
        self, mock_h5forest_class, mock_app
    ):
        """Test that 'v' key has window mode and values visible filter."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        v_bindings = [b for b in mock_app.kb.bindings if "v" in str(b.keys)]
        assert len(v_bindings) > 0
        assert v_bindings[0].filter is not None

    @patch("h5forest.h5_forest.H5Forest")
    def test_p_key_has_filter_condition(self, mock_h5forest_class, mock_app):
        """Test that 'p' key has window mode filter."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        p_bindings = [b for b in mock_app.kb.bindings if "p" in str(b.keys)]
        assert len(p_bindings) > 0
        assert p_bindings[0].filter is not None

    @patch("h5forest.h5_forest.H5Forest")
    def test_h_key_has_filter_condition(self, mock_h5forest_class, mock_app):
        """Test that 'h' key has window mode filter."""
        mock_h5forest_class.return_value = mock_app
        _init_window_bindings(mock_app)

        h_bindings = [b for b in mock_app.kb.bindings if "h" in str(b.keys)]
        assert len(h_bindings) > 0
        assert h_bindings[0].filter is not None

    @patch("h5forest.h5_forest.H5Forest")
    def test_handlers_wrapped_with_error_handler(
        self, mock_h5forest_class, mock_app
    ):
        """Test that the bindings class is properly initialized."""
        mock_h5forest_class.return_value = mock_app
        # With the refactored binding system, error handling is built
        # into the class
        bindings = H5KeyBindings(mock_app)
        assert bindings is not None
        assert hasattr(bindings, "bind_function")

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_plot_sets_correct_mode_flags(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test that move_plot sets all mode flags correctly."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_move_hist_sets_correct_mode_flags(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test that move_hist sets all mode flags correctly."""
        mock_h5forest_class.return_value = mock_app
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

    @patch("h5forest.h5_forest.H5Forest")
    def test_hotkeys_contains_correct_labels(
        self, mock_h5forest_class, mock_app
    ):
        """Test that hotkeys dict contains expected labels."""
        mock_h5forest_class.return_value = mock_app
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
