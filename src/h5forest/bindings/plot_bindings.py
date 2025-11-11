"""This module contains the keybindings for the plotting mode.

The functions in this module are used to define the keybindings for the
plotting mode and attach them to the application. It should not be used
directly.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.config import translate_key_label
from h5forest.dataset_prompts import prompt_for_chunking_preference
from h5forest.errors import error_handler
from h5forest.utils import WaitIndicator


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

        # Set x-axis directly (data loads asynchronously in background)
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

        # Set y-axis directly (data loads asynchronously in background)
        app.plot_content.text = app.scatter_plotter.set_y_key(node)

    @error_handler
    def toggle_x_scale(event):
        """Toggle the x-axis scale between linear and log."""
        # Wait for x-axis data assignment thread to finish if it's running
        if app.scatter_plotter.assignx_thread is not None:
            with WaitIndicator(app, "Computing x-axis data range..."):
                app.scatter_plotter.assignx_thread.join()
            app.scatter_plotter.assignx_thread = None

        # Check if x_min/x_max are available
        if (
            app.scatter_plotter.x_min is None
            or app.scatter_plotter.x_max is None
        ):
            app.print(
                "Cannot toggle x-scale: x-axis data range not yet computed. "
                "Please select x-axis dataset first (x)"
            )
            return

        # Get the current text
        split_text = app.plot_content.text.split("\n")

        # Get the current x-scale (it's on line 4)
        current_scale = split_text[4].split(": ")[1].strip()

        # Toggle the scale
        new_scale = "log" if current_scale == "linear" else "linear"

        # If toggling to log, validate data is compatible
        if new_scale == "log":
            if app.scatter_plotter.x_min <= 0:
                value_type = (
                    "zero" if app.scatter_plotter.x_min == 0 else "negative"
                )
                app.print(
                    f"Cannot use log scale on x-axis: data contains "
                    f"{value_type} values "
                    f"(min = {app.scatter_plotter.x_min})"
                )
                return

        split_text[4] = f"x-scale:     {new_scale}"

        # Update the text
        app.plot_content.text = "\n".join(split_text)
        app.scatter_plotter.plot_text = app.plot_content.text

        app.app.invalidate()

    @error_handler
    def toggle_y_scale(event):
        """Toggle the y-axis scale between linear and log."""
        # Wait for y-axis data assignment thread to finish if it's running
        if app.scatter_plotter.assigny_thread is not None:
            with WaitIndicator(app, "Computing y-axis data range..."):
                app.scatter_plotter.assigny_thread.join()
            app.scatter_plotter.assigny_thread = None

        # Check if y_min/y_max are available
        if (
            app.scatter_plotter.y_min is None
            or app.scatter_plotter.y_max is None
        ):
            app.print(
                "Cannot toggle y-scale: y-axis data range not yet computed. "
                "Please select y-axis dataset first (y)"
            )
            return

        # Get the current text
        split_text = app.plot_content.text.split("\n")

        # Get the current y-scale (it's on line 5)
        current_scale = split_text[5].split(": ")[1].strip()

        # Toggle the scale
        new_scale = "log" if current_scale == "linear" else "linear"

        # If toggling to log, validate data is compatible
        if new_scale == "log":
            if app.scatter_plotter.y_min <= 0:
                value_type = (
                    "zero" if app.scatter_plotter.y_min == 0 else "negative"
                )
                app.print(
                    f"Cannot use log scale on y-axis: data contains "
                    f"{value_type} values "
                    f"(min = {app.scatter_plotter.y_min})"
                )
                return

        split_text[5] = f"y-scale:     {new_scale}"

        # Update the text
        app.plot_content.text = "\n".join(split_text)
        app.scatter_plotter.plot_text = app.plot_content.text

        app.app.invalidate()

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
        """Plot and show scatter with mean in bins."""
        # Check if we have both x and y datasets selected
        if (
            "x" not in app.scatter_plotter.plot_params
            or "y" not in app.scatter_plotter.plot_params
        ):
            msg = "Please select both x-axis (x) and y-axis (y) datasets first"
            app.print(msg)
            return

        def do_plot(use_chunks):
            """Actually perform the plot after chunking preference is set."""
            # Make the plot with wait indicator
            with WaitIndicator(app, "Generating scatter plot..."):
                app.scatter_plotter.plot_and_show(
                    app.plot_content.text, use_chunks=use_chunks
                )

            app.default_focus()

        # Get the nodes to check for chunking
        nodes = [
            app.scatter_plotter.plot_params["x"],
            app.scatter_plotter.plot_params["y"],
        ]

        # Prompt for chunking preference if needed, then plot
        prompt_for_chunking_preference(app, nodes, do_plot)

    @error_handler
    def save_scatter(event):
        """Save the plot."""
        # Check if we have both x and y datasets selected
        if (
            "x" not in app.scatter_plotter.plot_params
            or "y" not in app.scatter_plotter.plot_params
        ):
            msg = "Please select both x-axis (x) and y-axis (y) datasets first"
            app.print(msg)
            return

        def do_save(use_chunks):
            """Actually save the plot after chunking preference is set."""
            app.scatter_plotter.plot_and_save(
                app.plot_content.text, use_chunks=use_chunks
            )

        # Get the nodes to check for chunking
        nodes = [
            app.scatter_plotter.plot_params["x"],
            app.scatter_plotter.plot_params["y"],
        ]

        # Prompt for chunking preference if needed, then save
        prompt_for_chunking_preference(app, nodes, do_save)

    @error_handler
    def reset(event):
        """Reset the plot content."""
        app.scatter_plotter.close()
        app.plot_content.text = app.scatter_plotter.reset()

        app.app.invalidate()
        app.default_focus()

    @error_handler
    def edit_plot(event):
        """Edit the plot configuration."""
        if app.app.layout.has_focus(app.plot_content):
            # Already in config, jump back to tree
            app.shift_focus(app.tree_content)
        else:
            # In tree, jump to config
            app.shift_focus(app.plot_content)

    def exit_edit_plot(event):
        """Exit edit plot mode."""
        app.shift_focus(app.tree_content)

    # Get the keybindings from config
    edit_key = app.config.get_keymap("plot_mode", "edit_config")
    edit_entry_key = app.config.get_keymap("plot_mode", "edit_entry")
    select_x_key = app.config.get_keymap("plot_mode", "select_x")
    select_y_key = app.config.get_keymap("plot_mode", "select_y")
    toggle_x_scale_key = app.config.get_keymap("plot_mode", "toggle_x_scale")
    toggle_y_scale_key = app.config.get_keymap("plot_mode", "toggle_y_scale")
    reset_key = app.config.get_keymap("plot_mode", "reset")
    show_plot_key = app.config.get_keymap("plot_mode", "show_plot")
    save_plot_key = app.config.get_keymap("plot_mode", "save_plot")
    quit_key = app.config.get_keymap("normal_mode", "quit")

    # Bind the functions
    app.kb.add(edit_key, filter=Condition(lambda: app.flag_plotting_mode))(
        edit_plot
    )
    app.kb.add(select_x_key, filter=Condition(lambda: app.flag_plotting_mode))(
        select_x
    )
    app.kb.add(
        toggle_x_scale_key, filter=Condition(lambda: app.flag_plotting_mode)
    )(toggle_x_scale)
    app.kb.add(select_y_key, filter=Condition(lambda: app.flag_plotting_mode))(
        select_y
    )
    app.kb.add(
        toggle_y_scale_key, filter=Condition(lambda: app.flag_plotting_mode)
    )(toggle_y_scale)
    app.kb.add(
        edit_entry_key,
        filter=Condition(lambda: app.app.layout.has_focus(app.plot_content)),
    )(edit_plot_entry)
    app.kb.add(
        show_plot_key, filter=Condition(lambda: app.flag_plotting_mode)
    )(plot_scatter)
    app.kb.add(
        save_plot_key, filter=Condition(lambda: app.flag_plotting_mode)
    )(save_scatter)
    app.kb.add(reset_key, filter=Condition(lambda: app.flag_plotting_mode))(
        reset
    )
    app.kb.add(
        quit_key,
        filter=Condition(lambda: app.app.layout.has_focus(app.plot_content)),
    )(exit_edit_plot)

    # Return all possible hot keys as a dict
    # The app will use property methods to filter based on state
    hot_keys = {
        "edit_config": Label(
            f"{translate_key_label(edit_key)} → Edit Plot Config"
        ),
        "edit_tree": Label(f"{translate_key_label(edit_key)} → Back to Tree"),
        "edit_entry": Label(
            f"{translate_key_label(edit_entry_key)} → Edit Entry"
        ),
        "select_x": Label(
            f"{translate_key_label(select_x_key)} → Select x-axis"
        ),
        "select_y": Label(
            f"{translate_key_label(select_y_key)} → Select y-axis"
        ),
        "toggle_x_scale": Label(
            f"{translate_key_label(toggle_x_scale_key)} → Toggle x-scale"
        ),
        "toggle_y_scale": Label(
            f"{translate_key_label(toggle_y_scale_key)} → Toggle y-scale"
        ),
        "plot": Label(f"{translate_key_label(show_plot_key)} → Show Plot"),
        "save_plot": Label(
            f"{translate_key_label(save_plot_key)} → Save Plot"
        ),
        "reset": Label(
            f"{translate_key_label(reset_key)} → Reset Plot Config"
        ),
        "exit_mode": Label(
            f"{translate_key_label(quit_key)} → Exit Plot Mode"
        ),
        "exit_config": Label(
            f"{translate_key_label(quit_key)} → Exit Config Edit"
        ),
    }

    return hot_keys
