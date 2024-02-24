"""A module containing the bindings for the histogram class.

This module contains the function that defines the bindings for the histogram
and attaches them to the application. It should not be used directly.
"""
import threading

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, VSplit
from prompt_toolkit.widgets import Label


def _init_hist_bindings(app):
    """Set up the bindings for histogram mode."""

    @app.error_handler
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

    @app.error_handler
    def select_data(event):
        """Select the data to sort into bins."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.hist_content.text = app.histogram_plotter.set_data_key(node)

        app.return_to_normal_mode()
        app.default_focus()

    @app.error_handler
    def compute_hist(event):
        """Compute the histogram."""

        def run_in_thread():
            """Make the plot."""
            app.histogram_plotter.compute_hist(app.hist_content.text)

        threading.Thread(target=run_in_thread, daemon=True).start()

        app.return_to_normal_mode()
        app.default_focus()

    @app.error_handler
    def plot_hist(event):
        """Plot the histogram."""
        app.histogram_plotter.plot_hist(app.hist_content.text)

        app.histogram_plotter.show()

        app.return_to_normal_mode()
        app.default_focus()

    @app.error_handler
    def save_hist(event):
        """Plot the histogram."""
        app.histogram_plotter.plot_hist(app.hist_content.text)

        app.histogram_plotter.save()

    @app.error_handler
    def reset_hist(event):
        """Reset the histogram content."""
        app.hist_content.text = app.histogram_plotter.reset()

    # Bind the functions
    app.kb.add("enter", filter=Condition(lambda: app.flag_hist_mode))(
        edit_hist_entry
    )
    app.kb.add("d", filter=Condition(lambda: app.flag_hist_mode))(select_data)
    app.kb.add("h", filter=Condition(lambda: app.flag_hist_mode))(compute_hist)
    app.kb.add("H", filter=Condition(lambda: app.flag_hist_mode))(plot_hist)
    app.kb.add("c-h", filter=Condition(lambda: app.flag_hist_mode))(save_hist)
    app.kb.add("r", filter=Condition(lambda: app.flag_hist_mode))(reset_hist)

    # Add the hot keys
    hot_keys = VSplit(
        [
            ConditionalContainer(
                Label("Enter → Edit entry"),
                Condition(lambda: app.app.layout.has_focus(app.hist_content)),
            ),
            ConditionalContainer(
                Label("d → Select data"),
                filter=Condition(
                    lambda: "data" not in app.histogram_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("h → Compute Histogram"),
                filter=Condition(
                    lambda: "data" in app.histogram_plotter.plot_params
                    and app.histogram_plotter.hist is None
                ),
            ),
            ConditionalContainer(
                Label("H → Show Histogram"),
                filter=Condition(
                    lambda: app.histogram_plotter.hist is not None
                ),
            ),
            ConditionalContainer(
                Label("CTRL-h → Save Histogram"),
                filter=Condition(
                    lambda: app.histogram_plotter.hist is not None
                ),
            ),
            Label("r → Reset"),
            Label("q → Exit Hist Mode"),
        ]
    )

    return hot_keys
