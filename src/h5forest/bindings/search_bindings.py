"""This module contains the keybindings for the search mode.

The search mode is a mode that allows the user to search through the HDF5 tree
using fuzzy matching. As the user types, the tree is filtered in real-time to
show only matching nodes and their parents.

This module defines the functions for binding search mode events to functions.
This should not be used directly, but instead provides the functions for the
application.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_search_bindings(app):
    """Set up the keybindings for the search mode."""

    @error_handler
    def exit_search_mode(event):
        """
        Cancel search and restore the original tree.

        Returns to normal mode with the original tree displayed.
        """
        # Restore the original tree
        app.tree.restore_tree()

        # Rebuild tree text from current tree state
        tree_text = app.tree.get_tree_text()

        # Return to normal mode BEFORE clearing buffer
        app.return_to_normal_mode()

        # Clear the search buffer (safe now that we're not in search mode)
        app.search_content.text = ""

        # Update the tree display with rebuilt tree text
        app.tree_buffer.set_document(
            Document(text=tree_text, cursor_position=0),
            bypass_readonly=True,
        )

        # Shift focus back to the tree
        app.shift_focus(app.tree_content)

        # Invalidate to refresh display
        event.app.invalidate()

    @error_handler
    def accept_search_results(event):
        """
        Accept search results and return to normal mode.

        Keeps the filtered tree visible and returns to normal mode,
        allowing all other modes (d, g, w, p, H) to work on the
        filtered results.
        """
        # Return to normal mode BEFORE clearing buffer
        # This prevents the text change handler from restoring the tree
        app.return_to_normal_mode()

        # Clear the search buffer (safe now that we're not in search mode)
        app.search_content.text = ""

        # Shift focus to the tree content (keeping filtered view)
        app.shift_focus(app.tree_content)

        # Update tree buffer to reflect current position
        app.tree_buffer.set_document(
            app.tree_buffer.document,
            bypass_readonly=True,
        )

        # Invalidate to refresh display
        event.app.invalidate()

    # Bind the keys
    app.kb.add("escape", filter=Condition(lambda: app.flag_search_mode))(
        exit_search_mode
    )

    app.kb.add("c-c", filter=Condition(lambda: app.flag_search_mode))(
        exit_search_mode
    )

    app.kb.add("enter", filter=Condition(lambda: app.flag_search_mode))(
        accept_search_results
    )

    # Return all hot keys as a list
    # No conditional labels in search mode
    hot_keys = [
        Label("Enter → Accept"),
        Label("Esc → Cancel"),
    ]

    return hot_keys
