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
        """
        Cancel search and restore the original tree.

        Returns to normal mode with the original tree displayed.
        """
        # Restore the original tree
        app.tree.restore_tree()

        # Clear the search buffer
        app.search_content.text = ""

        # Reset flags
        app.flag_tree_filtered = False
        app.return_to_normal_mode()

        # Update the tree display
        app.tree_buffer.set_document(
            app.tree_buffer.document,
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
        allowing all other modes (d, g, w, p, H) to work on the filtered results.
        """
        # Set flag that tree contains filtered results
        app.flag_tree_filtered = True

        # Clear the search buffer
        app.search_content.text = ""

        # Return to normal mode
        app.return_to_normal_mode()

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
    app.kb.add(
        "escape", filter=Condition(lambda: app.flag_search_mode)
    )(exit_search_mode)

    app.kb.add(
        "c-c", filter=Condition(lambda: app.flag_search_mode)
    )(exit_search_mode)

    app.kb.add(
        "enter", filter=Condition(lambda: app.flag_search_mode)
    )(accept_search_results)

    # Create hot keys display
    hot_keys = VSplit(
        [
            Label("Enter → Accept"),
            Label("Esc → Cancel"),
        ]
    )

    return hot_keys
