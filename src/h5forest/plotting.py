"""A module for plotting with matplotlib directly from the HDF5 file.

This is only ever called from the h5forest module and is not intended to be
used directly by the user.
"""

import threading
import warnings
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from prompt_toolkit.application import get_app

from h5forest.errors import error_handler
from h5forest.progress import ProgressBar

# Supress warnings related to numpy
warnings.filterwarnings("ignore")


class Plotter:
    """
    A class to handle the plotting of data from the HDF5 file.

    This is the parent class to all other plotting classes and contains only
    the generic plotting methods.

    Attributes:
        plot_params (dict):
            A dictionary to store the plot parameters.
        default_plot_text (str):
            The default text to display in the plotting TextArea.
        plot_text (str):
            The text to display in the plotting TextArea.
    """

    def __init__(self):
        """Initialise the plotter."""
        # Container for the plot parameters
        self.plot_params = {}

        # Placeholder for the fig and ax
        self.fig = None
        self.ax = None

    @error_handler
    def get_row(self, row):
        """
        Return the current row in the plot text.

        Args:
            row (int):
                The row to return.
        """
        return self.plot_text.split("\n")[row]

    def __len__(self):
        """Return the number of plot parameters."""
        return len(self.plot_params)

    @error_handler
    def show(self):
        """Show the plot and reset everything."""
        plt.show()

    @error_handler
    def close(self):
        """Close the figure if it exists."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None

    @error_handler
    def save(self):
        """Save the plot and reset everything."""
        from h5forest.h5_forest import H5Forest

        def save_callback():
            """Get the filepath and save the plot."""
            # Strip the user input
            out_path = H5Forest().user_input.strip()

            self.fig.savefig(out_path, dpi=100, bbox_inches="tight")

            H5Forest().print("Plot saved!")
            H5Forest().default_focus()
            H5Forest().return_to_normal_mode()

        H5Forest().input(
            "Enter the filepath to save the plot: ",
            save_callback,
            mini_buffer_text=str(Path.cwd()) + "/",
        )

    @error_handler
    def plot_and_show(self, text):
        """
        Plot the data and show the plot.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Compute the plot
        self._plot(text)

        # Show the plot
        self.show()

    @error_handler
    def plot_and_save(self, text):
        """
        Plot the data and save the plot.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Compute the plot
        self._plot(text)

        # Save the plot
        self.save()


class ScatterPlotter(Plotter):
    """
    The scatter plotting class.

    Attributes:
        plot_params (dict):
            A dictionary to store the plot parameters.
        default_plot_text (str):
            The default text to display in the plotting TextArea.
        plot_text (str):
            The text to display in the plotting TextArea.
        x_min (float):
            The minimum value for the x-axis.
        x_max (float):
            The maximum value for the x-axis.
        y_min (float):
            The minimum value for the y-axis.
        y_max (float):
            The maximum value for the y-axis.
        x_data (np.ndarray):
            The x-axis data.
        y_data (np.ndarray):
            The y-axis data.
    """

    def __init__(self):
        """Initialise the scatter plotter."""
        # Call the parent class
        super().__init__()

        # Define the default text for the plotting TextArea
        self.default_plot_text = (
            "x-axis:      <key>\n"
            "y-axis:      <key>\n"
            "x-label:     <label>\n"
            "y-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
            "marker:      .\n"
        )

        # Define the text for the plotting TextArea
        self.plot_text = self.default_plot_text

        # Initialise containters for minima and maxima
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None

        # Initialise the container for the scatter data
        self.x_data = None
        self.y_data = None

        # Attributes for working with threads
        self.assignx_thread = None
        self.assigny_thread = None
        self.plot_thread = None

    def set_x_key(self, node):
        """
        Set the x-axis key for the plot.

        This will set the plot parameter for the x-axis key and update the
        plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the x-axis.
        """
        from h5forest.h5_forest import H5Forest

        # Check the node is 1D
        if node.ndim > 1:
            H5Forest().print("Dataset must be 1D!")
            return self.plot_text

        # If we have any datasets already check we have a compatible shape
        for key in self.plot_params:
            if node.shape != self.plot_params[key].shape:
                H5Forest().print("Datasets must have the same shape!")
                return self.plot_text

        # Set the plot parameter for the x-axis key
        self.plot_params["x"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[0] = f"x-axis:      {node.path}"
        split_text[2] = f"x-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        @error_handler
        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.x_min, self.x_max = node.get_min_max()

        self.assignx_thread = threading.Thread(target=run_in_thread)
        self.assignx_thread.start()

        return self.plot_text

    def set_y_key(self, node):
        """
        Set the y-axis key for the plot.

        This will set the plot parameter for the y-axis key and update the
        plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the y-axis.
        """
        from h5forest.h5_forest import H5Forest

        # Check the node is 1D
        if node.ndim > 1:
            H5Forest().print("Dataset must be 1D!")
            return self.plot_text

        # If we have any datasets already check we have a compatible shape
        for key in self.plot_params:
            if node.shape != self.plot_params[key].shape:
                H5Forest().print("Datasets must have the same shape!")
                return self.plot_text

        # Set the plot parameter for the y-axis key
        self.plot_params["y"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[1] = f"y-axis:      {node.path}"
        split_text[3] = f"y-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        @error_handler
        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.y_min, self.y_max = node.get_min_max()

        self.assigny_thread = threading.Thread(target=run_in_thread)
        self.assigny_thread.start()

        return self.plot_text

    def reset(self):
        """Reset the plotting text."""
        self.plot_text = self.default_plot_text
        self.count_density = None
        self.sum_density = None
        self.mean_density = None
        self.xs = None
        self.ys = None
        self.plot_params = {}
        return self.plot_text

    def _plot(self, text):
        """
        Compute a scatter plot of the datasets.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Don't move on until the data is assigned
        if self.assignx_thread is not None:
            self.assignx_thread.join()
            self.assignx_thread = None
        if self.assigny_thread is not None:
            self.assigny_thread.join()
            self.assigny_thread = None

        # Unpack the nodes
        x_node = self.plot_params["x"]
        y_node = self.plot_params["y"]

        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[2].split(": ")[1].strip()
        y_label = split_text[3].split(": ")[1].strip()
        x_scale = split_text[4].split(": ")[1].strip()
        y_scale = split_text[5].split(": ")[1].strip()
        marker = split_text[6].split(": ")[1].strip()

        # Create the figure
        self.fig = plt.figure(figsize=(3.5, 3.5))
        self.ax = self.fig.add_subplot(111)

        # Draw a grid and make sure its behind everything
        self.ax.grid(True)
        self.ax.set_axisbelow(True)

        def run_in_thread():
            # Now lets plot the data, if we have chunked data we will plot each
            # chunk separately
            if (
                x_node.chunks == (1,)
                and y_node.chunks == (1,)
                or x_node.chunks != y_node.chunks
            ):
                # Get the data
                with h5py.File(x_node.filepath, "r") as hdf:
                    self.x_data = hdf[x_node.path][...]
                    self.y_data = hdf[y_node.path][...]

                # Plot the data
                self.ax.scatter(
                    self.x_data,
                    self.y_data,
                    marker=marker,
                    color="r",
                )

            else:
                # Loop over chunks and plot each one
                with h5py.File(x_node.filepath, "r") as hdf:
                    with ProgressBar(
                        total=x_node.size, description="Scatter"
                    ) as pb:
                        for chunk_index in np.ndindex(*x_node.chunks):
                            # Get the current slice for each dimension
                            slices = tuple(
                                slice(
                                    c_idx * c_size,
                                    min((c_idx + 1) * c_size, s),
                                )
                                for c_idx, c_size, s in zip(
                                    chunk_index, x_node.chunks, x_node.shape
                                )
                            )

                            # Get the data
                            x_data = hdf[x_node.path][slices]
                            y_data = hdf[y_node.path][slices]

                            # Plot the data
                            self.ax.scatter(
                                x_data,
                                y_data,
                                marker=marker,
                                color="r",
                            )

                            pb.advance(step=x_data.size)

        # Validate data for log scales
        from h5forest.h5_forest import H5Forest

        # Check that min/max values are available
        # If None after joining threads, it means get_min_max() failed
        if self.x_min is None or self.x_max is None:
            H5Forest().print(
                "Cannot plot: failed to determine x-axis data range. "
                "See error above for details."
            )
            return

        if self.y_min is None or self.y_max is None:
            H5Forest().print(
                "Cannot plot: failed to determine y-axis data range. "
                "See error above for details."
            )
            return

        if x_scale == "log":
            if self.x_min <= 0:
                H5Forest().print(
                    f"Cannot use log scale on x-axis: data contains "
                    f"{'zero' if self.x_min == 0 else 'negative'} values "
                    f"(min = {self.x_min})"
                )
                return

        if y_scale == "log":
            if self.y_min <= 0:
                H5Forest().print(
                    f"Cannot use log scale on y-axis: data contains "
                    f"{'zero' if self.y_min == 0 else 'negative'} values "
                    f"(min = {self.y_min})"
                )
                return

        # Set the labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Set the scale with error handling
        try:
            self.ax.set_xscale(x_scale)
        except Exception as e:
            H5Forest().print(f"Error setting x-scale to {x_scale}: {str(e)}")
            return

        try:
            self.ax.set_yscale(y_scale)
        except Exception as e:
            H5Forest().print(f"Error setting y-scale to {y_scale}: {str(e)}")
            return

        self.plot_thread = threading.Thread(target=run_in_thread)
        self.plot_thread.start()
        self.plot_thread.join()
        self.plot_thread = None


