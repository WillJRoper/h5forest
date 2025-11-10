"""Tests for histogram mode keybindings."""

from unittest.mock import MagicMock

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.hist_bindings import _init_hist_bindings


class TestHistBindings:
    """Test cases for histogram mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()
        app.flag_hist_mode = True
        app.tree = MagicMock()
        app.current_row = 0
        app.histogram_plotter = MagicMock()
        app.histogram_plotter.get_row = MagicMock(return_value="param: value")
        app.histogram_plotter.set_data_key = MagicMock(
            return_value="data key text"
        )
        app.histogram_plotter.compute_hist = MagicMock(
            return_value="computed hist"
        )
        app.histogram_plotter.plot_and_show = MagicMock()
        app.histogram_plotter.plot_and_save = MagicMock()
        app.histogram_plotter.reset = MagicMock(return_value="reset text")
        app.histogram_plotter.close = MagicMock()
        app.histogram_plotter.plot_params = {"data": "test_data"}
        app.histogram_plotter.plot_text = ""
        app.histogram_plotter.x_min = 1.0
        app.histogram_plotter.x_max = 100.0
        app.histogram_plotter.assign_data_thread = None
        app.hist_content = MagicMock()
        app.hist_content.text = (
            "data:        <key>\n"
            "nbins:       50\n"
            "x-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )
        app.hist_content.document = MagicMock()
        app.hist_content.document.cursor_position_row = 0
        app.hist_content.document.cursor_position = 10
        app.tree_content = MagicMock()
        app.shift_focus = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()
        app.print = MagicMock()
        app.input = MagicMock()
        app.user_input = ""
        app.kb = KeyBindings()
        app.app = MagicMock()
        app.app.layout = MagicMock()
        app.app.layout.has_focus = MagicMock(return_value=False)
        app.app.invalidate = MagicMock()
        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        return MagicMock()

    def test_init_hist_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_hist_bindings returns a dict of Labels."""

        hot_keys = _init_hist_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        assert len(hot_keys) == 12
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    def test_edit_hist_entry_toggle_linear_to_log(self, mock_app, mock_event):
        """Test toggling scale from linear to log."""
        _init_hist_bindings(mock_app)
        mock_app.app.layout.has_focus = MagicMock(return_value=True)
        mock_app.hist_content.text = "x-scale:     linear"
        mock_app.histogram_plotter.get_row = MagicMock(
            return_value="x-scale: linear"
        )
        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        assert len(bindings) > 0
        # Find the edit_hist_entry binding (the one that requires focus on
        # hist_content)
        handler = None
        for binding in bindings:
            if binding.filter():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            assert "log" in mock_app.hist_content.text
            mock_app.app.invalidate.assert_called_once()

    def test_edit_hist_entry_toggle_log_to_linear(self, mock_app, mock_event):
        """Test toggling scale from log to linear."""
        _init_hist_bindings(mock_app)
        mock_app.app.layout.has_focus = MagicMock(return_value=True)
        mock_app.hist_content.text = "x-scale:     log"
        mock_app.histogram_plotter.get_row = MagicMock(
            return_value="x-scale: log"
        )
        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = None
        for binding in bindings:
            if binding.filter():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            assert "linear" in mock_app.hist_content.text

    def test_edit_hist_entry_callback(self, mock_app, mock_event):
        """Test editing a non-scale parameter with callback."""
        _init_hist_bindings(mock_app)
        mock_app.app.layout.has_focus = MagicMock(return_value=True)
        mock_app.hist_content.text = "title:       My Hist"
        mock_app.histogram_plotter.get_row = MagicMock(
            return_value="title: My Hist"
        )
        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = None
        for binding in bindings:
            if binding.filter():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            mock_app.input.assert_called_once()
            callback = mock_app.input.call_args[0][1]
            mock_app.user_input = "New Title"
            callback()
            assert "New Title" in mock_app.hist_content.text
            mock_app.shift_focus.assert_called_with(mock_app.hist_content)

    def test_plot_hist_with_empty_params(self, mock_app, mock_event):
        """Test plotting histogram when params are empty."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {}
        node = MagicMock()
        node.is_group = False
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("h",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.histogram_plotter.set_data_key.assert_called_once_with(node)
        mock_app.histogram_plotter.compute_hist.assert_called_once()
        mock_app.histogram_plotter.plot_and_show.assert_called_once()

    def test_plot_hist_with_existing_params(self, mock_app, mock_event):
        """Test plotting histogram with existing params."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {"data": "test"}
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("h",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.histogram_plotter.set_data_key.assert_not_called()
        mock_app.histogram_plotter.compute_hist.assert_called_once()

    def test_plot_hist_with_group_node(self, mock_app, mock_event):
        """Test plotting histogram with group node (should fail)."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {}
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("h",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    def test_save_hist(self, mock_app, mock_event):
        """Test saving histogram."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {"data": "test"}
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("H",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.histogram_plotter.plot_and_save.assert_called_once()

    def test_save_hist_with_group_node(self, mock_app, mock_event):
        """Test saving histogram with group node (should fail)."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {}
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("H",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    def test_save_hist_with_empty_params(self, mock_app, mock_event):
        """Test saving histogram with empty params and dataset."""
        _init_hist_bindings(mock_app)
        mock_app.histogram_plotter.plot_params = {}
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        mock_app.histogram_plotter.set_data_key = MagicMock(
            return_value="data key text"
        )
        mock_app.histogram_plotter.compute_hist = MagicMock(
            return_value="computed hist"
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("H",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.histogram_plotter.set_data_key.assert_called_once_with(node)
        mock_app.histogram_plotter.compute_hist.assert_called_once()
        mock_app.histogram_plotter.plot_and_save.assert_called_once()

    def test_reset_hist(self, mock_app, mock_event):
        """Test resetting histogram."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("r",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.histogram_plotter.close.assert_called_once()
        mock_app.histogram_plotter.reset.assert_called_once()
        assert mock_app.hist_content.text == "reset text"
        mock_app.return_to_normal_mode.assert_called_once()

    def test_jump_to_config(self, mock_app, mock_event):
        """Test jumping to config mode."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("e",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.shift_focus.assert_called_once_with(mock_app.hist_content)

    def test_jump_to_config_when_already_in_config(self, mock_app, mock_event):
        """Test jumping from config back to tree."""
        # Set focus to be on hist_content
        mock_app.app.layout.has_focus = MagicMock(
            side_effect=lambda content: content == mock_app.hist_content
        )
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("e",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Should jump back to tree when already in config
        mock_app.shift_focus.assert_called_once_with(mock_app.tree_content)

    def test_exit_edit_hist(self, mock_app, mock_event):
        """Test exiting edit histogram mode."""
        mock_app.app.layout.has_focus = MagicMock(return_value=True)
        _init_hist_bindings(mock_app)
        bindings = [b for b in mock_app.kb.bindings if b.keys == ("q",)]
        handler = bindings[-1].handler
        handler(mock_event)
        mock_app.shift_focus.assert_called_with(mock_app.tree_content)

    def test_select_data(self, mock_app, mock_event):
        """Test selecting data for histogram."""
        _init_hist_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c-m",) and b.filter is not None
        ]
        # Find the binding that's not for hist_content
        handler = None
        for binding in bindings:
            if binding.filter() and not mock_app.app.layout.has_focus():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            mock_app.histogram_plotter.set_data_key.assert_called_once_with(
                node
            )

    def test_select_data_with_group(self, mock_app, mock_event):
        """Test selecting data with group node (should fail)."""
        _init_hist_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c-m",) and b.filter is not None
        ]
        handler = None
        for binding in bindings:
            if binding.filter() and not mock_app.app.layout.has_focus():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            mock_app.print.assert_called_once_with("/group is not a Dataset")

    def test_edit_bins(self, mock_app, mock_event):
        """Test editing bins."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("b",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.input.assert_called_once()

    def test_edit_bins_callback(self, mock_app, mock_event):
        """Test editing bins callback updates the value."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("b",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Get the callback that was passed to input
        callback = mock_app.input.call_args[0][1]
        mock_app.user_input = "100"

        # Call the callback
        callback()

        # Verify the bins value was updated
        assert "nbins:       100" in mock_app.hist_content.text
        mock_app.shift_focus.assert_called_with(mock_app.tree_content)

    def test_toggle_x_scale_linear_to_log(self, mock_app, mock_event):
        """Test toggling x scale from linear to log."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert "x-scale:     log" in mock_app.hist_content.text
        mock_app.app.invalidate.assert_called()

    def test_toggle_x_scale_log_to_linear(self, mock_app, mock_event):
        """Test toggling x scale from log to linear."""
        _init_hist_bindings(mock_app)

        # Set initial state to log
        mock_app.hist_content.text = (
            "data:        <key>\n"
            "nbins:       50\n"
            "x-label:     <label>\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
        )

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert "x-scale:     linear" in mock_app.hist_content.text
        mock_app.app.invalidate.assert_called()

    def test_toggle_y_scale_linear_to_log(self, mock_app, mock_event):
        """Test toggling y scale from linear to log."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert "y-scale:     log" in mock_app.hist_content.text
        mock_app.app.invalidate.assert_called()

    def test_toggle_y_scale_log_to_linear(self, mock_app, mock_event):
        """Test toggling y scale from log to linear."""
        _init_hist_bindings(mock_app)

        # Set initial state to log
        mock_app.hist_content.text = (
            "data:        <key>\n"
            "nbins:       50\n"
            "x-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     log\n"
        )

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert "y-scale:     linear" in mock_app.hist_content.text
        mock_app.app.invalidate.assert_called()

    def test_toggle_x_scale_with_none_x_min(self, mock_app, mock_event):
        """Test toggling x scale when x_min is None."""
        mock_app.histogram_plotter.x_min = None
        mock_app.histogram_plotter.x_max = None
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "data range not yet computed" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.hist_content.text

    def test_toggle_x_scale_to_log_with_zero_values(
        self, mock_app, mock_event
    ):
        """Test toggling x scale to log when x_min is 0."""
        mock_app.histogram_plotter.x_min = 0
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "zero" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.hist_content.text

    def test_toggle_x_scale_to_log_with_negative_values(
        self, mock_app, mock_event
    ):
        """Test toggling x scale to log when x_min is negative."""
        mock_app.histogram_plotter.x_min = -5.0
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "negative" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.hist_content.text

    def test_toggle_y_scale_with_none_x_min(self, mock_app, mock_event):
        """Test toggling y scale when x_min is None."""
        mock_app.histogram_plotter.x_min = None
        mock_app.histogram_plotter.x_max = None
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "data range not yet computed" in error_msg
        # Verify scale was NOT changed
        assert "y-scale:     linear" in mock_app.hist_content.text

    def test_edit_bins_with_none_x_min(self, mock_app, mock_event):
        """Test editing bins when x_min is None."""
        mock_app.histogram_plotter.x_min = None
        mock_app.histogram_plotter.x_max = None
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("b",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "data range not yet computed" in error_msg
        # Verify input was NOT called
        mock_app.input.assert_not_called()

    def test_toggle_x_scale_with_running_thread(self, mock_app, mock_event):
        """Test toggling x scale with a running assign_data_thread."""

        # Create a mock thread
        mock_thread = MagicMock()
        mock_app.histogram_plotter.assign_data_thread = mock_thread
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify thread was joined
        mock_thread.join.assert_called_once()
        # Verify scale was toggled
        assert "x-scale:     log" in mock_app.hist_content.text

    def test_edit_bins_with_running_thread(self, mock_app, mock_event):
        """Test editing bins with a running assign_data_thread."""

        # Create a mock thread
        mock_thread = MagicMock()
        mock_app.histogram_plotter.assign_data_thread = mock_thread
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("b",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify thread was joined
        mock_thread.join.assert_called_once()
        # Verify input was called (since x_min/x_max are valid)
        mock_app.input.assert_called_once()

    def test_toggle_y_scale_with_running_thread(self, mock_app, mock_event):
        """Test toggling y scale with a running assign_data_thread."""

        # Create a mock thread
        mock_thread = MagicMock()
        mock_app.histogram_plotter.assign_data_thread = mock_thread
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify thread was joined
        mock_thread.join.assert_called_once()
        # Verify scale was toggled
        assert "y-scale:     log" in mock_app.hist_content.text

    def test_exit_hist_mode(self, mock_app, mock_event):
        """Test exiting histogram mode."""
        _init_hist_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("q",) and b.filter is not None
        ]
        # Find the exit_hist_mode binding
        handler = None
        for binding in bindings:
            if binding.filter() and not mock_app.app.layout.has_focus():
                handler = binding.handler
                break
        if handler:
            handler(mock_event)
            mock_app.histogram_plotter.close.assert_called_once()
            mock_app.histogram_plotter.reset.assert_called_once()
            mock_app.return_to_normal_mode.assert_called_once()

    def test_all_keys_bound(self, mock_app):
        """Test that all expected keys are bound."""
        _init_hist_bindings(mock_app)
        for key in ["c-m", "b", "x", "y", "h", "H", "r", "e", "q"]:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"
