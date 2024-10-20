"""A module containing the keybindings for the basic UI.

This module contains the keybindings for the basic UI. These keybindings are
always active and are not dependent on any leader key. The functions in this
module should not be called directly, but are intended to be used by the main
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label


def _init_app_bindings(app):
    """
    Set up the keybindings for the basic UI.

    This includes basic closing functionality and leader keys for different
    modes. These are always active and are not dependent on any leader key.
    """

    def exit_app(event):
        """Exit the app."""
        event.app.exit()

    def jump_leader_mode(event):
        """Enter jump mode."""
        app._flag_normal_mode = False
        app._flag_jump_mode = True

    def dataset_leader_mode(event):
        """Enter dataset mode."""
        app._flag_normal_mode = False
        app._flag_dataset_mode = True

    def window_leader_mode(event):
        """Enter window mode."""
        app._flag_normal_mode = False
        app._flag_window_mode = True

    def plotting_leader_mode(event):
        """Enter plotting mode."""
        app._flag_normal_mode = False
        app._flag_plotting_mode = True

    def hist_leader_mode(event):
        """Enter hist mode."""
        app._flag_normal_mode = False
        app._flag_hist_mode = True

    @app.error_handler
    def exit_leader_mode(event):
        """Exit leader mode."""
        app.return_to_normal_mode()
        app.default_focus()
        event.app.invalidate()

    # Bind the functions
    app.kb.add("q", filter=Condition(lambda: app.flag_normal_mode))(exit_app)
    app.kb.add("c-q")(exit_app)
    app.kb.add("j", filter=Condition(lambda: app.flag_normal_mode))(
        jump_leader_mode
    )
    app.kb.add("d", filter=Condition(lambda: app.flag_normal_mode))(
        dataset_leader_mode
    )
    app.kb.add("w", filter=Condition(lambda: app.flag_normal_mode))(
        window_leader_mode
    )
    app.kb.add("p", filter=Condition(lambda: app.flag_normal_mode))(
        plotting_leader_mode
    )
    app.kb.add("h", filter=Condition(lambda: app.flag_normal_mode))(
        hist_leader_mode
    )
    app.kb.add("q", filter=Condition(lambda: not app.flag_normal_mode))(
        exit_leader_mode
    )

    # Add the hot keys
    hot_keys = [
        Label("d → Dataset Mode"),
        Label("h → Hist Mode"),
        Label("j → Jump Mode"),
        Label("p → Plotting Mode"),
        Label("w → Window Mode"),
        Label("q → Exit"),
    ]

    return hot_keys
