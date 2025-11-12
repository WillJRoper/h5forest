"""A module containing the keybindings for the file tree.

This module contains the keybinding functions for the file tree. The functions
in this module should not be called directly, but are intended to be used by
the application.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys

from h5forest.errors import error_handler


@error_handler
def move_up_ten(event):
    """Move up ten lines."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Move up ten lines
    app.tree_buffer.cursor_up(10)


@error_handler
def move_down_ten(event):
    """Move down ten lines."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Move down ten lines
    app.tree_buffer.cursor_down(10)


@error_handler
def move_left(event):
    """Move cursor left (vim h) - works app-wide."""
    event.app.key_processor.feed(KeyPress(Keys.Left))


@error_handler
def move_down(event):
    """Move cursor down (vim j) - works app-wide."""
    event.app.key_processor.feed(KeyPress(Keys.Down))


@error_handler
def move_up(event):
    """Move cursor up (vim k) - works app-wide."""
    event.app.key_processor.feed(KeyPress(Keys.Up))


@error_handler
def move_right(event):
    """Move cursor right (vim l) - works app-wide."""
    event.app.key_processor.feed(KeyPress(Keys.Right))


@error_handler
def expand_collapse_node(event):
    """
    Expand the node under the cursor.

    This uses lazy loading so only the group at the expansion point
    will be loaded.
    """
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the current cursor row and position
    current_row = app.current_row
    current_pos = app.current_position

    # Get the node under the cursor
    node = app.tree.get_current_node(current_row)

    # If we have a dataset just do nothing
    if node.is_dataset:
        app.print(f"{node.path} is not a Group")
        return

    # If the node has no children, do nothing
    if not node.has_children:
        app.print(f"{node.path} has no children")
        return

    # If the node is already open, close it
    if node.is_expanded:
        app.tree_buffer.set_document(
            Document(
                app.tree.close_node(node, current_row),
                cursor_position=current_pos,
            ),
            bypass_readonly=True,
        )
    else:  # Otherwise, open it
        app.tree_buffer.set_document(
            Document(
                app.tree.update_tree_text(node, current_row),
                cursor_position=current_pos,
            ),
            bypass_readonly=True,
        )


def expand_attributes(event):
    """Expand the attributes."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app.flag_expanded_attrs = True
    event.app.invalidate()


def collapse_attributes(event):
    """Collapse the attributes."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app.flag_expanded_attrs = False
    event.app.invalidate()
