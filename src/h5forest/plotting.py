"""A module for plotting with matplotlib directly from the HDF5 file.
"""
import matplotlib.pyplot as plt


class HexbinPlotter:
    def __init__(self):
        # Container for the plot parameters
        self.plot_params = {}

        # Define the default text for the plotting TextArea
        self.default_plot_text = (
            "x-axis: <x key>\n"
            "y-axis: <y key>\n"
            "color-axis: <color key\n"
            "x-label: <x-axis label (x key by default)>\n"
            "y-label: <y-axis label (y key by default)>\n"
            "c-label: <color-axis label (color key by default)>\n"
        )

        # Define the text for the plotting TextArea
        self.plot_text = self.default_plot_text

    def set_x_key(self, node):
        """
        Set the x-axis key for the plot.

        This will set the plot parameter for the x-axis key and update the
        plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the x-axis.
        """
        # Set the plot parameter for the x-axis key
        self.plot_params["x"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[0] = f"x-axis: {node.path}"
        self.plot_text = "\n".join(split_text)

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
        # Set the plot parameter for the y-axis key
        self.plot_params["y"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[1] = f"y-axis: {node.path}"
        self.plot_text = "\n".join(split_text)

        return self.plot_text

    def set_color_key(self, node):
        """
        Set the color-axis key for the plot.

        This will set the plot parameter for the color-axis key and update the
        plotting text.

        Args:
            node (h5forest.h5_forest.Node):
                The node to use for the color-axis.
        """
        # Set the plot parameter for the color-axis key
        self.plot_params["color"] = node

        # Set the text in the plotting area
        split_text = self.plot_text.split("\n")
        split_text[2] = f"color-axis: {node.path}"
        self.plot_text = "\n".join(split_text)

        return self.plot_text

    def __len__(self):
        """Return the number of plot parameters."""
        return len(self.plot_params)

    def show(self):
        """Show the plot and reset everything."""
        plt.show()
        self.plot_params = {}
        self.plot_text = self.default_plot_text

    def plot_hexbin_count(self):
        """
        Plot the hexbin count.

        If the node is has chunks we will plot the hexbin chunk by chunk.
        """

        # Unpack the nodes
        x_node = self.plot_params["x"]
        y_node = self.plot_params["y"]
        color_node = self.plot_params["color"]

        # If the node is not chunked we can just read and plot the data
        if (
            not x_node.is_chunked
            and not y_node.is_chunked
            and not color_node.is_chunked
        ):
            x_data = x_node.read()
            y_data = y_node.read()
            color_data = color_node.read()

            # Create the hexbin plot
            plt.hexbin(
                x_data, y_data, C=color_data, gridsize=30, cmap="viridis"
            )

            # Set the labels
            plt.xlabel(self.plot_params["x"])
            plt.ylabel(self.plot_params["y"])
            plt.colorbar(label=self.plot_params["color"])

            # Show the plot
            plt.show()

        # Get the x, y and color data
        x_data = self.forest.get_data(self.plot_params["x"])
        y_data = self.forest.get_data(self.plot_params["y"])
        color_data = self.forest.get_data(self.plot_params["color"])

        # Create the hexbin plot
        plt.hexbin(x_data, y_data, C=color_data, gridsize=30, cmap="viridis")

        # Set the labels
        plt.xlabel(self.plot_params["x"])
        plt.ylabel(self.plot_params["y"])
        plt.colorbar(label=self.plot_params["color"])

        # Show the plot
        plt.show()
