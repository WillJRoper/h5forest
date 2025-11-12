"""This submodule defines the functions for goto mode in H5Forest.

The goto mode is a mode that allows the user to quickly navigate the tree using
a set of keybindings. This is useful for large trees where the user knows the
name of the node they want to go to.
This module defines the functions for binding goto mode events to functions.
This should not be used directly, but instead provides the functions for the
application.
"""

from h5forest.errors import error_handler


@error_handler
def goto_top(event):
    """Go to the top of the tree (vim gg)."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Move to the top
    app.set_cursor_position(app.tree.tree_text, new_cursor_pos=0)

    # Exit goto mode
    app.return_to_normal_mode()


@error_handler
def goto_bottom(event):
    """Go to the bottom of the tree."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Move to the end
    app.set_cursor_position(app.tree.tree_text, new_cursor_pos=app.tree.length)

    # Exit goto mode
    app.return_to_normal_mode()


@error_handler
def goto_parent(event):
    """Go to the parent of the current node."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the current node
    node = app.tree.get_current_node(app.current_row)

    # Get the node's parent
    parent = node.parent

    # if we're at the top, do nothing
    if parent is None:
        app.print(f"{node.path} is a root Group!")
        app.return_to_normal_mode()
        return

    # Get position of the first character in this row
    pos = app.current_position - app.current_column

    # Loop backwards until we hit the parent
    for row in range(app.current_row - 1, -1, -1):
        # Compute the position at this row
        pos -= len(app.tree.tree_text_split[row]) + 1

        # If we are at the parent stop
        if app.tree.get_current_node(row) is parent:
            break

    # Safety check, avoid doing something stupid
    if pos < 0:
        pos = 0

    # Move the cursor
    app.set_cursor_position(app.tree.tree_text, pos)

    app.return_to_normal_mode()


@error_handler
def goto_next(event):
    """Go to the next sibling node at the same depth level."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the current node
    current_node = app.tree.get_current_node(app.current_row)
    current_depth = current_node.depth

    # Get the position of the first character in this row
    pos = app.current_position - app.current_column

    # Loop forward to find next sibling (node at same or lower depth)
    for row in range(app.current_row + 1, app.tree.height):
        # Compute the position at this row
        pos += len(app.tree.tree_text_split[row - 1]) + 1

        # Get the node at this row
        node = app.tree.get_current_node(row)

        # If we found a node at lower or equal depth, we found a sibling
        if node.depth <= current_depth:
            app.set_cursor_position(app.tree.tree_text, pos)
            app.return_to_normal_mode()
            return

    # If we got here, we're at the end of the tree or couldn't find a sibling
    if app.current_row == app.tree.height - 1:
        # At end of tree, just exit
        app.return_to_normal_mode()
    else:
        # Couldn't find a sibling (all remaining are children)
        app.print("Next Group can't be found")
        app.return_to_normal_mode()


@error_handler
def jump_to_key(event):
    """Jump to next key containing user input."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    def jump_to_key_callback():
        """Jump to next key containing user input."""
        # Unpack user input
        key = app.user_input.strip()

        # Get the position of the first character in this row
        pos = app.current_position - app.current_column

        # Loop over keys until we find a key containing the
        # user input
        for row in range(app.current_row, app.tree.height):
            # Compute the position at this row
            pos += len(app.tree.tree_text_split[row]) + 1

            # Ensure we don't over shoot
            if row + 1 > app.tree.height - 1:
                app.print("Couldn't find matching key!")
                app.default_focus()
                app.return_to_normal_mode()
                return

            # If we are at the next node stop
            if key in app.tree.get_current_node(row + 1).name:
                break

        # Return to normal
        app.default_focus()
        app.return_to_normal_mode()

        # Move the cursor
        app.set_cursor_position(app.tree.tree_text, pos)

    # Get the search string from the user
    app.input(
        "Jump to next key containing:",
        jump_to_key_callback,
    )
