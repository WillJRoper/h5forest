"""A module containing the keybindings for the help mode.

This module contains the keybindings for the help mode. This mode is
activated when the user presses '?' to view the help screen. The help
mode allows the user to navigate through help documentation with vim-style
keybindings. The functions in this module should not be called directly,
but are intended to be used by the main application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_help_bindings(app):
    """Set up the keybindings for the help mode."""

    @error_handler
    def toggle_help(event):
        """Toggle the help screen visibility."""
        app.flag_help_visible = not app.flag_help_visible
        if app.flag_help_visible:
            app._flag_normal_mode = False
            app._flag_help_mode = True
            app.mode_title.update_title("Help Mode")
            app.shift_focus(app.help_content)
        else:
            app._flag_normal_mode = True
            app._flag_help_mode = False
            app.mode_title.update_title("Normal Mode")
            app.default_focus()
        app.update_hotkeys_panel()
        event.app.invalidate()

    @error_handler
    def close_help(event):
        """Close the help screen."""
        app.flag_help_visible = False
        app._flag_normal_mode = True
        app._flag_help_mode = False
        app.mode_title.update_title("Normal Mode")
        app.default_focus()
        app.update_hotkeys_panel()
        event.app.invalidate()

    @error_handler
    def help_move_up(event):
        """Move up in help screen (vim k)."""
        event.app.key_processor.feed(KeyPress(Keys.Up))

    @error_handler
    def help_move_down(event):
        """Move down in help screen (vim j)."""
        event.app.key_processor.feed(KeyPress(Keys.Down))

    # Bind '?' to toggle help screen
    app.kb.add(
        "?",
        filter=Condition(lambda: app.flag_normal_mode or app.flag_help_visible),
    )(toggle_help)

    # Bind 'q' to close help when help is visible
    app.kb.add("q", filter=Condition(lambda: app.flag_help_visible))(close_help)

    # Bind navigation keys for help mode
    app.kb.add("j", filter=Condition(lambda: app.flag_help_mode))(
        help_move_down
    )
    app.kb.add("k", filter=Condition(lambda: app.flag_help_mode))(help_move_up)
    app.kb.add("down", filter=Condition(lambda: app.flag_help_mode))(
        help_move_down
    )
    app.kb.add("up", filter=Condition(lambda: app.flag_help_mode))(help_move_up)

    # Return all possible hot keys as a list
    # The app will use property methods to display these based on mode state
    hot_keys = [
        Label("j/k or ↓/↑ → Navigate"),
        Label("q → Exit Help"),
    ]

    return hot_keys
