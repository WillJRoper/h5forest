"""This module contains the keybindings for the plotting mode.

The functions in this module are used to define the keybindings for the plotting
mode and attach them to the application. It should not be used directly.
"""
import threading

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, VSplit
from prompt_toolkit.widgets import Label


def _init_plot_bindings(app):
    """Set up the keybindings for the plotting mode."""

    def select_x(event):
        """Select the x-axis."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.plot_content.text = app.density_plotter.set_x_key(node)

        app.return_to_normal_mode()

    def select_y(event):
        """Select the y-axis."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.plot_content.text = app.density_plotter.set_y_key(node)

        app.return_to_normal_mode()

    def select_color(event):
        """Select the color-axis."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.plot_content.text = app.density_plotter.set_color_key(node)

        app.return_to_normal_mode()

    def edit_plot_entry(event):
        """Edit plot param under cursor."""
        # Get the current position and row in the plot content
        current_row = app.plot_content.document.cursor_position_row
        current_pos = app.plot_content.document.cursor_position

        # Get the current row text  in the plot content split into
        # key and value
        split_line = app.density_plotter.get_row(current_row).split(": ")

        # Split the current plot content into lines
        split_text = app.plot_content.text.split("\n")

        def edit_plot_entry_callback():
            """Edit the plot param under cursor."""
            # Strip the user input
            user_input = app.user_input.strip()

            # And set the text here
            split_text[current_row] = (
                f"{split_line[0]}:  ".ljust(13) + f"{user_input}"
            )

            # And display the new text
            app.plot_content.text = "\n".join(split_text)
            app.density_plotter.plot_text = app.plot_content.text

            # And shift focus back to the plot content
            app.shift_focus(app.plot_content)

            # And put the cursor back where it was
            app.plot_content.document = Document(
                text=app.plot_content.text, cursor_position=current_pos
            )

        # Get the modified entry from the user
        app.input(split_line[0], edit_plot_entry_callback)

    def get_count_density(event):
        """Get the count density of the dataset."""

        def run_in_thread():
            """Make the plot."""
            app.density_plotter.compute_counts(app.plot_content.text)

        threading.Thread(target=run_in_thread, daemon=True).start()

        app.return_to_normal_mode()
        app.default_focus()

    def get_sum_density(event):
        """Get the sum density of the dataset."""

        def run_in_thread():
            """Make the plot."""
            app.density_plotter.compute_sums(app.plot_content.text)

        threading.Thread(target=run_in_thread, daemon=True).start()

        app.return_to_normal_mode()
        app.default_focus()

    def get_mean_density(event):
        """Get the mean density of the dataset."""

        def run_in_thread():
            """Make the plot."""
            app.density_plotter.compute_means(app.plot_content.text)

        threading.Thread(target=run_in_thread, daemon=True).start()

        app.return_to_normal_mode()
        app.default_focus()

    def plot_count_density(event):
        """Plot and show pcolormesh with counts in bins."""
        app.density_plotter.plot_count_density(app.plot_content.text)

        # Show it (this resets the plotter class)
        app.density_plotter.show()

        app.return_to_normal_mode()
        app.default_focus()

    def plot_sum_density(event):
        """Plot and show pcolormesh with sum in bins."""
        # Make the plot
        app.density_plotter.plot_sum_density(app.plot_content.text)

        # Show it (this resets the plotter class)
        app.density_plotter.show()

        app.return_to_normal_mode()
        app.default_focus()

    def plot_mean_density(event):
        """Plot and show pcolormesh with mean in bins."""
        # Make the plot
        app.density_plotter.plot_mean_density(app.plot_content.text)

        # Show it (this resets the plotter class)
        app.density_plotter.show()

        app.return_to_normal_mode()
        app.default_focus()

    def save_count(event):
        """Plot and save the density count."""
        app.density_plotter.plot_count_density(app.plot_content.text)

        app.density_plotter.save()

    def save_sum(event):
        """Plot and save the density sum."""
        app.density_plotter.plot_sum_density(app.plot_content.text)

        app.density_plotter.save()

    def save_mean(event):
        """Plot and save the density mean."""
        app.density_plotter.plot_mean_density(app.plot_content.text)

        app.density_plotter.save()

    def reset(event):
        """Reset the plot content."""
        app.plot_content.text = app.density_plotter.reset()

    # Bind the functions
    app.kb.add("x", filter=Condition(lambda: app.flag_plotting_mode))(select_x)
    app.kb.add("y", filter=Condition(lambda: app.flag_plotting_mode))(select_y)
    app.kb.add("w", filter=Condition(lambda: app.flag_plotting_mode))(
        select_color
    )
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.plot_content)),
    )(edit_plot_entry)
    app.kb.add("c", filter=Condition(lambda: app.flag_plotting_mode))(
        get_count_density
    )
    app.kb.add("s", filter=Condition(lambda: app.flag_plotting_mode))(
        get_sum_density
    )
    app.kb.add("m", filter=Condition(lambda: app.flag_plotting_mode))(
        get_mean_density
    )
    app.kb.add("C", filter=Condition(lambda: app.flag_plotting_mode))(
        plot_count_density
    )
    app.kb.add("S", filter=Condition(lambda: app.flag_plotting_mode))(
        plot_sum_density
    )
    app.kb.add("M", filter=Condition(lambda: app.flag_plotting_mode))(
        plot_mean_density
    )
    app.kb.add("c-c", filter=Condition(lambda: app.flag_plotting_mode))(
        save_count
    )
    app.kb.add("c-s", filter=Condition(lambda: app.flag_plotting_mode))(
        save_sum
    )
    app.kb.add("c-m", filter=Condition(lambda: app.flag_plotting_mode))(
        save_mean
    )
    app.kb.add("r", filter=Condition(lambda: app.flag_plotting_mode))(reset)

    # Add the hot keys
    hot_keys = VSplit(
        [
            ConditionalContainer(
                Label("Enter → Edit entry"),
                Condition(lambda: app.app.layout.has_focus(app.plot_content)),
            ),
            ConditionalContainer(
                Label("x → Select x-axis"),
                filter=Condition(
                    lambda: "x" not in app.density_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("y → Select y-axis"),
                filter=Condition(
                    lambda: "y" not in app.density_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("w → Select Weights"),
                filter=Condition(
                    lambda: "weights" not in app.density_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("c → Compute Density (Count)"),
                filter=Condition(
                    lambda: "x" in app.density_plotter.plot_params
                    and "y" in app.density_plotter.plot_params
                    and app.density_plotter.count_density is None
                ),
            ),
            ConditionalContainer(
                Label("s → Compute Density (Sum)"),
                filter=Condition(
                    lambda: "x" in app.density_plotter.plot_params
                    and "y" in app.density_plotter.plot_params
                    and "color" in app.density_plotter.plot_params
                    and app.density_plotter.sum_density is None
                ),
            ),
            ConditionalContainer(
                Label("m → Compute Density (Mean)"),
                filter=Condition(
                    lambda: "x" in app.density_plotter.plot_params
                    and "y" in app.density_plotter.plot_params
                    and "color" in app.density_plotter.plot_params
                    and app.density_plotter.mean_density is None
                ),
            ),
            ConditionalContainer(
                Label("C → Show Density (Count)"),
                filter=Condition(
                    lambda: app.density_plotter.count_density is not None
                ),
            ),
            ConditionalContainer(
                Label("S → Show Density (Sum)"),
                filter=Condition(
                    lambda: app.density_plotter.sum_density is not None
                ),
            ),
            ConditionalContainer(
                Label("M → Show Density (Mean)"),
                filter=Condition(
                    lambda: app.density_plotter.mean_density is not None
                ),
            ),
            ConditionalContainer(
                Label("CTRL-c → Save Density (Count)"),
                filter=Condition(
                    lambda: app.density_plotter.count_density is not None
                ),
            ),
            ConditionalContainer(
                Label("CTRL-s → Save Density (Sum)"),
                filter=Condition(
                    lambda: app.density_plotter.sum_density is not None
                ),
            ),
            ConditionalContainer(
                Label("CTRL-M → Save Density (Mean)"),
                filter=Condition(
                    lambda: app.density_plotter.mean_density is not None
                ),
            ),
            Label("r → Reset"),
            Label("q → Exit Plotting Mode"),
        ]
    )

    return hot_keys