class HistogramPlotter(Plotter):
    """
    The histogram plotting class.

    Attributes:
        plot_params (dict):
            A dictionary to store the plot parameters.
        default_plot_text (str):
            The default text to display in the plotting TextArea.
        plot_text (str):
            The text to display in the plotting TextArea.
        x_min (float):
            The minimum value for the x-axis.
        x_max (float):
            The maximum value for the x-axis.
        hist (np.ndarray):
            The histogram.
        xs (np.ndarray):
            The x-axis grid.
        widths (np.ndarray):
            The bin widths.
    """

    def __init__(self):
        """Initialise the histogram plotter."""
        # Call the parent class
        super().__init__()

        # Define the default text for the plotting TextArea
        self.default_plot_text = (
            "data:        <key>\n"
            "nbins:       50\n"
            "x-label:     <label>\n"
            "x-scale:     linear\n"
            "y-scale:     linear\n"
        )

        # Define the text for the plotting TextArea
        self.plot_text = self.default_plot_text

        # Initialise containters for minima and maxima
        self.x_min = None
        self.x_max = None

        # Initialise the scaling of each axis (we'll assume linear for now)
        self.x_scale = "linear"
        self.y_scale = "linear"

        # Plotting data containers
        self.hist = None
        self.xs = None
        self.widths = None

        # Attributes for working with threads
        self.assign_data_thread = None
        self.compute_hist_thread = None

    @error_handler
    def set_data_key(self, node):
        """
        Set the data key for the plot.

        This will set the plot parameter for the data key and update the
        plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the data.
        """
        # Set the plot parameter for the data key
        self.plot_params["data"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[0] = f"data:        {node.path}"
        split_text[2] = f"x-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        @error_handler
        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.x_min, self.x_max = node.get_min_max()

        # Run the thread but don't move on until it's finished
        self.assign_data_thread = threading.Thread(target=run_in_thread)

        # Start the thread (we'll join later to ensure its finished when we
        # need it)
        self.assign_data_thread.start()

        return self.plot_text

    @error_handler
    def compute_hist(self, text):
        """
        Compute the histogram.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """

        @error_handler
        def run_in_thread():
            """Compute the histogram."""
            from h5forest.h5_forest import H5Forest

            # Unpack the node
            node = self.plot_params["data"]

            # Split the text
            split_text = text.split("\n")

            # Unpack the number of bins
            nbins = int(split_text[1].split(": ")[1].strip())

            # Unpack scales
            x_scale = split_text[3].split(": ")[1].strip()

            # We need to wait for the data assignment thread to finish
            if self.assign_data_thread is not None:
                self.assign_data_thread.join()
                self.assign_data_thread = None

            # If we got this far we're ready to go so force a redraw
            get_app().invalidate()

            # Check that min/max values are available
            # If None after joining thread, it means get_min_max() failed
            if self.x_min is None or self.x_max is None:
                H5Forest().print(
                    "Cannot compute histogram: failed to determine data "
                    "range. See error above for details."
                )
                return

            # Validate data for log scale
            if x_scale == "log":
                if self.x_min <= 0:
                    H5Forest().print(
                        f"Cannot use log scale: data contains "
                        f"{'zero' if self.x_min == 0 else 'negative'} values "
                        f"(min = {self.x_min})"
                    )
                    return
                bins = np.logspace(
                    np.log10(self.x_min), np.log10(self.x_max), nbins + 1
                )
            else:
                bins = np.linspace(self.x_min, self.x_max, nbins + 1)
            self.widths = bins[1:] - bins[:-1]
            self.xs = (bins[1:] + bins[:-1]) / 2

            # Get the number of chunks
            chunks = node.chunks if node.is_chunked else 1

            # If neither node is not chunked we can just read and grid the data
            if chunks == 1:
                # Get the data
                with h5py.File(node.filepath, "r") as hdf:
                    data = hdf[node.path][...]

                # Compute the grid
                self.hist, _ = np.histogram(data, bins=bins)

            # Otherwise we need to read in the data chunk by chunk and add each
            # chunks grid to the total grid
            else:
                # Initialise the grid
                self.hist = np.zeros(nbins)

                # Get the data
                with h5py.File(node.filepath, "r") as hdf:
                    data = hdf[node.path]

                    # Loop over the chunks
                    with ProgressBar(
                        total=node.size, description="Hist"
                    ) as pb:
                        for chunk_index in np.ndindex(*node.n_chunks):
                            # Get the current slice for each dimension
                            slices = tuple(
                                slice(
                                    c_idx * c_size,
                                    min((c_idx + 1) * c_size, s),
                                )
                                for c_idx, c_size, s in zip(
                                    chunk_index, node.chunks, node.shape
                                )
                            )

                            # Get the chunk
                            chunk_data = data[slices]

                            # Compute the grid for the chunk
                            chunk_density, _ = np.histogram(
                                chunk_data, bins=bins
                            )

                            # Add it to the total
                            self.hist += chunk_density

                            pb.advance(step=chunk_data.size)

        self.compute_hist_thread = threading.Thread(target=run_in_thread)
        self.compute_hist_thread.start()

        return self.plot_text

    @error_handler
    def _plot(self, text):
        """
        Plot the histogram.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        from h5forest.h5_forest import H5Forest

        # Don't move on until the histogram is computed
        self.compute_hist_thread.join()
        self.compute_hist_thread = None

        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[2].split(": ")[1].strip()
        x_scale = split_text[3].split(": ")[1].strip()
        y_scale = split_text[4].split(": ")[1].strip()

        # Check that histogram was computed successfully
        # If None after joining thread, it means compute_hist failed
        if self.hist is None:
            H5Forest().print(
                "Cannot plot histogram: histogram computation failed. "
                "See error above for details."
            )
            return

        # Validate y-axis for log scale (check histogram values)
        if y_scale == "log":
            hist_min = np.min(self.hist)
            if hist_min <= 0:
                H5Forest().print(
                    f"Cannot use log scale on y-axis: histogram contains "
                    f"{'zero' if hist_min == 0 else 'negative'} counts "
                    f"(min = {hist_min})"
                )
                return

        # Create the figure
        self.fig = plt.figure(figsize=(3.5, 3.5))
        self.ax = self.fig.add_subplot(111)

        # Draw a grid and make sure its behind everything
        self.ax.grid(True)
        self.ax.set_axisbelow(True)

        # Draw the bars
        self.ax.bar(self.xs, self.hist, width=self.widths)

        # Set the labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel("$N$")

        # Set the scale with error handling
        try:
            self.ax.set_xscale(x_scale)
        except Exception as e:
            H5Forest().print(f"Error setting x-scale to {x_scale}: {str(e)}")
            return

        try:
            self.ax.set_yscale(y_scale)
        except Exception as e:
            H5Forest().print(f"Error setting y-scale to {y_scale}: {str(e)}")
            return

    def reset(self):
        """Reset the histogram."""
        self.hist = None
        self.xs = None
        self.widths = None
        self.plot_text = self.default_plot_text
        self.fig = None
        self.ax = None
        self.plot_params = {}
        return self.plot_text
