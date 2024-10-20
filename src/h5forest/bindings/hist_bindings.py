"""A module containing the bindings for the histogram class.

This module contains the function that defines the bindings for the histogram
and attaches them to the application. It should not be used directly.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, VSplit
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_hist_bindings(app):
    """Set up the bindings for histogram mode."""

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
        app.hist_content.text = app.histogram_plotter.reset()
        app.return_to_normal_mode()
        app.default_focus()

    @error_handler
    def edit_hist(event):
        """Edit the histogram."""
        app.shift_focus(app.hist_content)

    def exit_edit_hist(event):
        """Exit the edit mode."""
        app.shift_focus(app.tree_content)

    # Bind the functions
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.hist_content)),
    )(edit_hist_entry)
    app.kb.add("h", filter=Condition(lambda: app.flag_hist_mode))(plot_hist)
    app.kb.add("H", filter=Condition(lambda: app.flag_hist_mode))(save_hist)
    app.kb.add("r", filter=Condition(lambda: app.flag_hist_mode))(reset_hist)
    app.kb.add(
        "e",
        filter=Condition(
            lambda: app.flag_hist_mode
            and len(app.histogram_plotter.plot_params) > 0
        ),
    )(edit_hist)
    app.kb.add(
        "q",
        filter=Condition(lambda: app.app.layout.has_focus(app.hist_content)),
    )(exit_edit_hist)

    # Add the hot keys
    hot_keys = VSplit(
        [
            ConditionalContainer(
                Label("e → Edit Config"),
                Condition(lambda: len(app.histogram_plotter.plot_params) > 0),
            ),
            ConditionalContainer(
                Label("Enter → Edit entry"),
                Condition(lambda: app.app.layout.has_focus(app.hist_content)),
            ),
            Label("h → Show Histogram"),
            Label("H → Save Histogram"),
            Label("r → Reset"),
            ConditionalContainer(
                Label("q → Exit Hist Mode"),
                Condition(
                    lambda: not app.app.layout.has_focus(app.hist_content)
                ),
            ),
            ConditionalContainer(
                Label("q → Exit Config"),
                Condition(lambda: app.app.layout.has_focus(app.hist_content)),
            ),
        ]
    )

    return hot_keys
