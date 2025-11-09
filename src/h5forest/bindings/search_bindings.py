"""This module contains the keybindings for the search mode.

The search mode is a mode that allows the user to search through the HDF5 tree
using fuzzy matching. As the user types, the tree is filtered in real-time to
show only matching nodes and their parents.

This module defines the functions for binding search mode events to functions.
This should not be used directly, but instead provides the functions for the
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import VSplit
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_search_bindings(app):
    """Set up the keybindings for the search mode."""

    @error_handler
    def exit_search_mode(event):
        """Exit search mode and restore the original tree."""
        # Restore the original tree
        app.tree.restore_tree()

        # Clear the search buffer
        app.search_content.text = ""

        # Return to normal mode
        app.return_to_normal_mode()

        # Shift focus back to the tree
        app.shift_focus(app.tree_content)

        # Invalidate to refresh display
        event.app.invalidate()

    @error_handler
    def accept_search(event):
        """Accept search and keep filtered tree, jump to first match."""
        # If there are matches, jump to the first one
        if app.tree.filtered_node_rows:
            # Get the first match (after restoring we'd lose this info)
            first_match_row = app.tree.filtered_node_rows[0]

            # Restore tree first
            app.tree.restore_tree()

            # Calculate cursor position for the first match
            cursor_pos = sum(
                len(line) + 1
                for line in app.tree.tree_text_split[:first_match_row]
            )

            # Jump to it
            app.set_cursor_position(app.tree.tree_text, cursor_pos)
        else:
            # No matches, just restore
            app.tree.restore_tree()

        # Clear the search buffer
        app.search_content.text = ""

        # Return to normal mode
        app.return_to_normal_mode()

        # Shift focus back to the tree
        app.shift_focus(app.tree_content)

        # Invalidate to refresh display
        event.app.invalidate()

    # Bind the keys
    app.kb.add(
        "escape", filter=Condition(lambda: app.flag_search_mode)
    )(exit_search_mode)

    app.kb.add(
        "c-c", filter=Condition(lambda: app.flag_search_mode)
    )(exit_search_mode)

    app.kb.add(
        "enter", filter=Condition(lambda: app.flag_search_mode)
    )(accept_search)

    # Create hot keys display
    hot_keys = VSplit(
        [
            Label("Enter → Accept"),
            Label("Esc → Cancel"),
        ]
    )

    return hot_keys
