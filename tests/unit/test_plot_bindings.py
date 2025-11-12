"""Tests for plotting mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.bindings import H5KeyBindings


def _init_plot_bindings(app):
    """Initialize plot bindings using H5KeyBindings class."""
    bindings = H5KeyBindings(app)
    bindings._init_plot_bindings()
    bindings._init_normal_mode_bindings()  # For q key to exit mode

    # Return dict of hotkeys matching old interface
    return {
        "edit_plot_config": bindings.edit_plot_config_label,
        "exit_plot_edit": bindings.exit_plot_edit_label,
        "edit_plot_entry": bindings.edit_plot_entry_label,
        "select_x_data": bindings.select_x_data_label,
        "select_y_data": bindings.select_y_data_label,
        "toggle_x_log_scale": bindings.toggle_x_log_scale_label,
        "toggle_y_log_scale": bindings.toggle_y_log_scale_label,
        "reset_plot": bindings.reset_plot_label,
        "show_plot": bindings.show_plot_label,
        "save_plot": bindings.save_plot_label,
        "exit_mode": bindings.exit_mode_label,
        "exit": bindings.exit_label,
    }


class TestPlotBindings:
    """Test cases for plotting mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        from tests.conftest import add_config_mock

        app = MagicMock()

        # Set up mode flags
        app.flag_plotting_mode = True

        # Set up tree
        app.tree = MagicMock()
        app.current_row = 0

        # Set up scatter plotter
        app.scatter_plotter = MagicMock()
        app.scatter_plotter.set_x_key = MagicMock(return_value="x-axis text")
        app.scatter_plotter.set_y_key = MagicMock(return_value="y-axis text")
        app.scatter_plotter.get_row = MagicMock(return_value="param: value")
        app.scatter_plotter.plot_and_show = MagicMock()
        app.scatter_plotter.plot_and_save = MagicMock()
        app.scatter_plotter.reset = MagicMock(return_value="reset text")
        app.scatter_plotter.close = MagicMock()
        app.scatter_plotter.plot_params = {"x": "data1", "y": "data2"}
        app.scatter_plotter.plot_text = ""
        app.scatter_plotter.__len__ = MagicMock(return_value=2)
        app.scatter_plotter.x_min = 1.0
        app.scatter_plotter.x_max = 100.0
        app.scatter_plotter.y_min = 1.0
        app.scatter_plotter.y_max = 100.0
        app.scatter_plotter.assignx_thread = None
        app.scatter_plotter.assigny_thread = None

        # Set up plot content
        app.plot_content = MagicMock()
        app.plot_content.text = (
            "x-axis:      <key>\n"
            "y-axis:      <key>\n"
            "x-label:     <label>\n"
            "y-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )
        app.plot_content.document = MagicMock()
        app.plot_content.document.cursor_position_row = 0
        app.plot_content.document.cursor_position = 10

        # Set up tree content
        app.tree_content = MagicMock()

        # Set up focus and UI
        app.shift_focus = MagicMock()
        app.default_focus = MagicMock()
        app.return_to_normal_mode = MagicMock()
        app.print = MagicMock()
        app.input = MagicMock()
        app.user_input = ""

        # Set up keybindings
        app.kb = KeyBindings()

        # Set up layout
        app.app = MagicMock()
        app.app.layout = MagicMock()
        app.app.layout.has_focus = MagicMock(return_value=False)
        app.app.invalidate = MagicMock()

        add_config_mock(app)
        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        event = MagicMock()
        return event

    @patch("h5forest.h5_forest.H5Forest")
    def test_init_plot_bindings_returns_hotkeys(
        self, mock_h5forest_class, mock_app
    ):
        """Test that _init_plot_bindings returns a dict of Labels."""
        mock_h5forest_class.return_value = mock_app

        hot_keys = _init_plot_bindings(mock_app)
        assert isinstance(hot_keys, dict)
        assert len(hot_keys) == 12
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    @patch("h5forest.h5_forest.H5Forest")
    def test_select_x_with_dataset(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test selecting x-axis with a dataset node."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Create a dataset node
        node = MagicMock()
        node.is_group = False
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        # Find the select_x handler
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify set_x_key was called
        mock_app.scatter_plotter.set_x_key.assert_called_once_with(node)

        # Verify plot content was updated
        assert mock_app.plot_content.text == "x-axis text"

    @patch("h5forest.h5_forest.H5Forest")
    def test_select_x_with_group(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test selecting x-axis with a group node (should fail)."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Create a group node
        node = MagicMock()
        node.is_group = True
        node.path = "/some/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("x",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was printed
        mock_app.print.assert_called_once_with("/some/group is not a Dataset")

        # Verify set_x_key was NOT called
        mock_app.scatter_plotter.set_x_key.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_select_y_with_dataset(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test selecting y-axis with a dataset node."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Create a dataset node
        node = MagicMock()
        node.is_group = False
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        # Find the select_y handler
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify set_y_key was called
        mock_app.scatter_plotter.set_y_key.assert_called_once_with(node)

        # Verify plot content was updated
        assert mock_app.plot_content.text == "y-axis text"

    @patch("h5forest.h5_forest.H5Forest")
    def test_select_y_with_group(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test selecting y-axis with a group node (should fail)."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Create a group node
        node = MagicMock()
        node.is_group = True
        node.path = "/another/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify error message was printed
        mock_app.print.assert_called_once_with(
            "/another/group is not a Dataset"
        )

        # Verify set_y_key was NOT called
        mock_app.scatter_plotter.set_y_key.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_edit_plot_entry_toggle_linear_to_log(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling scale from linear to log."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set up plot content with linear scale
        mock_app.plot_content.text = "x-scale:     linear\ny-scale:     log"
        mock_app.plot_content.document.cursor_position_row = 0
        mock_app.plot_content.document.cursor_position = 10
        mock_app.scatter_plotter.get_row = MagicMock(
            return_value="x-scale: linear"
        )

        # Find the edit_plot_entry handler (enter key = c-m)
        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify text was toggled to log
        assert "log" in mock_app.plot_content.text
        assert mock_app.scatter_plotter.plot_text == mock_app.plot_content.text
        mock_app.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_edit_plot_entry_toggle_log_to_linear(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling scale from log to linear."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set up plot content with log scale
        mock_app.plot_content.text = "x-scale:     log\ny-scale:     linear"
        mock_app.plot_content.document.cursor_position_row = 0
        mock_app.plot_content.document.cursor_position = 10
        mock_app.scatter_plotter.get_row = MagicMock(
            return_value="x-scale: log"
        )

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify text was toggled to linear
        assert "linear" in mock_app.plot_content.text
        mock_app.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_edit_plot_entry_callback(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test editing a non-scale parameter with callback."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set up plot content with non-scale parameter
        mock_app.plot_content.text = (
            "title:       My Plot\nx-scale:     linear"
        )
        mock_app.plot_content.document.cursor_position_row = 0
        mock_app.plot_content.document.cursor_position = 10
        mock_app.scatter_plotter.get_row = MagicMock(
            return_value="title: My Plot"
        )

        bindings = [b for b in mock_app.kb.bindings if "c-m" in str(b.keys)]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify input was called with callback
        mock_app.input.assert_called_once()
        call_args = mock_app.input.call_args[0]
        assert call_args[0] == "title"
        assert callable(call_args[1])

        # Simulate the callback being called
        mock_app.user_input = "New Title"
        callback = call_args[1]
        callback()

        # Verify text was updated
        assert "New Title" in mock_app.plot_content.text
        mock_app.shift_focus.assert_called_once_with(mock_app.plot_content)

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.plot_funcs.prompt_for_chunking_preference")
    def test_plot_scatter(
        self, mock_prompt, mock_h5forest_class, mock_app, mock_event
    ):
        """Test plotting and showing scatter plot."""
        mock_h5forest_class.return_value = mock_app
        # Make the prompt call the callback immediately
        mock_prompt.side_effect = lambda app, nodes, callback: callback(
            use_chunks=False
        )

        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify plot_and_show was called with use_chunks parameter
        mock_app.scatter_plotter.plot_and_show.assert_called_once_with(
            mock_app.plot_content.text, use_chunks=False
        )

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.plot_funcs.prompt_for_chunking_preference")
    def test_save_scatter(
        self, mock_prompt, mock_h5forest_class, mock_app, mock_event
    ):
        """Test saving scatter plot."""
        mock_h5forest_class.return_value = mock_app
        # Make the prompt call the callback immediately
        mock_prompt.side_effect = lambda app, nodes, callback: callback(
            use_chunks=False
        )

        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("P",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify plot_and_save was called with use_chunks parameter
        mock_app.scatter_plotter.plot_and_save.assert_called_once_with(
            mock_app.plot_content.text, use_chunks=False
        )

    @patch("h5forest.h5_forest.H5Forest")
    def test_plot_scatter_missing_x_axis(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test plotting without x-axis selected."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set plot_params with only y
        mock_app.scatter_plotter.plot_params = {"y": "some_data"}

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Should print error message
        expected_msg = (
            "Please select both x-axis (x) and y-axis (y) datasets first"
        )
        mock_app.print.assert_called_once_with(expected_msg)
        # Should not call plot_and_show
        mock_app.scatter_plotter.plot_and_show.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_plot_scatter_missing_y_axis(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test plotting without y-axis selected."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set plot_params with only x
        mock_app.scatter_plotter.plot_params = {"x": "some_data"}

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Should print error message
        expected_msg = (
            "Please select both x-axis (x) and y-axis (y) datasets first"
        )
        mock_app.print.assert_called_once_with(expected_msg)
        # Should not call plot_and_show
        mock_app.scatter_plotter.plot_and_show.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_plot_scatter_missing_both_axes(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test plotting without any axes selected."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set plot_params empty
        mock_app.scatter_plotter.plot_params = {}

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Should print error message
        expected_msg = (
            "Please select both x-axis (x) and y-axis (y) datasets first"
        )
        mock_app.print.assert_called_once_with(expected_msg)
        # Should not call plot_and_show
        mock_app.scatter_plotter.plot_and_show.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_save_scatter_missing_x_axis(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test saving without x-axis selected."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set plot_params with only y
        mock_app.scatter_plotter.plot_params = {"y": "some_data"}

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("P",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Should print error message
        expected_msg = (
            "Please select both x-axis (x) and y-axis (y) datasets first"
        )
        mock_app.print.assert_called_once_with(expected_msg)
        # Should not call plot_and_save
        mock_app.scatter_plotter.plot_and_save.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_save_scatter_missing_y_axis(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test saving without y-axis selected."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set plot_params with only x
        mock_app.scatter_plotter.plot_params = {"x": "some_data"}

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("P",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Should print error message
        expected_msg = (
            "Please select both x-axis (x) and y-axis (y) datasets first"
        )
        mock_app.print.assert_called_once_with(expected_msg)
        # Should not call plot_and_save
        mock_app.scatter_plotter.plot_and_save.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.bindings.plot_funcs.WaitIndicator")
    @patch("h5forest.bindings.plot_funcs.prompt_for_chunking_preference")
    def test_plot_scatter_calls_default_focus(
        self,
        mock_prompt,
        mock_wait_indicator,
        mock_h5forest_class,
        mock_app,
        mock_event,
    ):
        """Test that plot_scatter calls default_focus after plotting."""
        mock_h5forest_class.return_value = mock_app
        # Mock WaitIndicator context manager
        mock_wait_indicator.return_value.__enter__ = MagicMock()
        mock_wait_indicator.return_value.__exit__ = MagicMock()

        # Make the prompt call the callback immediately
        mock_prompt.side_effect = lambda app, nodes, callback: callback(
            use_chunks=False
        )

        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("p",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify default_focus was called
        mock_app.default_focus.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_reset(self, mock_h5forest_class, mock_app, mock_event):
        """Test resetting plot content."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("r",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify reset was called
        mock_app.scatter_plotter.reset.assert_called_once()

        # Verify plot content was updated
        assert mock_app.plot_content.text == "reset text"

        # Verify UI was updated
        mock_app.app.invalidate.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_edit_plot(self, mock_h5forest_class, mock_app, mock_event):
        """Test entering edit plot mode."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("e",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify focus shifted to plot content
        mock_app.shift_focus.assert_called_once_with(mock_app.plot_content)

    @patch("h5forest.h5_forest.H5Forest")
    def test_exit_edit_plot(self, mock_h5forest_class, mock_app, mock_event):
        """Test exiting edit plot mode."""
        mock_h5forest_class.return_value = mock_app
        mock_app.app.layout.has_focus = MagicMock(return_value=True)

        _init_plot_bindings(mock_app)

        # Find the 'e' binding for exiting edit mode (edit_config
        # key exits when in config)
        bindings = [b for b in mock_app.kb.bindings if b.keys == ("e",)]
        # Should have an e binding with has_focus filter
        assert len(bindings) > 0

        # Get the exit_edit_plot handler (bound when plot config has focus)
        # There are two 'e' bindings: one for entering, one for exiting
        handler = (
            bindings[-1].handler if len(bindings) > 1 else bindings[0].handler
        )
        handler(mock_event)

        # Verify focus shifted back to tree
        mock_app.shift_focus.assert_called_with(mock_app.tree_content)

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_linear_to_log(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale from linear to log."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Find the X binding (capital X for toggle)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify x-scale was toggled to log
        assert "log" in mock_app.plot_content.text
        mock_app.app.invalidate.assert_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_log_to_linear(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale from log to linear."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set initial state to log
        mock_app.plot_content.text = (
            "x-axis:      <key>\n"
            "y-axis:      <key>\n"
            "x-label:     <label>\n"
            "y-label:     <label>\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify x-scale was toggled back to linear
        assert "x-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_linear_to_log(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale from linear to log."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Find the Y binding (capital Y for toggle)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        assert len(bindings) > 0

        handler = bindings[0].handler
        handler(mock_event)

        # Verify y-scale was toggled to log
        assert "y-scale:     log" in mock_app.plot_content.text
        mock_app.app.invalidate.assert_called()

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_log_to_linear(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale from log to linear."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        # Set initial state to log
        mock_app.plot_content.text = (
            "x-axis:      <key>\n"
            "y-axis:      <key>\n"
            "x-label:     <label>\n"
            "y-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     log\n"
            "marker:      .\n"
        )

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify y-scale was toggled back to linear
        assert "y-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_with_none_x_min(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale when x_min is None."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.x_min = None
        mock_app.scatter_plotter.x_max = None
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "x-axis data range not yet computed" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_to_log_with_zero_values(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale to log when x_min is 0."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.x_min = 0
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "zero" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_to_log_with_negative_values(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale to log when x_min is negative."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.x_min = -5.0
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "negative" in error_msg
        # Verify scale was NOT changed
        assert "x-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_with_none_y_min(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale when y_min is None."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.y_min = None
        mock_app.scatter_plotter.y_max = None
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "y-axis data range not yet computed" in error_msg
        # Verify scale was NOT changed
        assert "y-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_to_log_with_zero_values(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale to log when y_min is 0."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.y_min = 0
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "zero" in error_msg
        # Verify scale was NOT changed
        assert "y-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_to_log_with_negative_values(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale to log when y_min is negative."""
        mock_h5forest_class.return_value = mock_app
        mock_app.scatter_plotter.y_min = -5.0
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify error message was printed
        mock_app.print.assert_called_once()
        error_msg = mock_app.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "negative" in error_msg
        # Verify scale was NOT changed
        assert "y-scale:     linear" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_x_scale_with_running_thread(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling x scale with a running assignx_thread."""
        mock_h5forest_class.return_value = mock_app

        # Create a mock thread
        mock_thread = MagicMock()
        mock_app.scatter_plotter.assignx_thread = mock_thread
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("X",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify thread was joined
        mock_thread.join.assert_called_once()
        # Verify scale was toggled
        assert "x-scale:     log" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_toggle_y_scale_with_running_thread(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test toggling y scale with a running assigny_thread."""
        mock_h5forest_class.return_value = mock_app

        # Create a mock thread
        mock_thread = MagicMock()
        mock_app.scatter_plotter.assigny_thread = mock_thread
        _init_plot_bindings(mock_app)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("Y",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Verify thread was joined
        mock_thread.join.assert_called_once()
        # Verify scale was toggled
        assert "y-scale:     log" in mock_app.plot_content.text

    @patch("h5forest.h5_forest.H5Forest")
    def test_reset_closes_figure(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test that reset closes any open figures."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("r",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)

        # Verify close was called
        mock_app.scatter_plotter.close.assert_called_once()
        mock_app.scatter_plotter.reset.assert_called_once()

    @patch("h5forest.h5_forest.H5Forest")
    def test_all_keys_bound(self, mock_h5forest_class, mock_app):
        """Test that all expected keys are bound."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)

        expected_keys = [
            "x",
            "y",
            "X",
            "Y",
            "c-m",
            "p",
            "P",
            "r",
            "e",
            "q",
        ]

        for key in expected_keys:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"

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
    def test_hotkeys_structure(self, mock_h5forest_class, mock_app):
        """Test that hotkeys dict has correct structure."""
        mock_h5forest_class.return_value = mock_app
        hot_keys = _init_plot_bindings(mock_app)

        # Should be a dict with Label values

        assert len(hot_keys) == 12

        # All values should be Labels
        for key, value in hot_keys.items():
            assert isinstance(key, str)
            assert isinstance(value, Label)

    @patch("h5forest.h5_forest.H5Forest")
    def test_jump_to_config_when_in_tree(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test jumping to config from tree."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)
        # Focus is not on plot_content (i.e., we're in tree)
        mock_app.app.layout.has_focus = MagicMock(return_value=False)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("e",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Should jump to plot_content
        mock_app.shift_focus.assert_called_once_with(mock_app.plot_content)

    @patch("h5forest.h5_forest.H5Forest")
    def test_jump_to_config_when_already_in_config(
        self, mock_h5forest_class, mock_app, mock_event
    ):
        """Test jumping from config back to tree."""
        mock_h5forest_class.return_value = mock_app
        _init_plot_bindings(mock_app)
        # Set focus to be on plot_content
        mock_app.app.layout.has_focus = MagicMock(
            side_effect=lambda content: content == mock_app.plot_content
        )
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("e",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        # Should jump back to tree when already in config
        mock_app.shift_focus.assert_called_once_with(mock_app.tree_content)
