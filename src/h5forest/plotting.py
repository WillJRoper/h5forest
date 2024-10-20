"""A module for plotting with matplotlib directly from the HDF5 file.

This is only ever called from the h5forest module and is not intended to be
used directly by the user.
"""

import os
import threading
import warnings

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
            mini_buffer_text=os.getcwd() + "/",
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


class DensityPlotter(Plotter):
    """
    The density grid plotting class.

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
        c_min (float):
            The minimum value for the color-axis.
        c_max (float):
            The maximum value for the color-axis.
        count_density (np.ndarray):
            The grid of counts.
        sum_density (np.ndarray):
            The grid of sums.
        mean_density (np.ndarray):
            The grid of means.
        xs (np.ndarray):
            The x-axis grid.
        ys (np.ndarray):
            The y-axis grid.
    """

    def __init__(self):
        """Initialise the density plotter."""
        # Call the parent class
        super().__init__()

        # Define the default text for the plotting TextArea
        self.default_plot_text = (
            "x-axis:      <key>\n"
            "y-axis:      <key>\n"
            "weights:     <key>\n"
            "x-bins:      100\n"
            "y-bins:      100\n"
            "x-label:     <label>\n"
            "y-label:     <label>\n"
            "w-label:     <label>\n"
            "x-scale:     log\n"
            "y-scale:     log\n"
            "w-scale:     log\n"
        )

        # Define the text for the plotting TextArea
        self.plot_text = self.default_plot_text

        # Initialise containters for minima and maxima
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.c_min = None
        self.c_max = None

        # Initialise the container for the density grid
        self.count_density = None
        self.sum_density = None
        self.mean_density = None
        self.xs = None
        self.ys = None

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
        split_text[5] = f"x-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.x_min, self.x_max = node.get_min_max()

        threading.Thread(target=run_in_thread, daemon=True).start()

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
        split_text[6] = f"y-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.y_min, self.y_max = node.get_min_max()

        threading.Thread(target=run_in_thread, daemon=True).start()

        return self.plot_text

    def set_color_key(self, node):
        """
        Set the weights-axis key for the plot.

        This will set the plot parameter for the weights-axis key and update
        the plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the weights-axis.
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

        # Set the plot parameter for the weights-axis key
        self.plot_params["weights"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[2] = f"weights:     {node.path}"
        split_text[7] = f"w-label:     {node.path}"
        self.plot_text = "\n".join(split_text)

        def run_in_thread():
            # Get the minimum and maximum values for the x and y axes
            self.c_min, self.c_max = node.get_min_max()

        threading.Thread(target=run_in_thread, daemon=True).start()

        return self.plot_text

    def reset(self):
        """Reset the plotting text."""
        self.plot_text = self.default_plot_text
        self.count_density = None
        self.sum_density = None
        self.mean_density = None
        self.xs = None
        self.ys = None
        return self.plot_text

    def compute_counts(self, text):
        """
        Compute a density plot of the datasets.

        If the nodes have chunks we will calculate the density chunk by chunk.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Unpack the nodes
        x_node = self.plot_params["x"]
        y_node = self.plot_params["y"]

        # Unpack the labels scales
        split_text = text.split("\n")
        x_scale = split_text[8].split(": ")[1].strip()
        y_scale = split_text[9].split(": ")[1].strip()
        w_scale = split_text[10].split(": ")[1].strip()

        # Unpack the bins
        x_bins = int(split_text[3].split(": ")[1].strip())
        y_bins = int(split_text[4].split(": ")[1].strip())

        # Define the bins
        if x_scale == "log":
            self.xs = np.logspace(
                np.log10(self.x_min), np.log10(self.x_max), x_bins + 1
            )
        else:
            self.xs = np.linspace(self.x_min, self.x_max, x_bins + 1)
        if y_scale == "log":
            self.ys = np.logspace(
                np.log10(self.y_min), np.log10(self.y_max), y_bins + 1
            )
        else:
            self.ys = np.linspace(self.y_min, self.y_max, y_bins + 1)

        # Get the chunk shape
        chunk_shape = min((x_node.chunks[0], y_node.chunks[0]))

        # Get the number of chunks
        chunks = (
            x_node.shape[0] // chunk_shape if chunk_shape is not None else 1
        )

        # If neither node is not chunked we can just read and grid the data
        if chunks == 1:
            # Get the data
            with h5py.File(x_node.filepath, "r") as hdf:
                x_data = hdf[x_node.path][...]
                y_data = hdf[y_node.path][...]

            # Compute the grid
            self.count_density, _, _ = np.histogram2d(
                x_data,
                y_data,
                bins=(self.xs, self.ys),
                range=[[self.x_min, self.x_max], [self.y_min, self.y_max]],
            )

        # Otherwise we need to read in the data chunk by chunk and add each
        # chunks grid to the total grid
        else:
            # Initialise the grid
            self.count_density = np.zeros((x_bins, y_bins))

            # Get the data
            with h5py.File(x_node.filepath, "r") as hdf:
                x_data = hdf[x_node.path]
                y_data = hdf[y_node.path]

                # Get the shape of the data
                x_shape = x_data.shape[0]

                # Loop over the chunks
                with ProgressBar(
                    total=x_node.size, description="2DHist"
                ) as pb:
                    for i in range(chunks):
                        # Define the slice
                        _slice = slice(
                            i * chunk_shape,
                            min(((i + 1) * chunk_shape, x_shape)),
                        )

                        # Compute the grid for the chunk
                        chunk_density, _, _ = np.histogram2d(
                            x_data[_slice],
                            y_data[_slice],
                            bins=(self.xs, self.ys),
                            range=[
                                [self.x_min, self.x_max],
                                [self.y_min, self.y_max],
                            ],
                        )

                        # Add it to the total
                        self.count_density += chunk_density

                        pb.advance(step=chunk_shape)

        # Apply log to z axis if desired
        if w_scale == "log":
            self.count_density[self.count_density > 0] = np.log10(
                self.count_density[self.count_density > 0]
            )

            # Remove any zeros
            self.count_density[self.count_density <= 0] = np.nan

    def compute_sums(self, text):
        """
        Compute a density plot of the datasets collecting the sum.

        If the nodes have chunks we will calculate the density chunk by chunk.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Unpack the nodes
        x_node = self.plot_params["x"]
        y_node = self.plot_params["y"]
        w_node = self.plot_params["weights"]

        # Unpack the labels scales
        split_text = text.split("\n")
        x_scale = split_text[8].split(": ")[1].strip()
        y_scale = split_text[9].split(": ")[1].strip()
        w_scale = split_text[10].split(": ")[1].strip()

        # Unpack the bins
        x_bins = int(split_text[3].split(": ")[1].strip())
        y_bins = int(split_text[4].split(": ")[1].strip())

        # Define the bins
        if x_scale == "log":
            self.xs = np.logspace(
                np.log10(self.x_min), np.log10(self.x_max), x_bins + 1
            )
        else:
            self.xs = np.linspace(self.x_min, self.x_max, x_bins + 1)
        if y_scale == "log":
            self.ys = np.logspace(
                np.log10(self.y_min), np.log10(self.y_max), y_bins + 1
            )
        else:
            self.ys = np.linspace(self.y_min, self.y_max, y_bins + 1)

        # Get the chunk shape
        chunk_shape = min((x_node.chunks[0], y_node.chunks[0]))

        # Get the number of chunks
        chunks = x_node.shape[0] // chunk_shape

        # If neither node is not chunked we can just read and grid the data
        if chunks == 1:
            # Get the data
            with h5py.File(x_node.filepath, "r") as hdf:
                x_data = hdf[x_node.path][...]
                y_data = hdf[y_node.path][...]
                w_data = hdf[w_node.path][...]

            # Compute the grid
            self.sum_density, _, _ = np.histogram2d(
                x_data,
                y_data,
                weights=w_data,
                bins=(self.xs, self.ys),
                range=[[self.x_min, self.x_max], [self.y_min, self.y_max]],
            )

        # Otherwise we need to read in the data chunk by chunk and add each
        # chunks grid to the total grid
        else:
            # Initialise the grid
            self.sum_density = np.zeros((x_bins, y_bins))

            # Get the data
            with h5py.File(x_node.filepath, "r") as hdf:
                x_data = hdf[x_node.path]
                y_data = hdf[y_node.path]
                w_data = hdf[w_node.path]

                # Get the shape of the data
                x_shape = x_data.shape[0]

                # Loop over the chunks
                with ProgressBar(
                    total=x_node.size, description="2DHist"
                ) as pb:
                    for i in range(chunks):
                        # Define the slice
                        _slice = slice(
                            i * chunk_shape,
                            min(((i + 1) * chunk_shape, x_shape)),
                        )

                        # Compute the grid for the chunk
                        chunk_density, _, _ = np.histogram2d(
                            x_data[_slice],
                            y_data[_slice],
                            weights=w_data[_slice],
                            bins=(self.xs, self.ys),
                            range=[
                                [self.x_min, self.x_max],
                                [self.y_min, self.y_max],
                            ],
                        )

                        # Add it to the total
                        self.sum_density += chunk_density

                        pb.advance(step=chunk_shape)

        # Apply log to z axis if desired
        if w_scale == "log":
            self.sum_density[self.sum_density > 0] = np.log10(
                self.sum_density[self.sum_density > 0]
            )

            # Remove any zeros
            self.sum_density[self.sum_density <= 0] = np.nan

    def compute_means(self, text):
        """
        Compute a density plot of the datasets collecting the mean.

        If the nodes have chunks we will calculate the density chunk by chunk.

        Args:
            text (str):
                The text to extract the plot parameters from.
        """
        # Get the sum and counts
        self.compute_counts(text)
        self.compute_sums(text)

        # Calculate the mean
        self.mean_density = self.sum_density / self.count_density

    def plot_count_density(self, text):
        """
        Plot pcolormesh with counts in bins.

        This will plot the pcolormesh with histograms along the axes.
        """
        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[5].split(": ")[1].strip()
        y_label = split_text[6].split(": ")[1].strip()
        x_scale = split_text[8].split(": ")[1].strip()
        y_scale = split_text[9].split(": ")[1].strip()

        # Create the figure
        self.fig = plt.figure(figsize=(3.5, 3.5))
        self.ax = self.fig.add_subplot(111)

        # Visulise the grid
        self.ax.pcolormesh(
            self.xs,
            self.ys,
            self.count_density.T,
            cmap="plasma",
        )

        # Set the labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Set the scale
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)

    def plot_sum_density(self, text):
        """
        Plot pcolormesh with sums in bins.

        This will plot the pcolormesh with histograms along the axes.
        """
        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[5].split(": ")[1].strip()
        y_label = split_text[6].split(": ")[1].strip()
        w_label = split_text[7].split(": ")[1].strip()
        x_scale = split_text[8].split(": ")[1].strip()
        y_scale = split_text[9].split(": ")[1].strip()
        w_scale = split_text[10].split(": ")[1].strip()

        # Create the figure
        self.fig = plt.figure(figsize=(3.5, 3.5))
        self.ax = self.fig.add_subplot(111)

        # Visulise the grid
        im = self.ax.pcolormesh(
            self.xs,
            self.ys,
            self.sum_density.T,
            cmap="plasma",
        )

        # Set the labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Set the scale
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)

        # Draw the colorbar and label it
        cbar = self.fig.colorbar(im)
        if w_scale == "log" and "log" not in w_label:
            cbar.set_label(r"$\log_{10}$" f"({w_label})")
        else:
            cbar.set_label(w_label)

    def plot_mean_density(self, text):
        """
        Plot pcolormesh with sums in bins.

        This will plot the pcolormesh with histograms along the self.axes.
        """
        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[5].split(": ")[1].strip()
        y_label = split_text[6].split(": ")[1].strip()
        w_label = split_text[7].split(": ")[1].strip()
        x_scale = split_text[8].split(": ")[1].strip()
        y_scale = split_text[9].split(": ")[1].strip()
        w_scale = split_text[10].split(": ")[1].strip()

        # Create the figure
        self.fig = plt.figure(figsize=(3.5, 3.5))
        self.ax = self.fig.add_subplot(111)

        # Visulise the grid
        im = self.ax.pcolormesh(
            self.xs,
            self.ys,
            self.mean_density.T,
            cmap="plasma",
        )

        # Set the labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Set the scale
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)

        # Draw the colorbar and label it
        cbar = self.fig.colorbar(im)
        if w_scale == "log" and "log" not in w_label:
            cbar.set_label(r"<$\log_{10}$" f"({w_label})>")
        else:
            cbar.set_label(f"<{w_label}>")


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

        # Flags for working with threads
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

        def run_in_thread():
            """Compute the histogram."""
            # Unpack the node
            node = self.plot_params["data"]

            # Split the text
            split_text = text.split("\n")

            # Unpack the number of bins
            nbins = int(split_text[1].split(": ")[1].strip())

            # Unpack scales
            x_scale = split_text[3].split(": ")[1].strip()

            # We need to wait for the data assignment thread to finish
            self.assign_data_thread.join()
            self.assign_data_thread = None

            # If we got this far we're ready to go so force a redraw
            get_app().invalidate()

            # Define the bins
            if x_scale == "log":
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

                # Compute the number of chunks in each dimension
                n_chunks = [
                    int(np.ceil(s / c))
                    for s, c in zip(node.shape, node.chunks)
                ]

                # Get the data
                with h5py.File(node.filepath, "r") as hdf:
                    data = hdf[node.path]

                    # Loop over the chunks
                    with ProgressBar(
                        total=node.size, description="Hist"
                    ) as pb:
                        for chunk_index in np.ndindex(*n_chunks):
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
        # Don't move on until the histogram is computed
        self.compute_hist_thread.join()
        self.compute_hist_thread = None

        # Unpack the labels scales
        split_text = text.split("\n")
        x_label = split_text[2].split(": ")[1].strip()
        x_scale = split_text[3].split(": ")[1].strip()
        y_scale = split_text[4].split(": ")[1].strip()

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

        # Set the scale
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)

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
