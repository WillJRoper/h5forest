"""A submodule defining the window mode functions for H5Forest bindings.

This module contains the functions for binding to window events. These include
moving focus between different panes in the application window, such as the
tree, attributes, values, and plot areas.
"""

from h5forest.errors import error_handler


@error_handler
def move_tree(event):
    """Move focus to the tree."""
    app = event.app
    app.shift_focus(app.tree_content)
    app.return_to_normal_mode()


@error_handler
def move_attr(event):
    """Move focus to the attributes."""
    app = event.app
    app.shift_focus(app.attributes_content)
    app.return_to_normal_mode()


@error_handler
def move_values(event):
    """Move focus to values."""
    app = event.app
    app.shift_focus(app.values_content)
    app.return_to_normal_mode()


@error_handler
def move_plot(event):
    """Move focus to the plot."""
    app = event.app
    app.shift_focus(app.plot_content)

    # Plotting is special case where we also want to enter plotting
    # mode
    app._flag_normal_mode = False
    app._flag_window_mode = False
    app._flag_plotting_mode = True


@error_handler
def move_hist(event):
    """Move focus to the plot."""
    app = event.app
    app.shift_focus(app.hist_content)

    # Plotting is special case where we also want to enter plotting
    # mode
    app._flag_normal_mode = False
    app._flag_window_mode = False
    app._flag_hist_mode = True
