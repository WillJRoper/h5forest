"""A module containing the bindings for the histogram class.

This module contains the function that defines the bindings for the histogram
and attaches them to the application. It should not be used directly.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler
from h5forest.utils import WaitIndicator


def _init_hist_bindings(app):
    """Set up the bindings for histogram mode."""

    @error_handler
    def select_data(event):
        """Select the dataset for the histogram."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the histogram area
        app.hist_content.text = app.histogram_plotter.set_data_key(node)

    @error_handler
    def edit_bins(event):
        """Edit the number of bins."""
        # Wait for data assignment thread to finish if it's running
        if app.histogram_plotter.assign_data_thread is not None:
            with WaitIndicator(app, "Computing data range..."):
                app.histogram_plotter.assign_data_thread.join()
            app.histogram_plotter.assign_data_thread = None

        # Check if x_min/x_max are available (needed to compute histogram)
        if (
            app.histogram_plotter.x_min is None
            or app.histogram_plotter.x_max is None
        ):
            app.print(
                "Cannot edit bins: data range not yet computed. "
                "Please select a dataset first (Enter)"
            )
            return

        # Get the current text
        split_text = app.hist_content.text.split("\n")

        # Get the current bins value
        current_bins = split_text[1].split(": ")[1].strip()

        def edit_bins_callback():
            """Update the bins value."""
            # Strip the user input
            user_input = app.user_input.strip()

            # Update the text
            split_text[1] = f"nbins:       {user_input}"
            app.hist_content.text = "\n".join(split_text)
            app.histogram_plotter.plot_text = app.hist_content.text

            # Return to tree focus
            app.shift_focus(app.tree_content)

        # Get the modified entry from the user
        app.input(
            "Number of bins", edit_bins_callback, mini_buffer_text=current_bins
        )

    @error_handler
    def toggle_x_scale(event):
        """Toggle the x-axis scale between linear and log."""
        # Wait for data assignment thread to finish if it's running
        if app.histogram_plotter.assign_data_thread is not None:
            with WaitIndicator(app, "Computing data range..."):
                app.histogram_plotter.assign_data_thread.join()
            app.histogram_plotter.assign_data_thread = None

        # Check if x_min/x_max are available
        if (
            app.histogram_plotter.x_min is None
            or app.histogram_plotter.x_max is None
        ):
            app.print(
                "Cannot toggle x-scale: data range not yet computed. "
                "Please select a dataset first (Enter)"
            )
            return

        # Get the current text
        split_text = app.hist_content.text.split("\n")

        # Get the current x-scale
        current_scale = split_text[3].split(": ")[1].strip()

        # Toggle the scale
        new_scale = "log" if current_scale == "linear" else "linear"

        # If toggling to log, validate data is compatible
        if new_scale == "log":
            if app.histogram_plotter.x_min <= 0:
                value_type = (
                    "zero" if app.histogram_plotter.x_min == 0 else "negative"
                )
                app.print(
                    f"Cannot use log scale on x-axis: data contains "
                    f"{value_type} values "
                    f"(min = {app.histogram_plotter.x_min})"
                )
                return

        split_text[3] = f"x-scale:     {new_scale}"

        # Update the text
        app.hist_content.text = "\n".join(split_text)
        app.histogram_plotter.plot_text = app.hist_content.text

        app.app.invalidate()

    @error_handler
    def toggle_y_scale(event):
        """Toggle the y-axis scale between linear and log."""
        # Wait for data assignment thread to finish if it's running
        if app.histogram_plotter.assign_data_thread is not None:
            with WaitIndicator(app, "Computing data range..."):
                app.histogram_plotter.assign_data_thread.join()
            app.histogram_plotter.assign_data_thread = None

        # Check if x_min/x_max are available (needed to compute histogram)
        if (
            app.histogram_plotter.x_min is None
            or app.histogram_plotter.x_max is None
        ):
            app.print(
                "Cannot toggle y-scale: data range not yet computed. "
                "Please select a dataset first (Enter)"
            )
            return

        # Get the current text
        split_text = app.hist_content.text.split("\n")

        # Get the current y-scale
        current_scale = split_text[4].split(": ")[1].strip()

        # Toggle the scale
        new_scale = "log" if current_scale == "linear" else "linear"

        # Note: We can't validate y-scale until histogram is computed
        # (y-scale applies to histogram counts, not data values)
        # Validation will happen when the histogram is plotted

        split_text[4] = f"y-scale:     {new_scale}"

        # Update the text
        app.hist_content.text = "\n".join(split_text)
        app.histogram_plotter.plot_text = app.hist_content.text

        app.app.invalidate()

    @error_handler
    def edit_hist_entry(event):
        """Edit histogram param under cursor."""
        # Get the current position and row in the plot content
        current_row = app.hist_content.document.cursor_position_row
        current_pos = app.hist_content.document.cursor_position

        # Get the current row text  in the plot content split into
        # key and value
        split_line = app.histogram_plotter.get_row(current_row).split(": ")

        # Split the current plot content into lines
        split_text = app.hist_content.text.split("\n")

        # If we're on a toggle option (i.e. scaling is linear or log) lets
        # toggle it rather than edit it
        if "scale" in split_line[0]:
            if split_line[1].strip() == "linear":
                split_text[current_row] = (
                    f"{split_line[0]}:  ".ljust(13) + "log"
                )
            else:
                split_text[current_row] = (
                    f"{split_line[0]}:  ".ljust(13) + "linear"
                )

            app.hist_content.text = "\n".join(split_text)

            # And put the cursor back where it was
            app.hist_content.document = Document(
                text=app.hist_content.text, cursor_position=current_pos
            )
            app.histogram_plotter.plot_text = app.hist_content.text

            app.app.invalidate()

            return

        def edit_hist_entry_callback():
            """Edit the plot param under cursor."""
            # Strip the user input
            user_input = app.user_input.strip()

            # And set the text here
            split_text[current_row] = (
                f"{split_line[0]}:  ".ljust(13) + f"{user_input}"
            )

            # And display the new text
            app.hist_content.text = "\n".join(split_text)
            app.histogram_plotter.plot_text = app.hist_content.text

            # And shift focus back to the plot content
            app.shift_focus(app.hist_content)

            # And put the cursor back where it was
            app.hist_content.document = Document(
                text=app.hist_content.text, cursor_position=current_pos
            )

        # Get the modified entry from the user
        app.input(split_line[0], edit_hist_entry_callback)

    @error_handler
    def plot_hist(event):
        """Plot the histogram."""
        # Don't update if we already have everything
        if len(app.histogram_plotter.plot_params) == 0:
            # Get the node under the cursor
            node = app.tree.get_current_node(app.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                app.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            app.hist_content.text = app.histogram_plotter.set_data_key(node)

        # Compute and plot the histogram with wait indicator
        with WaitIndicator(app, "Generating histogram..."):
            # Compute the histogram
            app.hist_content.text = app.histogram_plotter.compute_hist(
                app.hist_content.text
            )

            # Get the plot
            app.histogram_plotter.plot_and_show(app.hist_content.text)

    @error_handler
    def save_hist(event):
        """Plot the histogram."""
        # Don't update if we already have everything
        if len(app.histogram_plotter.plot_params) == 0:
            # Get the node under the cursor
            node = app.tree.get_current_node(app.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                app.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            app.hist_content.text = app.histogram_plotter.set_data_key(node)

        # Compute the histogram
        app.hist_content.text = app.histogram_plotter.compute_hist(
            app.hist_content.text
        )

        # Get the plot
        app.histogram_plotter.plot_and_save(app.hist_content.text)

    @error_handler
    def reset_hist(event):
        """Reset the histogram content."""
        app.histogram_plotter.close()
        app.hist_content.text = app.histogram_plotter.reset()
        app.return_to_normal_mode()
        app.default_focus()

    @error_handler
    def edit_hist(event):
        """Edit the histogram configuration."""
        if app.app.layout.has_focus(app.hist_content):
            # Already in config, jump back to tree
            app.shift_focus(app.tree_content)
        else:
            # In tree, jump to config
            app.shift_focus(app.hist_content)

    @error_handler
    def exit_hist_mode(event):
        """Exit histogram mode."""
        app.histogram_plotter.close()
        app.hist_content.text = app.histogram_plotter.reset()
        app.return_to_normal_mode()
        app.default_focus()

    def exit_edit_hist(event):
        """Exit the edit mode."""
        app.shift_focus(app.tree_content)

    # Bind the functions
    app.kb.add(
        "enter",
        filter=Condition(
            lambda: app.flag_hist_mode
            and not app.app.layout.has_focus(app.hist_content)
        ),
    )(select_data)
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.hist_content)),
    )(edit_hist_entry)
    app.kb.add("b", filter=Condition(lambda: app.flag_hist_mode))(edit_bins)
    app.kb.add("x", filter=Condition(lambda: app.flag_hist_mode))(
        toggle_x_scale
    )
    app.kb.add("y", filter=Condition(lambda: app.flag_hist_mode))(
        toggle_y_scale
    )
    app.kb.add("h", filter=Condition(lambda: app.flag_hist_mode))(plot_hist)
    app.kb.add("H", filter=Condition(lambda: app.flag_hist_mode))(save_hist)
    app.kb.add("r", filter=Condition(lambda: app.flag_hist_mode))(reset_hist)
    app.kb.add("e", filter=Condition(lambda: app.flag_hist_mode))(edit_hist)
    app.kb.add(
        "q",
        filter=Condition(
            lambda: app.flag_hist_mode
            and not app.app.layout.has_focus(app.hist_content)
        ),
    )(exit_hist_mode)
    app.kb.add(
        "q",
        filter=Condition(lambda: app.app.layout.has_focus(app.hist_content)),
    )(exit_edit_hist)

    # Return all possible hot keys as a dict
    # The app will use property methods to filter based on state
    hot_keys = {
        "edit_config": Label("e → Edit Config"),
        "edit_tree": Label("e → Back To Tree"),
        "edit_entry": Label("Enter → Edit entry"),
        "select_data": Label("Enter → Select data"),
        "edit_bins": Label("b → Edit bins"),
        "toggle_x_scale": Label("x → Toggle x-scale"),
        "toggle_y_scale": Label("y → Toggle y-scale"),
        "show_hist": Label("h → Show Histogram"),
        "save_hist": Label("H → Save Histogram"),
        "reset": Label("r → Reset"),
        "exit_mode": Label("q → Exit Hist Mode"),
        "exit_config": Label("q → Exit Hist Config"),
    }

    return hot_keys
