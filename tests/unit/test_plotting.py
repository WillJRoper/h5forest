"""Comprehensive unit tests for h5forest.plotting module."""

import tempfile
from unittest.mock import Mock, patch

import h5py
import numpy as np
import pytest

from h5forest.plotting import HistogramPlotter, Plotter, ScatterPlotter


class TestPlotter:
    """Test the base Plotter class."""

    def test_plotter_init(self):
        """Test Plotter initialization."""
        plotter = Plotter()
        assert plotter.plot_params == {}
        assert plotter.fig is None
        assert plotter.ax is None

    def test_get_row(self):
        """Test get_row method."""
        plotter = Plotter()
        plotter.plot_text = "line1\nline2\nline3"

        assert plotter.get_row(0) == "line1"
        assert plotter.get_row(1) == "line2"
        assert plotter.get_row(2) == "line3"

    @patch("h5forest.h5_forest.H5Forest")
    def test_get_row_with_error(self, mock_forest_class):
        """Test get_row with invalid row index."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = Plotter()
        plotter.plot_text = "line1\nline2"

        # Should raise IndexError but error_handler will catch it
        result = plotter.get_row(10)
        assert result is None  # error_handler returns None on error
        mock_forest.print.assert_called_once()  # Error should be printed

    def test_len(self):
        """Test __len__ method."""
        plotter = Plotter()
        assert len(plotter) == 0

        plotter.plot_params = {"x": "data1", "y": "data2"}
        assert len(plotter) == 2

    @patch("h5forest.plotting.plt.show")
    def test_show(self, mock_show):
        """Test show method."""
        plotter = Plotter()
        plotter.show()
        mock_show.assert_called_once()

    @patch("h5forest.plotting.plt.close")
    def test_close_with_figure(self, mock_close):
        """Test close method with existing figure."""
        plotter = Plotter()
        fig_mock = Mock()
        plotter.fig = fig_mock
        plotter.ax = Mock()

        plotter.close()

        mock_close.assert_called_once_with(fig_mock)
        assert plotter.fig is None
        assert plotter.ax is None

    @patch("h5forest.plotting.plt.close")
    def test_close_without_figure(self, mock_close):
        """Test close method when no figure exists."""
        plotter = Plotter()
        plotter.fig = None
        plotter.ax = None

        plotter.close()

        # close should not be called if fig is None
        mock_close.assert_not_called()
        assert plotter.fig is None
        assert plotter.ax is None

    @patch("h5forest.plotting.Path.cwd")
    @patch("h5forest.h5_forest.H5Forest")
    def test_save(self, mock_forest_class, mock_cwd):
        """Test save method with file path input."""
        # Setup mocks
        mock_cwd.return_value = Mock(__str__=Mock(return_value="/tmp"))
        mock_forest = Mock()
        mock_forest.user_input = "/tmp/test.png"
        mock_forest_class.return_value = mock_forest

        plotter = Plotter()
        plotter.fig = Mock()
        plotter.fig.savefig = Mock()

        # Call save which sets up callback
        plotter.save()

        # Verify input was called with correct arguments
        mock_forest.input.assert_called_once()
        call_args = mock_forest.input.call_args[0]
        assert "filepath" in call_args[0]
        assert callable(call_args[1])  # Second arg should be callback

        # Simulate callback execution
        callback = call_args[1]
        callback()

        # Verify save was called
        plotter.fig.savefig.assert_called_once_with(
            "/tmp/test.png", dpi=100, bbox_inches="tight"
        )
        mock_forest.print.assert_called_with("Plot saved!")
        mock_forest.default_focus.assert_called_once()
        mock_forest.return_to_normal_mode.assert_called_once()

    @patch("h5forest.plotting.plt.show")
    def test_plot_and_show(self, mock_show):
        """Test plot_and_show method."""
        plotter = Plotter()
        plotter._plot = Mock()

        text = "test plot text"
        plotter.plot_and_show(text)

        plotter._plot.assert_called_once_with(text)
        mock_show.assert_called_once()

    @patch("h5forest.plotting.Path.cwd")
    @patch("h5forest.h5_forest.H5Forest")
    def test_plot_and_save(self, mock_forest_class, mock_cwd):
        """Test plot_and_save method."""
        mock_cwd.return_value = Mock(__str__=Mock(return_value="/tmp"))
        mock_forest = Mock()
        mock_forest.user_input = "/tmp/test.png"
        mock_forest_class.return_value = mock_forest

        plotter = Plotter()
        plotter._plot = Mock()
        plotter.fig = Mock()
        plotter.fig.savefig = Mock()

        text = "test plot text"
        plotter.plot_and_save(text)

        plotter._plot.assert_called_once_with(text)
        mock_forest.input.assert_called_once()


class TestScatterPlotter:
    """Test the ScatterPlotter class."""

    def test_scatter_plotter_init(self):
        """Test ScatterPlotter initialization."""
        plotter = ScatterPlotter()

        assert plotter.plot_params == {}
        assert plotter.fig is None
        assert plotter.ax is None
        assert "x-axis:" in plotter.default_plot_text
        assert "y-axis:" in plotter.default_plot_text
        assert plotter.plot_text == plotter.default_plot_text
        assert plotter.x_min is None
        assert plotter.x_max is None
        assert plotter.y_min is None
        assert plotter.y_max is None
        assert plotter.x_data is None
        assert plotter.y_data is None
        assert plotter.assignx_thread is None
        assert plotter.assigny_thread is None
        assert plotter.plot_thread is None

    def test_set_x_key_with_1d_dataset(self):
        """Test set_x_key with valid 1D dataset."""
        plotter = ScatterPlotter()

        # Create mock node
        node = Mock()
        node.ndim = 1
        node.shape = (100,)
        node.path = "/data/x_values"
        node.get_min_max = Mock(return_value=(0.0, 10.0))

        result = plotter.set_x_key(node)

        # Verify plot params were set
        assert plotter.plot_params["x"] == node

        # Verify plot text was updated
        assert "/data/x_values" in result
        assert "x-axis:" in result

        # Wait for thread to complete
        if plotter.assignx_thread is not None:
            plotter.assignx_thread.join()

        # Verify min/max were set
        assert plotter.x_min == 0.0
        assert plotter.x_max == 10.0

    @patch("h5forest.h5_forest.H5Forest")
    def test_set_x_key_with_multidimensional_dataset(self, mock_forest_class):
        """Test set_x_key with >1D dataset (should fail)."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Create mock node with 2D shape
        node = Mock()
        node.ndim = 2
        node.shape = (100, 50)

        result = plotter.set_x_key(node)

        # Verify error message was printed
        mock_forest.print.assert_called_once_with("Dataset must be 1D!")

        # Verify plot params were NOT set
        assert "x" not in plotter.plot_params

        # Should return existing plot text
        assert result == plotter.plot_text

    @patch("h5forest.h5_forest.H5Forest")
    def test_set_x_key_with_incompatible_shape(self, mock_forest_class):
        """Test set_x_key with incompatible shape to existing data."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Add existing data with different shape
        existing_node = Mock()
        existing_node.shape = (50,)
        plotter.plot_params["y"] = existing_node

        # Create mock node with incompatible shape
        node = Mock()
        node.ndim = 1
        node.shape = (100,)

        plotter.set_x_key(node)

        # Verify error message was printed
        mock_forest.print.assert_called_once_with(
            "Datasets must have the same shape!"
        )

        # Verify plot params were NOT updated with x
        assert "x" not in plotter.plot_params

    def test_set_y_key_with_1d_dataset(self):
        """Test set_y_key with valid 1D dataset."""
        plotter = ScatterPlotter()

        # Create mock node
        node = Mock()
        node.ndim = 1
        node.shape = (100,)
        node.path = "/data/y_values"
        node.get_min_max = Mock(return_value=(5.0, 15.0))

        result = plotter.set_y_key(node)

        # Verify plot params were set
        assert plotter.plot_params["y"] == node

        # Verify plot text was updated
        assert "/data/y_values" in result
        assert "y-axis:" in result

        # Wait for thread to complete
        if plotter.assigny_thread is not None:
            plotter.assigny_thread.join()

        # Verify min/max were set
        assert plotter.y_min == 5.0
        assert plotter.y_max == 15.0

    @patch("h5forest.h5_forest.H5Forest")
    def test_set_y_key_with_multidimensional_dataset(self, mock_forest_class):
        """Test set_y_key with >1D dataset (should fail)."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Create mock node with 2D shape
        node = Mock()
        node.ndim = 2
        node.shape = (100, 50)

        plotter.set_y_key(node)

        # Verify error message was printed
        mock_forest.print.assert_called_once_with("Dataset must be 1D!")

        # Verify plot params were NOT set
        assert "y" not in plotter.plot_params

    @patch("h5forest.h5_forest.H5Forest")
    def test_set_y_key_with_incompatible_shape(self, mock_forest_class):
        """Test set_y_key with incompatible shape to existing data."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Add existing data with different shape
        existing_node = Mock()
        existing_node.shape = (50,)
        plotter.plot_params["x"] = existing_node

        # Create mock node with incompatible shape
        node = Mock()
        node.ndim = 1
        node.shape = (100,)

        plotter.set_y_key(node)

        # Verify error message was printed
        mock_forest.print.assert_called_once_with(
            "Datasets must have the same shape!"
        )

    def test_reset(self):
        """Test reset method."""
        plotter = ScatterPlotter()

        # Set some state
        plotter.plot_params = {"x": "data1", "y": "data2"}
        plotter.plot_text = "modified text"
        plotter.count_density = [1, 2, 3]
        plotter.sum_density = [4, 5, 6]
        plotter.mean_density = [7, 8, 9]
        plotter.xs = [1, 2, 3]
        plotter.ys = [4, 5, 6]

        result = plotter.reset()

        # Verify everything was reset
        assert result == plotter.default_plot_text
        assert plotter.plot_text == plotter.default_plot_text
        assert plotter.count_density is None
        assert plotter.sum_density is None
        assert plotter.mean_density is None
        assert plotter.xs is None
        assert plotter.ys is None
        assert plotter.plot_params == {}

    @patch("h5forest.plotting.plt.figure")
    @patch("h5forest.plotting.h5py.File")
    def test_plot_non_chunked_data(self, mock_h5py_file, mock_figure):
        """Test _plot with non-chunked data."""
        # Setup plot parameters
        plotter = ScatterPlotter()

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        x_node.filepath = "/tmp/test.h5"
        x_node.path = "/x_data"

        y_node = Mock()
        y_node.chunks = (1,)
        y_node.filepath = "/tmp/test.h5"
        y_node.path = "/y_data"

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Set min/max values (normally computed in set_x_key/set_y_key)
        plotter.x_min = 1.0
        plotter.x_max = 5.0
        plotter.y_min = 2.0
        plotter.y_max = 10.0

        # Setup mock HDF5 file
        mock_hdf = Mock()
        x_data = np.array([1, 2, 3, 4, 5])
        y_data = np.array([2, 4, 6, 8, 10])
        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            side_effect=lambda key: {
                "/x_data": Mock(__getitem__=Mock(return_value=x_data)),
                "/y_data": Mock(__getitem__=Mock(return_value=y_data)),
            }[key]
        )
        mock_h5py_file.return_value = mock_hdf

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      o\n"
        )

        plotter._plot(text)

        # Verify figure was created
        mock_figure.assert_called_once_with(figsize=(3.5, 3.5))

        # Verify subplot was added
        mock_fig.add_subplot.assert_called_once_with(111)

        # Verify grid was enabled
        mock_ax.grid.assert_called_once_with(True)
        mock_ax.set_axisbelow.assert_called_once_with(True)

        # Verify scatter was called
        mock_ax.scatter.assert_called_once()

        # Verify labels and scales were set
        mock_ax.set_xlabel.assert_called_once_with("X Values")
        mock_ax.set_ylabel.assert_called_once_with("Y Values")
        mock_ax.set_xscale.assert_called_once_with("linear")
        mock_ax.set_yscale.assert_called_once_with("linear")

    @patch("h5forest.plotting.plt.figure")
    @patch("h5forest.plotting.h5py.File")
    @patch("h5forest.plotting.ProgressBar")
    def test_plot_chunked_data(
        self, mock_progress_bar, mock_h5py_file, mock_figure
    ):
        """Test _plot with chunked data."""
        # Setup plot parameters
        plotter = ScatterPlotter()

        # Create mock nodes with matching chunks
        x_node = Mock()
        x_node.chunks = (5,)  # Chunk size of 5
        x_node.filepath = "/tmp/test.h5"
        x_node.path = "/x_data"
        x_node.shape = (10,)
        x_node.size = 10

        y_node = Mock()
        y_node.chunks = (5,)  # Same chunk size
        y_node.filepath = "/tmp/test.h5"
        y_node.path = "/y_data"
        y_node.shape = (10,)
        y_node.size = 10

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Set min/max values (normally computed in set_x_key/set_y_key)
        plotter.x_min = 1.0
        plotter.x_max = 10.0
        plotter.y_min = 10.0
        plotter.y_max = 100.0

        # Setup mock HDF5 file with chunked data
        mock_hdf = Mock()

        # Create chunked data
        chunk1_x = np.array([1, 2, 3, 4, 5])
        chunk2_x = np.array([6, 7, 8, 9, 10])
        chunk1_y = np.array([2, 4, 6, 8, 10])
        chunk2_y = np.array([12, 14, 16, 18, 20])

        x_dataset = Mock()
        y_dataset = Mock()

        # Mock __getitem__ for slicing
        def x_getitem(key):
            if key == slice(0, 5):
                return chunk1_x
            elif key == slice(5, 10):
                return chunk2_x
            return np.array([])

        def y_getitem(key):
            if key == slice(0, 5):
                return chunk1_y
            elif key == slice(5, 10):
                return chunk2_y
            return np.array([])

        x_dataset.__getitem__ = Mock(side_effect=x_getitem)
        y_dataset.__getitem__ = Mock(side_effect=y_getitem)

        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            side_effect=lambda key: {
                "/x_data": x_dataset,
                "/y_data": y_dataset,
            }[key]
        )
        mock_h5py_file.return_value = mock_hdf

        # Setup mock progress bar
        mock_pb = Mock()
        mock_pb.__enter__ = Mock(return_value=mock_pb)
        mock_pb.__exit__ = Mock(return_value=False)
        mock_progress_bar.return_value = mock_pb

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify scatter was called multiple times
        # (np.ndindex with chunks=(5,) gives 5 iterations)
        assert mock_ax.scatter.call_count == 5

    @patch("h5forest.plotting.plt.figure")
    @patch("h5forest.plotting.h5py.File")
    def test_plot_with_log_scale(self, mock_h5py_file, mock_figure):
        """Test _plot with logarithmic scale."""
        plotter = ScatterPlotter()

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        x_node.filepath = "/tmp/test.h5"
        x_node.path = "/x_data"

        y_node = Mock()
        y_node.chunks = (1,)
        y_node.filepath = "/tmp/test.h5"
        y_node.path = "/y_data"

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Set min/max values (normally computed in set_x_key/set_y_key)
        plotter.x_min = 1.0
        plotter.x_max = 1000.0
        plotter.y_min = 1.0
        plotter.y_max = 1000000.0

        # Setup mock HDF5 file
        mock_hdf = Mock()
        x_data = np.array([1, 10, 100, 1000])
        y_data = np.array([1, 100, 10000, 1000000])
        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            side_effect=lambda key: {
                "/x_data": Mock(__getitem__=Mock(return_value=x_data)),
                "/y_data": Mock(__getitem__=Mock(return_value=y_data)),
            }[key]
        )
        mock_h5py_file.return_value = mock_hdf

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log scales
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     log\n"
            "y-scale:     log\n"
            "marker:      x\n"
        )

        plotter._plot(text)

        # Verify scales were set to log
        mock_ax.set_xscale.assert_called_once_with("log")
        mock_ax.set_yscale.assert_called_once_with("log")

    @patch("h5forest.plotting.plt.figure")
    @patch("h5forest.plotting.h5py.File")
    def test_plot_with_different_markers(self, mock_h5py_file, mock_figure):
        """Test _plot with different marker styles."""
        plotter = ScatterPlotter()

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        x_node.filepath = "/tmp/test.h5"
        x_node.path = "/x_data"

        y_node = Mock()
        y_node.chunks = (1,)
        y_node.filepath = "/tmp/test.h5"
        y_node.path = "/y_data"

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Set min/max values (normally computed in set_x_key/set_y_key)
        plotter.x_min = 1.0
        plotter.x_max = 3.0
        plotter.y_min = 4.0
        plotter.y_max = 6.0

        # Setup mock HDF5 file
        mock_hdf = Mock()
        x_data = np.array([1, 2, 3])
        y_data = np.array([4, 5, 6])
        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            side_effect=lambda key: {
                "/x_data": Mock(__getitem__=Mock(return_value=x_data)),
                "/y_data": Mock(__getitem__=Mock(return_value=y_data)),
            }[key]
        )
        mock_h5py_file.return_value = mock_hdf

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with star marker
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      *\n"
        )

        plotter._plot(text)

        # Verify scatter was called with star marker
        call_kwargs = mock_ax.scatter.call_args[1]
        assert call_kwargs["marker"] == "*"


class TestScatterPlotterErrorHandling:
    """Test error handling in ScatterPlotter."""

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_negative_x_values_log_scale(
        self, mock_figure, mock_forest_class
    ):
        """Test that log scale on x-axis with negative values shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Set min/max with negative values
        plotter.x_min = -10.0
        plotter.x_max = 100.0
        plotter.y_min = 1.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log x-scale
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale on x-axis" in error_msg
        assert "negative" in error_msg

        # Verify scale was NOT set (function returned early)
        mock_ax.set_xscale.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_zero_x_values_log_scale(
        self, mock_figure, mock_forest_class
    ):
        """Test that log scale on x-axis with zero values shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Set min/max with zero
        plotter.x_min = 0.0
        plotter.x_max = 100.0
        plotter.y_min = 1.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log x-scale
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale on x-axis" in error_msg
        assert "zero" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_negative_y_values_log_scale(
        self, mock_figure, mock_forest_class
    ):
        """Test that log scale on y-axis with negative values shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Set min/max with negative y values
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.y_min = -5.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log y-scale
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     log\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale on y-axis" in error_msg
        assert "negative" in error_msg

        # Verify scale was NOT set (function returned early)
        mock_ax.set_yscale.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_none_x_values(self, mock_figure, mock_forest_class):
        """Test that None x_min/x_max shows appropriate error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Set min/max to None (not yet computed)
        plotter.x_min = None
        plotter.x_max = None
        plotter.y_min = 1.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "failed to determine x-axis data range" in error_msg
        assert "See error above for details" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_none_y_values(self, mock_figure, mock_forest_class):
        """Test that None y_min/y_max shows appropriate error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()

        # Set min/max to None (not yet computed)
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.y_min = None
        plotter.y_max = None

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)

        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text
        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "failed to determine y-axis data range" in error_msg
        assert "See error above for details" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_set_xscale_exception_handling(
        self, mock_figure, mock_forest_class
    ):
        """Test exception handling when set_xscale fails."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.y_min = 1.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)
        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure with ax that raises exception on set_xscale
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.set_xscale.side_effect = ValueError("Invalid scale")
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Error setting x-scale" in error_msg
        assert "Invalid scale" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_set_yscale_exception_handling(
        self, mock_figure, mock_forest_class
    ):
        """Test exception handling when set_yscale fails."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = ScatterPlotter()
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.y_min = 1.0
        plotter.y_max = 100.0

        # Create mock nodes
        x_node = Mock()
        x_node.chunks = (1,)
        y_node = Mock()
        y_node.chunks = (1,)
        plotter.plot_params = {"x": x_node, "y": y_node}

        # Setup mock figure with ax that raises exception on set_yscale
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.set_yscale.side_effect = ValueError("Invalid scale")
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        text = (
            "x-axis:      /x_data\n"
            "y-axis:      /y_data\n"
            "x-label:     X Values\n"
            "y-label:     Y Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Error setting y-scale" in error_msg
        assert "Invalid scale" in error_msg


class TestHistogramPlotterErrorHandling:
    """Test error handling in HistogramPlotter."""

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    def test_compute_hist_with_negative_values_log_scale(
        self, mock_h5py_file, mock_get_app, mock_forest_class
    ):
        """Test that log scale with negative data values shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = 1
        node.is_chunked = False

        plotter.plot_params = {"data": node}
        plotter.x_min = -10.0  # Negative minimum
        plotter.x_max = 100.0

        # Create compute text with log scale
        text = (
            "data:        /hist_data\n"
            "nbins:       10\n"
            "x-label:     Data\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "negative" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    def test_compute_hist_with_zero_values_log_scale(
        self, mock_h5py_file, mock_get_app, mock_forest_class
    ):
        """Test that log scale with zero data values shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = 1
        node.is_chunked = False

        plotter.plot_params = {"data": node}
        plotter.x_min = 0.0  # Zero minimum
        plotter.x_max = 100.0

        # Create compute text with log scale
        text = (
            "data:        /hist_data\n"
            "nbins:       10\n"
            "x-label:     Data\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale" in error_msg
        assert "zero" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_hist_with_zero_counts_log_yscale(
        self, mock_figure, mock_forest_class
    ):
        """Test that log y-scale with zero histogram counts shows error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = HistogramPlotter()

        # Setup histogram data with zeros
        plotter.hist = np.array([0, 1, 2, 3, 4])
        plotter.xs = np.array([1, 2, 3, 4, 5])
        plotter.widths = np.array([0.8, 0.8, 0.8, 0.8, 0.8])

        # Mock compute thread
        plotter.compute_hist_thread = Mock()
        plotter.compute_hist_thread.join = Mock()

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log y-scale
        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data Values\n"
            "x-scale:     linear\n"
            "y-scale:     log\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot use log scale on y-axis" in error_msg
        assert "zero" in error_msg

        # Verify scale was NOT set (function returned early)
        mock_ax.set_yscale.assert_not_called()

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    def test_compute_hist_with_none_values(
        self, mock_h5py_file, mock_get_app, mock_forest_class
    ):
        """Test that None x_min/x_max shows appropriate error."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = 1
        node.is_chunked = False

        plotter.plot_params = {"data": node}
        plotter.x_min = None  # Not yet computed
        plotter.x_max = None

        # Create compute text
        text = (
            "data:        /hist_data\n"
            "nbins:       10\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "failed to determine data range" in error_msg
        assert "See error above for details" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_set_xscale_exception_handling(
        self, mock_figure, mock_forest_class
    ):
        """Test exception handling when set_xscale fails in histogram."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = HistogramPlotter()
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.hist = np.array([1, 2, 3, 4, 5])
        plotter.xs = np.array([1, 2, 3, 4, 5])
        plotter.widths = np.array([1, 1, 1, 1, 1])
        # Mock thread with join method
        mock_thread = Mock()
        mock_thread.join = Mock()
        plotter.compute_hist_thread = mock_thread

        # Setup mock figure with ax that raises exception on set_xscale
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.set_xscale.side_effect = ValueError("Invalid scale")
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Error setting x-scale" in error_msg
        assert "Invalid scale" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_set_yscale_exception_handling(
        self, mock_figure, mock_forest_class
    ):
        """Test exception handling when set_yscale fails in histogram."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = HistogramPlotter()
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        plotter.hist = np.array([1, 2, 3, 4, 5])
        plotter.xs = np.array([1, 2, 3, 4, 5])
        plotter.widths = np.array([1, 1, 1, 1, 1])
        # Mock thread with join method
        mock_thread = Mock()
        mock_thread.join = Mock()
        plotter.compute_hist_thread = mock_thread

        # Setup mock figure with ax that raises exception on set_yscale
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.set_yscale.side_effect = ValueError("Invalid scale")
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Error setting y-scale" in error_msg
        assert "Invalid scale" in error_msg

    @patch("h5forest.h5_forest.H5Forest")
    @patch("h5forest.plotting.plt.figure")
    def test_plot_with_failed_histogram_computation(
        self, mock_figure, mock_forest_class
    ):
        """Test error handling when histogram computation fails."""
        mock_forest = Mock()
        mock_forest_class.return_value = mock_forest

        plotter = HistogramPlotter()
        plotter.x_min = 1.0
        plotter.x_max = 100.0
        # Explicitly set hist to None to simulate failed computation
        plotter.hist = None
        # Mock thread with join method
        mock_thread = Mock()
        mock_thread.join = Mock()
        plotter.compute_hist_thread = mock_thread

        text = (
            "data:        /hist_data\n"
            "nbins:       10\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter._plot(text)

        # Verify error was printed
        mock_forest.print.assert_called_once()
        error_msg = mock_forest.print.call_args[0][0]
        assert "Cannot plot histogram" in error_msg
        assert "histogram computation failed" in error_msg


class TestHistogramPlotter:
    """Test the HistogramPlotter class."""

    def test_histogram_plotter_init(self):
        """Test HistogramPlotter initialization."""
        plotter = HistogramPlotter()

        assert plotter.plot_params == {}
        assert plotter.fig is None
        assert plotter.ax is None
        assert "data:" in plotter.default_plot_text
        assert "nbins:" in plotter.default_plot_text
        assert plotter.plot_text == plotter.default_plot_text
        assert plotter.x_min is None
        assert plotter.x_max is None
        assert plotter.x_scale == "linear"
        assert plotter.y_scale == "linear"
        assert plotter.hist is None
        assert plotter.xs is None
        assert plotter.widths is None
        assert plotter.assign_data_thread is None
        assert plotter.compute_hist_thread is None

    def test_set_data_key(self):
        """Test set_data_key method."""
        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.path = "/histogram/data"
        node.get_min_max = Mock(return_value=(0.0, 100.0))

        result = plotter.set_data_key(node)

        # Verify plot params were set
        assert plotter.plot_params["data"] == node

        # Verify plot text was updated
        assert "/histogram/data" in result
        assert "data:" in result

        # Wait for thread to complete
        if plotter.assign_data_thread is not None:
            plotter.assign_data_thread.join()

        # Verify min/max were set
        assert plotter.x_min == 0.0
        assert plotter.x_max == 100.0

    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    def test_compute_hist_non_chunked_linear(
        self, mock_h5py_file, mock_get_app
    ):
        """Test compute_hist with non-chunked data and linear scale."""
        # Setup mock app
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = 1
        node.is_chunked = False

        plotter.plot_params = {"data": node}
        plotter.x_min = 0.0
        plotter.x_max = 10.0

        # Setup mock HDF5 file
        mock_hdf = Mock()
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            return_value=Mock(__getitem__=Mock(return_value=data))
        )
        mock_h5py_file.return_value = mock_hdf

        # Create compute text
        text = (
            "data:        /hist_data\n"
            "nbins:       10\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify histogram was computed
        assert plotter.hist is not None
        assert len(plotter.hist) == 10
        assert plotter.xs is not None
        assert len(plotter.xs) == 10
        assert plotter.widths is not None
        assert len(plotter.widths) == 10

    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    def test_compute_hist_non_chunked_log(self, mock_h5py_file, mock_get_app):
        """Test compute_hist with non-chunked data and log scale."""
        # Setup mock app
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = 1
        node.is_chunked = False

        plotter.plot_params = {"data": node}
        plotter.x_min = 1.0
        plotter.x_max = 1000.0

        # Setup mock HDF5 file
        mock_hdf = Mock()
        data = np.array([1, 10, 100, 500, 1000])
        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(
            return_value=Mock(__getitem__=Mock(return_value=data))
        )
        mock_h5py_file.return_value = mock_hdf

        # Create compute text with log scale
        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data\n"
            "x-scale:     log\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify histogram was computed with log bins
        assert plotter.hist is not None
        assert len(plotter.hist) == 5

    @patch("h5forest.plotting.get_app")
    @patch("h5forest.plotting.h5py.File")
    @patch("h5forest.plotting.ProgressBar")
    def test_compute_hist_chunked(
        self, mock_progress_bar, mock_h5py_file, mock_get_app
    ):
        """Test compute_hist with chunked data."""
        # Setup mock app
        mock_app = Mock()
        mock_get_app.return_value = mock_app

        plotter = HistogramPlotter()

        # Create mock node with chunks
        node = Mock()
        node.filepath = "/tmp/test.h5"
        node.path = "/hist_data"
        node.chunks = (5,)
        node.is_chunked = True
        node.n_chunks = (2,)
        node.shape = (10,)
        node.size = 10

        plotter.plot_params = {"data": node}
        plotter.x_min = 0.0
        plotter.x_max = 10.0

        # Setup mock HDF5 file with chunked data
        mock_hdf = Mock()

        chunk1 = np.array([1, 2, 3, 4, 5])
        chunk2 = np.array([6, 7, 8, 9, 10])

        dataset = Mock()

        def getitem(key):
            if key == (slice(0, 5),):
                result = Mock()
                result.size = 5
                result.__iter__ = Mock(return_value=iter(chunk1))
                result.__array__ = Mock(return_value=chunk1)
                return chunk1
            elif key == (slice(5, 10),):
                result = Mock()
                result.size = 5
                result.__iter__ = Mock(return_value=iter(chunk2))
                result.__array__ = Mock(return_value=chunk2)
                return chunk2
            return np.array([])

        dataset.__getitem__ = Mock(side_effect=getitem)

        mock_hdf.__enter__ = Mock(return_value=mock_hdf)
        mock_hdf.__exit__ = Mock(return_value=False)
        mock_hdf.__getitem__ = Mock(return_value=dataset)
        mock_h5py_file.return_value = mock_hdf

        # Setup mock progress bar
        mock_pb = Mock()
        mock_pb.__enter__ = Mock(return_value=mock_pb)
        mock_pb.__exit__ = Mock(return_value=False)
        mock_progress_bar.return_value = mock_pb

        # Create compute text
        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter.compute_hist(text)

        # Wait for thread to complete
        if plotter.compute_hist_thread is not None:
            plotter.compute_hist_thread.join()

        # Verify histogram was computed
        assert plotter.hist is not None
        assert len(plotter.hist) == 5

    @patch("h5forest.plotting.plt.figure")
    def test_plot_histogram(self, mock_figure):
        """Test _plot method for histogram."""
        plotter = HistogramPlotter()

        # Setup histogram data
        plotter.hist = np.array([1, 2, 3, 4, 5])
        plotter.xs = np.array([1, 2, 3, 4, 5])
        plotter.widths = np.array([0.8, 0.8, 0.8, 0.8, 0.8])

        # Mock compute thread
        plotter.compute_hist_thread = Mock()
        plotter.compute_hist_thread.join = Mock()

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text
        text = (
            "data:        /hist_data\n"
            "nbins:       5\n"
            "x-label:     Data Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        plotter._plot(text)

        # Verify figure was created
        mock_figure.assert_called_once_with(figsize=(3.5, 3.5))

        # Verify subplot was added
        mock_fig.add_subplot.assert_called_once_with(111)

        # Verify grid was enabled
        mock_ax.grid.assert_called_once_with(True)
        mock_ax.set_axisbelow.assert_called_once_with(True)

        # Verify bar was called
        mock_ax.bar.assert_called_once()

        # Verify labels and scales were set
        mock_ax.set_xlabel.assert_called_once_with("Data Values")
        mock_ax.set_ylabel.assert_called_once_with("$N$")
        mock_ax.set_xscale.assert_called_once_with("linear")
        mock_ax.set_yscale.assert_called_once_with("linear")

    @patch("h5forest.plotting.plt.figure")
    def test_plot_histogram_with_log_scale(self, mock_figure):
        """Test _plot method for histogram with log scale."""
        plotter = HistogramPlotter()

        # Setup histogram data
        plotter.hist = np.array([1, 10, 100, 1000])
        plotter.xs = np.array([1, 10, 100, 1000])
        plotter.widths = np.array([9, 90, 900, 9000])

        # Mock compute thread
        plotter.compute_hist_thread = Mock()
        plotter.compute_hist_thread.join = Mock()

        # Setup mock figure
        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_figure.return_value = mock_fig

        # Create plot text with log scales
        text = (
            "data:        /hist_data\n"
            "nbins:       4\n"
            "x-label:     Data Values\n"
            "x-scale:     log\n"
            "y-scale:     log\n"
        )

        plotter._plot(text)

        # Verify scales were set to log
        mock_ax.set_xscale.assert_called_once_with("log")
        mock_ax.set_yscale.assert_called_once_with("log")

    def test_reset_histogram(self):
        """Test reset method for histogram."""
        plotter = HistogramPlotter()

        # Set some state
        plotter.hist = np.array([1, 2, 3])
        plotter.xs = np.array([1, 2, 3])
        plotter.widths = np.array([0.8, 0.8, 0.8])
        plotter.plot_text = "modified text"
        plotter.fig = Mock()
        plotter.ax = Mock()
        plotter.plot_params = {"data": "some_data"}

        result = plotter.reset()

        # Verify everything was reset
        assert result == plotter.default_plot_text
        assert plotter.plot_text == plotter.default_plot_text
        assert plotter.hist is None
        assert plotter.xs is None
        assert plotter.widths is None
        assert plotter.fig is None
        assert plotter.ax is None
        assert plotter.plot_params == {}


class TestPlotterIntegration:
    """Integration tests with real HDF5 files."""

    @pytest.fixture
    def histogram_h5_file(self):
        """Create a temporary HDF5 file for histogram testing."""
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
            filepath = tmp.name

        # Create test file with data for histograms
        with h5py.File(filepath, "w") as f:
            f.create_dataset("data", data=np.random.randn(1000))
            f.create_dataset("x_scatter", data=np.arange(100))
            f.create_dataset("y_scatter", data=np.arange(100) * 2)

        yield filepath

        # Cleanup
        import os

        if os.path.exists(filepath):
            os.unlink(filepath)

    @patch("h5forest.progress.get_window_size")
    @patch("h5forest.plotting.plt.show")
    def test_full_scatter_plot_workflow(
        self, mock_show, mock_window_size, histogram_h5_file
    ):
        """Test complete scatter plot workflow with real HDF5 file."""

        # Mock terminal size
        mock_window_size.return_value = (24, 80)

        # Create plotter
        plotter = ScatterPlotter()

        # Create mock nodes instead of real ones to avoid ProgressBar issues
        x_node = Mock()
        x_node.ndim = 1
        x_node.shape = (100,)
        x_node.path = "/x_scatter"
        x_node.filepath = histogram_h5_file
        x_node.get_min_max = Mock(return_value=(0.0, 99.0))
        x_node.chunks = (1,)

        y_node = Mock()
        y_node.ndim = 1
        y_node.shape = (100,)
        y_node.path = "/y_scatter"
        y_node.filepath = histogram_h5_file
        y_node.get_min_max = Mock(return_value=(0.0, 198.0))
        y_node.chunks = (1,)

        # Set keys
        plotter.set_x_key(x_node)
        plotter.set_y_key(y_node)

        # Wait for threads
        if plotter.assignx_thread:
            plotter.assignx_thread.join()
        if plotter.assigny_thread:
            plotter.assigny_thread.join()

        # Create plot
        text = plotter.plot_text
        plotter.plot_and_show(text)

        # Verify plot was shown
        mock_show.assert_called_once()

        # Verify figure was created
        assert plotter.fig is not None
        assert plotter.ax is not None

    @patch("h5forest.progress.get_window_size")
    @patch("h5forest.plotting.plt.show")
    @patch("h5forest.plotting.get_app")
    def test_full_histogram_workflow(
        self, mock_get_app, mock_show, mock_window_size, histogram_h5_file
    ):
        """Test complete histogram workflow with real HDF5 file."""
        # Setup mocks
        mock_app = Mock()
        mock_get_app.return_value = mock_app
        mock_window_size.return_value = (24, 80)

        # Create plotter
        plotter = HistogramPlotter()

        # Create mock node to avoid ProgressBar issues
        node = Mock()
        node.path = "/data"
        node.filepath = histogram_h5_file
        node.get_min_max = Mock(return_value=(-3.0, 3.0))

        # Set data key
        plotter.set_data_key(node)

        # Wait for thread
        if plotter.assign_data_thread:
            plotter.assign_data_thread.join()

        # Create histogram text
        text = (
            "data:        " + node.path + "\n"
            "nbins:       20\n"
            "x-label:     Values\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        # Set up node for compute_hist
        node.chunks = 1
        node.is_chunked = False

        # Compute histogram
        plotter.compute_hist(text)

        # Wait for thread
        if plotter.compute_hist_thread:
            plotter.compute_hist_thread.join()

        # Create plot
        plotter.plot_and_show(text)

        # Verify plot was shown
        mock_show.assert_called_once()

        # Verify histogram was computed
        assert plotter.hist is not None
        assert len(plotter.hist) == 20
