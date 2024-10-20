"""This module contains the keybindings for the plotting mode.

The functions in this module are used to define the keybindings for the
plotting mode and attach them to the application. It should not be used
directly.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, VSplit
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_plot_bindings(app):
    """Set up the keybindings for the plotting mode."""

    @error_handler
    def select_x(event):
        """Select the x-axis."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.plot_content.text = app.scatter_plotter.set_x_key(node)

    @error_handler
    def select_y(event):
        """Select the y-axis."""
        # Get the node under the cursor
        node = app.tree.get_current_node(app.current_row)

        # Exit if the node is not a Dataset
        if node.is_group:
            app.print(f"{node.path} is not a Dataset")
            return

        # Set the text in the plotting area
        app.plot_content.text = app.scatter_plotter.set_y_key(node)

    @error_handler
    def edit_plot_entry(event):
        """Edit plot param under cursor."""
        # Get the current position and row in the plot content
        current_row = app.plot_content.document.cursor_position_row
        current_pos = app.plot_content.document.cursor_position

        # Get the current row text  in the plot content split into
        # key and value
        split_line = app.scatter_plotter.get_row(current_row).split(": ")

        # Split the current plot content into lines
        split_text = app.plot_content.text.split("\n")

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

            app.plot_content.text = "\n".join(split_text)

            # And put the cursor back where it was
            app.plot_content.document = Document(
                text=app.plot_content.text, cursor_position=current_pos
            )
            app.scatter_plotter.plot_text = app.plot_content.text

            app.app.invalidate()

            return

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
            app.scatter_plotter.plot_text = app.plot_content.text

            # And shift focus back to the plot content
            app.shift_focus(app.plot_content)

            # And put the cursor back where it was
            app.plot_content.document = Document(
                text=app.plot_content.text, cursor_position=current_pos
            )

        # Get the modified entry from the user
        app.input(split_line[0], edit_plot_entry_callback)

    @error_handler
    def plot_scatter(event):
        """Plot and show pcolormesh with mean in bins."""
        # Make the plot
        app.scatter_plotter.plot_and_show(app.plot_content.text)

        app.return_to_normal_mode()
        app.default_focus()

    @error_handler
    def save_scatter(event):
        """Save the plot."""
        app.scatter_plotter.plot_and_save(app.plot_content.text)

    @error_handler
    def reset(event):
        """Reset the plot content."""
        app.plot_content.text = app.scatter_plotter.reset()

        app.app.invalidate()
        app.return_to_normal_mode()
        app.default_focus()

    @error_handler
    def edit_plot(event):
        """Edit the plot."""
        app.shift_focus(app.plot_content)

    def exit_edit_plot(event):
        """Exit edit plot mode."""
        app.shift_focus(app.tree_content)

    # Bind the functions
    app.kb.add("x", filter=Condition(lambda: app.flag_plotting_mode))(select_x)
    app.kb.add("y", filter=Condition(lambda: app.flag_plotting_mode))(select_y)
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.plot_content)),
    )(edit_plot_entry)
    app.kb.add("p", filter=Condition(lambda: app.flag_plotting_mode))(
        plot_scatter
    )
    app.kb.add("P", filter=Condition(lambda: app.flag_plotting_mode))(
        save_scatter
    )
    app.kb.add("r", filter=Condition(lambda: app.flag_plotting_mode))(reset)
    app.kb.add(
        "e",
        filter=Condition(
            lambda: app.flag_plotting_mode
            and len(app.scatter_plotter.plot_params) > 0
        ),
    )(edit_plot)
    app.kb.add(
        "q",
        filter=Condition(lambda: app.app.layout.has_focus(app.plot_content)),
    )(exit_edit_plot)

    # Add the hot keys
    hot_keys = VSplit(
        [
            ConditionalContainer(
                Label("e → Edit Config"),
                Condition(lambda: len(app.scatter_plotter.plot_params) > 0),
            ),
            ConditionalContainer(
                Label("Enter → Edit entry"),
                Condition(lambda: app.app.layout.has_focus(app.plot_content)),
            ),
            ConditionalContainer(
                Label("x → Select x-axis"),
                filter=Condition(
                    lambda: "x" not in app.scatter_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("y → Select y-axis"),
                filter=Condition(
                    lambda: "y" not in app.scatter_plotter.plot_params
                ),
            ),
            ConditionalContainer(
                Label("p → Plot"),
                Condition(lambda: len(app.scatter_plotter) > 0),
            ),
            ConditionalContainer(
                Label("P → Save Plot"),
                Condition(lambda: len(app.scatter_plotter) > 0),
            ),
            Label("r → Reset"),
            ConditionalContainer(
                Label("q → Exit Plotting Mode"),
                Condition(
                    lambda: not app.app.layout.has_focus(app.plot_content)
                ),
            ),
            ConditionalContainer(
                Label("q → Exit Config"),
                Condition(lambda: app.app.layout.has_focus(app.plot_content)),
            ),
        ]
    )

    return hot_keys
