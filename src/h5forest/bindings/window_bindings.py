"""A module for binding window events to functions.

This module contains the functions for binding window events to functions. This
should not be used directly, but instead provides the functions for the
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.config import translate_key_label
from h5forest.errors import error_handler


def _init_window_bindings(app):
    """Set up the keybindings for the window mode."""

    @error_handler
    def move_tree(event):
        """Move focus to the tree."""
        app.shift_focus(app.tree_content)
        app.return_to_normal_mode()

    @error_handler
    def move_attr(event):
        """Move focus to the attributes."""
        app.shift_focus(app.attributes_content)
        app.return_to_normal_mode()

    @error_handler
    def move_values(event):
        """Move focus to values."""
        app.shift_focus(app.values_content)
        app.return_to_normal_mode()

    @error_handler
    def move_plot(event):
        """Move focus to the plot."""
        app.shift_focus(app.plot_content)

        # Plotting is special case where we also want to enter plotting
        # mode
        app._flag_normal_mode = False
        app._flag_window_mode = False
        app._flag_plotting_mode = True

    @error_handler
    def move_hist(event):
        """Move focus to the plot."""
        app.shift_focus(app.hist_content)

        # Plotting is special case where we also want to enter plotting
        # mode
        app._flag_normal_mode = False
        app._flag_window_mode = False
        app._flag_hist_mode = True

    @error_handler
    def move_to_default(event):
        """
        Move focus to the default area.

        This is the tree content.
        """
        app.default_focus()
        app.return_to_normal_mode()

    # Get keybindings from config
    tree_key = app.config.get_keymap("window_mode", "focus_tree")
    attr_key = app.config.get_keymap("window_mode", "focus_attributes")
    values_key = app.config.get_keymap("window_mode", "focus_values")
    plot_key = app.config.get_keymap("window_mode", "focus_plot")
    hist_key = app.config.get_keymap("window_mode", "focus_hist")
    quit_key = app.config.get_keymap("normal_mode", "quit")

    # Bind the functions
    app.kb.add(tree_key, filter=Condition(lambda: app.flag_window_mode))(
        move_tree
    )
    app.kb.add(attr_key, filter=Condition(lambda: app.flag_window_mode))(
        move_attr
    )
    app.kb.add(
        values_key,
        filter=Condition(
            lambda: app.flag_window_mode and app.flag_values_visible
        ),
    )(move_values)
    app.kb.add(plot_key, filter=Condition(lambda: app.flag_window_mode))(
        move_plot
    )
    app.kb.add(hist_key, filter=Condition(lambda: app.flag_window_mode))(
        move_hist
    )
    app.kb.add("escape")(move_to_default)

    # Return all possible hot keys as a dict
    # The app will use property methods to filter based on state
    hot_keys = {
        "move_tree": Label(f"{translate_key_label(tree_key)} → Move to Tree"),
        "move_attrs": Label(
            f"{translate_key_label(attr_key)} → Move to Attributes"
        ),
        "move_values": Label(
            f"{translate_key_label(values_key)} → Move to Values"
        ),
        "move_plot": Label(f"{translate_key_label(plot_key)} → Move to Plot"),
        "move_hist": Label(
            f"{translate_key_label(hist_key)} → Move to Histogram"
        ),
        "exit": Label(f"{translate_key_label(quit_key)} → Exit Window Mode"),
    }

    return hot_keys
