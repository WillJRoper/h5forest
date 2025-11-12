"""This submodule defining the functions for search mode in H5Forest.

The search mode is a mode that allows the user to search through the HDF5 tree
using fuzzy matching. As the user types, the tree is filtered in real-time to
show only matching nodes and their parents.

This module defines the functions to be bound to search mode events.
This should not be used directly, but instead provides the functions for the
application.
"""

import threading

from prompt_toolkit.document import Document

from h5forest.errors import error_handler
from h5forest.utils import WaitIndicator


@error_handler
def search_leader_mode(event):
    """Enter search mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_search_mode = True
    app.search_content.text = ""
    app.search_content.buffer.cursor_position = 0
    app.shift_focus(app.search_content)

    # Start building the search index in the background
    app.tree.get_all_paths()

    # Show wait indicator while index is building
    def monitor_index_building():
        """Monitor index building and trigger auto-update when done."""
        # Create and start the wait indicator
        indicator = WaitIndicator(app, "Constructing search database...")

        # Only show indicator if index is actually building
        if app.tree.index_building:
            indicator.start()

        # Wait for index building to complete
        if app.tree.unpack_thread:
            app.tree.unpack_thread.join()

        # Stop the indicator
        indicator.stop()

        # If user has already typed a query, trigger search update
        def update_search():
            # Set mini buffer to show "Search:" prompt
            app.print("")

            # Ensure focus is back on search content
            app.shift_focus(app.search_content)

            query = app.search_content.text
            if query:  # Only update if there's a query
                filtered_text = app.tree.filter_tree(query)
                app.tree_buffer.set_document(
                    Document(
                        filtered_text,
                        cursor_position=0,
                    ),
                    bypass_readonly=True,
                )
                app.app.invalidate()

        app.app.loop.call_soon_threadsafe(update_search)

    # Start monitoring in background thread
    if app.tree.index_building:
        thread = threading.Thread(target=monitor_index_building, daemon=True)
        thread.start()

    event.app.invalidate()


@error_handler
def exit_search_mode(event):
    """
    Cancel search and restore the original tree.

    Returns to normal mode with the original tree displayed.
    """
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

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
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

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
