"""Tests for dataset mode keybindings."""

from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Label

from h5forest.bindings.dataset_bindings import _init_dataset_bindings


class TestDatasetBindings:
    """Test cases for dataset mode keybindings."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock H5Forest application for testing."""
        app = MagicMock()
        app.flag_dataset_mode = True
        app.tree = MagicMock()
        app.current_row = 0
        app.value_title = MagicMock()
        app.value_title.update_title = MagicMock()
        app.values_content = MagicMock()
        app.values_content.text = ""
        app.flag_values_visible = False
        app.return_to_normal_mode = MagicMock()
        app.default_focus = MagicMock()
        app.print = MagicMock()
        app.input = MagicMock()
        app.user_input = ""
        app.kb = KeyBindings()
        app.app = MagicMock()
        app.app.loop = MagicMock()
        return app

    @pytest.fixture
    def mock_event(self):
        """Create a mock event for testing."""
        return MagicMock()

    def test_init_dataset_bindings_returns_hotkeys(self, mock_app):
        """Test that _init_dataset_bindings returns a list of Labels."""

        hot_keys = _init_dataset_bindings(mock_app)
        assert isinstance(hot_keys, list)
        assert len(hot_keys) == 7
        for item in hot_keys:
            assert isinstance(item, Label)

    def test_show_values(self, mock_app, mock_event):
        """Test showing dataset values."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_value_text = MagicMock(return_value="value text")
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("v",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert mock_app.values_content.text == "value text"
        assert mock_app.flag_values_visible is True
        mock_app.value_title.update_title.assert_called_once()

    def test_show_values_with_group(self, mock_app, mock_event):
        """Test showing values with group node (should fail)."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("v",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    def test_show_values_empty_text(self, mock_app, mock_event):
        """Test showing values when text is empty."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.get_value_text = MagicMock(return_value="")
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("v",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert mock_app.flag_values_visible is False

    def test_show_values_in_range(self, mock_app, mock_event):
        """Test showing values in a range."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_value_text = MagicMock(return_value="range values")
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("V",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.input.assert_called_once()
        callback = mock_app.input.call_args[0][1]
        mock_app.user_input = "10 - 20"
        callback()
        node.get_value_text.assert_called_once_with(
            start_index=10, end_index=20
        )
        assert mock_app.values_content.text == "range values"

    def test_show_values_in_range_invalid_input(self, mock_app, mock_event):
        """Test showing values in range with invalid input."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("V",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        callback = mock_app.input.call_args[0][1]
        mock_app.user_input = "invalid"
        callback()
        mock_app.print.assert_called_once()
        mock_app.default_focus.assert_called_once()

    def test_show_values_in_range_with_group(self, mock_app, mock_event):
        """Test showing values in range with group node (should fail)."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("V",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")
        mock_app.input.assert_not_called()

    def test_show_values_in_range_empty_text(self, mock_app, mock_event):
        """Test showing values in range when text is empty."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_value_text = MagicMock(return_value="")
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("V",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        callback = mock_app.input.call_args[0][1]
        mock_app.user_input = "10 - 20"
        callback()
        node.get_value_text.assert_called_once_with(
            start_index=10, end_index=20
        )
        # Should return early without setting flag_values_visible
        assert mock_app.flag_values_visible is False

    def test_close_values(self, mock_app, mock_event):
        """Test closing value pane."""
        _init_dataset_bindings(mock_app)
        mock_app.flag_values_visible = True
        mock_app.values_content.text = "some values"
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("c",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        assert mock_app.flag_values_visible is False
        assert mock_app.values_content.text == ""
        mock_app.return_to_normal_mode.assert_called_once()

    @patch("threading.Thread")
    def test_minimum_maximum(self, mock_thread, mock_app, mock_event):
        """Test getting minimum and maximum values."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_min_max = MagicMock(return_value=(0, 100))
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("m",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]["daemon"] is True
        # Call the thread function to test it
        thread_func = mock_thread.call_args[1]["target"]
        thread_func()
        mock_app.app.loop.call_soon_threadsafe.assert_called_once()

    def test_minimum_maximum_with_group(self, mock_app, mock_event):
        """Test min/max with group node (should fail)."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("m",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    @patch("threading.Thread")
    def test_mean(self, mock_thread, mock_app, mock_event):
        """Test getting mean value."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_mean = MagicMock(return_value=50.0)
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("M",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_thread.assert_called_once()
        # Call the thread function
        thread_func = mock_thread.call_args[1]["target"]
        thread_func()
        mock_app.app.loop.call_soon_threadsafe.assert_called_once()

    def test_mean_with_group(self, mock_app, mock_event):
        """Test mean with group node (should fail)."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("M",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    @patch("threading.Thread")
    def test_std(self, mock_thread, mock_app, mock_event):
        """Test getting standard deviation."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = False
        node.path = "/dataset"
        node.get_std = MagicMock(return_value=15.0)
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("s",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_thread.assert_called_once()
        # Call the thread function
        thread_func = mock_thread.call_args[1]["target"]
        thread_func()
        mock_app.app.loop.call_soon_threadsafe.assert_called_once()

    def test_std_with_group(self, mock_app, mock_event):
        """Test std with group node (should fail)."""
        _init_dataset_bindings(mock_app)
        node = MagicMock()
        node.is_group = True
        node.path = "/group"
        mock_app.tree.get_current_node = MagicMock(return_value=node)
        bindings = [
            b
            for b in mock_app.kb.bindings
            if b.keys == ("s",) and b.filter is not None
        ]
        handler = bindings[0].handler
        handler(mock_event)
        mock_app.print.assert_called_once_with("/group is not a Dataset")

    def test_all_keys_bound(self, mock_app):
        """Test that all expected keys are bound."""
        _init_dataset_bindings(mock_app)
        for key in ["v", "V", "c", "m", "M", "s"]:
            bindings = [b for b in mock_app.kb.bindings if key in str(b.keys)]
            assert len(bindings) > 0, f"Key '{key}' not bound"
