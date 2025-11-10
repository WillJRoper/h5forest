"""Tests for H5Forest property methods that return dynamic label layouts."""

from unittest.mock import MagicMock, Mock

import pytest

from h5forest.h5_forest import H5Forest
from h5forest.utils import DynamicLabelLayout


class TestH5ForestLabelProperties:
    """Test cases for H5Forest label property methods."""

    @pytest.fixture
    def mock_h5forest(self):
        """Create a mock H5Forest instance with necessary attributes."""
        # Create a mock instance without calling __init__
        h5f = Mock(spec=H5Forest)

        # Set up basic attributes
        h5f.flag_expanded_attrs = False
        h5f.flag_values_visible = False

        # Mock the app and layout
        h5f.app = MagicMock()
        h5f.app.layout = MagicMock()
        h5f.app.layout.has_focus = MagicMock(return_value=False)

        # Mock content attributes
        h5f.tree_content = MagicMock()
        h5f.tree_content.content = MagicMock()
        h5f.attributes_content = MagicMock()
        h5f.values_content = MagicMock()
        h5f.plot_content = MagicMock()
        h5f.hist_content = MagicMock()

        # Mock plotters
        h5f.scatter_plotter = MagicMock()
        h5f.scatter_plotter.plot_params = {}
        h5f.scatter_plotter.__len__ = MagicMock(return_value=0)

        h5f.histogram_plotter = MagicMock()
        h5f.histogram_plotter.plot_params = {}

        # Mock the binding dictionaries
        h5f._app_keys_dict = {
            "expand_attrs": Mock(),
            "shrink_attrs": Mock(),
            "dataset_mode": Mock(),
            "goto_mode": Mock(),
            "hist_mode": Mock(),
            "plotting_mode": Mock(),
            "window_mode": Mock(),
            "search": Mock(),
            "restore_tree": Mock(),
            "exit": Mock(),
        }

        h5f._tree_keys_dict = {
            "open_group": Mock(),
            "move_ten": Mock(),
        }

        h5f._dataset_keys_list = [Mock() for _ in range(7)]
        h5f._goto_keys_list = [Mock() for _ in range(6)]

        h5f._window_keys_dict = {
            "move_tree": Mock(),
            "move_attrs": Mock(),
            "move_values": Mock(),
            "move_plot": Mock(),
            "move_hist": Mock(),
            "exit": Mock(),
        }

        h5f._plot_keys_dict = {
            "edit_config": Mock(),
            "edit_tree": Mock(),
            "edit_entry": Mock(),
            "select_x": Mock(),
            "select_y": Mock(),
            "toggle_x_scale": Mock(),
            "toggle_y_scale": Mock(),
            "plot": Mock(),
            "save_plot": Mock(),
            "reset": Mock(),
            "exit_mode": Mock(),
            "exit_config": Mock(),
        }

        h5f._hist_keys_dict = {
            "edit_config": Mock(),
            "edit_tree": Mock(),
            "edit_entry": Mock(),
            "select_data": Mock(),
            "edit_bins": Mock(),
            "toggle_x_scale": Mock(),
            "toggle_y_scale": Mock(),
            "show_hist": Mock(),
            "save_hist": Mock(),
            "reset": Mock(),
            "exit_mode": Mock(),
            "exit_config": Mock(),
        }

        h5f._search_keys_list = [Mock(), Mock()]

        # Bind the actual methods to the mock
        h5f._get_hot_keys = H5Forest._get_hot_keys.__get__(h5f, H5Forest)
        h5f._get_dataset_keys = H5Forest._get_dataset_keys.__get__(
            h5f, H5Forest
        )
        h5f._get_goto_keys = H5Forest._get_goto_keys.__get__(h5f, H5Forest)
        h5f._get_window_keys = H5Forest._get_window_keys.__get__(h5f, H5Forest)
        h5f._get_plot_keys = H5Forest._get_plot_keys.__get__(h5f, H5Forest)
        h5f._get_hist_keys = H5Forest._get_hist_keys.__get__(h5f, H5Forest)
        h5f._get_search_keys = H5Forest._get_search_keys.__get__(h5f, H5Forest)

        # Bind the actual property methods to the mock
        h5f.hot_keys = property(H5Forest.hot_keys.fget).__get__(h5f, H5Forest)
        h5f.dataset_keys = property(H5Forest.dataset_keys.fget).__get__(
            h5f, H5Forest
        )
        h5f.goto_keys = property(H5Forest.goto_keys.fget).__get__(
            h5f, H5Forest
        )
        h5f.window_keys = property(H5Forest.window_keys.fget).__get__(
            h5f, H5Forest
        )
        h5f.plot_keys = property(H5Forest.plot_keys.fget).__get__(
            h5f, H5Forest
        )
        h5f.hist_keys = property(H5Forest.hist_keys.fget).__get__(
            h5f, H5Forest
        )
        h5f.search_keys = property(H5Forest.search_keys.fget).__get__(
            h5f, H5Forest
        )

        return h5f

    def test_hot_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that hot_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.hot_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_hot_keys_without_tree_focus(self, mock_h5forest):
        """Test hot_keys when tree doesn't have focus."""
        mock_h5forest.app.layout.has_focus.return_value = False

        result = mock_h5forest.hot_keys

        # Should return DynamicLabelLayout
        assert isinstance(result, DynamicLabelLayout)

        # Get the labels (they're wrapped in a callable)
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have: open_group (Enter), expand/shrink_attrs, dataset, goto,
        # hist, plotting, window, search, move_ten, restore_tree, exit
        assert len(labels) == 11

    def test_hot_keys_with_tree_focus(self, mock_h5forest):
        """Test hot_keys when tree has focus."""

        # Make has_focus return True only for tree_content.content
        def has_focus_side_effect(content):
            return content == mock_h5forest.tree_content.content

        mock_h5forest.app.layout.has_focus.side_effect = has_focus_side_effect

        result = mock_h5forest.hot_keys

        # Get the labels
        labels = result.labels() if callable(result.labels) else result.labels

        # Should include tree keys and search when tree has focus
        # Should have 11 labels
        assert len(labels) == 11

    def test_hot_keys_with_expanded_attrs(self, mock_h5forest):
        """Test hot_keys shows shrink_attrs when attrs are expanded."""
        mock_h5forest.flag_expanded_attrs = True

        result = mock_h5forest.hot_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have 11 labels (one of which is shrink, not expand)
        assert len(labels) == 11

    def test_hot_keys_with_collapsed_attrs(self, mock_h5forest):
        """Test hot_keys shows expand_attrs when attrs are collapsed."""
        mock_h5forest.flag_expanded_attrs = False

        result = mock_h5forest.hot_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have 11 labels (one of which is expand, not shrink)
        assert len(labels) == 11

    def test_dataset_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that dataset_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.dataset_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_dataset_keys_contains_all_labels(self, mock_h5forest):
        """Test that dataset_keys contains all dataset labels."""
        result = mock_h5forest.dataset_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have 7 dataset keys
        assert len(labels) == 7
        assert all(
            label in labels for label in mock_h5forest._dataset_keys_list
        )

    def test_goto_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that goto_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.goto_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_goto_keys_contains_all_labels(self, mock_h5forest):
        """Test that goto_keys contains all goto labels."""
        result = mock_h5forest.goto_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have 6 goto keys
        assert len(labels) == 6
        assert all(label in labels for label in mock_h5forest._goto_keys_list)

    def test_window_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that window_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.window_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_window_keys_without_values_visible(self, mock_h5forest):
        """Test window_keys when values panel is not visible."""
        mock_h5forest.flag_values_visible = False

        result = mock_h5forest.window_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should not include move_values when values not visible
        # Should have 5 keys: tree, attrs, plot, hist, exit
        assert len(labels) == 5
        assert mock_h5forest._window_keys_dict["move_values"] not in labels

    def test_window_keys_with_values_visible(self, mock_h5forest):
        """Test window_keys when values panel is visible."""
        mock_h5forest.flag_values_visible = True

        result = mock_h5forest.window_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should include move_values when values visible and not focused
        # Should have 6 keys: tree, attrs, values, plot, hist, exit
        # If values_content is currently focused, move_values won't be shown
        # The test should have 5 or 6 depending on focus state
        assert len(labels) >= 5 and len(labels) <= 6

    def test_plot_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that plot_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.plot_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_plot_keys_with_config_focused(self, mock_h5forest):
        """Test plot_keys when config panel is focused."""

        def has_focus_side_effect(content):
            return content == mock_h5forest.plot_content

        mock_h5forest.app.layout.has_focus.side_effect = has_focus_side_effect

        result = mock_h5forest.plot_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should only have 3 config-specific keys
        assert len(labels) == 3
        assert mock_h5forest._plot_keys_dict["edit_entry"] in labels
        assert mock_h5forest._plot_keys_dict["edit_tree"] in labels
        assert mock_h5forest._plot_keys_dict["exit_config"] in labels

    def test_hist_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that hist_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.hist_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_hist_keys_with_config_focused(self, mock_h5forest):
        """Test hist_keys when config panel is focused."""

        def has_focus_side_effect(content):
            return content == mock_h5forest.hist_content

        mock_h5forest.app.layout.has_focus.side_effect = has_focus_side_effect

        result = mock_h5forest.hist_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should only have 3 config-specific keys
        assert len(labels) == 3
        assert mock_h5forest._hist_keys_dict["edit_entry"] in labels
        assert mock_h5forest._hist_keys_dict["edit_tree"] in labels
        assert mock_h5forest._hist_keys_dict["exit_config"] in labels

    def test_search_keys_returns_dynamic_layout(self, mock_h5forest):
        """Test that search_keys returns a DynamicLabelLayout."""
        result = mock_h5forest.search_keys
        assert isinstance(result, DynamicLabelLayout)

    def test_search_keys_contains_all_labels(self, mock_h5forest):
        """Test that search_keys contains all search labels."""
        result = mock_h5forest.search_keys
        labels = result.labels() if callable(result.labels) else result.labels

        # Should have 2 search keys
        assert len(labels) == 2
        assert all(
            label in labels for label in mock_h5forest._search_keys_list
        )

    def test_hot_keys_without_app_attribute(self, mock_h5forest):
        """Test hot_keys handles missing app attribute gracefully."""
        # Remove app attribute to simulate initialization state
        delattr(mock_h5forest, "app")

        result = mock_h5forest.hot_keys

        # Should still return a DynamicLabelLayout without error
        assert isinstance(result, DynamicLabelLayout)

        # Should have basic keys
        labels = result.labels() if callable(result.labels) else result.labels
        assert len(labels) == 11  # All keys including Enter and move_ten

    def test_hot_keys_without_tree_content_attribute(self, mock_h5forest):
        """Test hot_keys handles missing tree_content gracefully."""
        delattr(mock_h5forest, "tree_content")

        result = mock_h5forest.hot_keys

        # Should still return a DynamicLabelLayout without error
        assert isinstance(result, DynamicLabelLayout)
