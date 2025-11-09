"""This module contains the keybindings for the goto mode.

The goto mode is a mode that allows the user to quickly navigate the tree using
a set of keybindings. This is useful for large trees where the user knows the
name of the node they want to go to.
This module defines the functions for binding goto mode events to functions.
This should not be used directly, but instead provides the functions for the
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_goto_bindings(app):
    """Set up the keybindings for the goto mode."""

    @error_handler
    def goto_top(event):
        """Go to the top of the tree (vim gg)."""
        app.set_cursor_position(app.tree.tree_text, new_cursor_pos=0)

        # Exit goto mode
        app.return_to_normal_mode()

    @error_handler
    def goto_bottom(event):
        """Go to the bottom of the tree."""
        app.set_cursor_position(
            app.tree.tree_text, new_cursor_pos=app.tree.length
        )

        # Exit goto mode
        app.return_to_normal_mode()

    @error_handler
    def goto_parent(event):
        """Go to the parent of the current node."""
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
        """Go to the next node."""
        # Get the current node
        node = app.tree.get_current_node(app.current_row)

        # Get the depth of this node and the target depth
        depth = node.depth
        target_depth = depth - 1 if depth > 0 else 0

        # Get the position of the first character in this row
        pos = app.current_position - app.current_column

        # Do nothing if we are at the end
        if app.current_row == app.tree.height - 1:
            app.return_to_normal_mode()
            return

        # Loop forwards until we hit the next node at the level above
        # this node's depth. If at the root just move to the next
        # root group.
        found_next = False
        for row in range(app.current_row, app.tree.height):
            # Compute the position at this row
            pos += len(app.tree.tree_text_split[row]) + 1

            # Ensure we don't over shoot
            if row + 1 >= app.tree.height:
                break

            # If we are at the next node stop
            if app.tree.get_current_node(row + 1).depth == target_depth:
                found_next = True
                break

        if found_next:
            # Move the cursor
            app.set_cursor_position(app.tree.tree_text, pos)
        else:
            app.print("Next Group can't be found")

        app.return_to_normal_mode()

    @error_handler
    def jump_to_key(event):
        """Jump to next key containing user input."""

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

    # Bind the functions
    app.kb.add("t", filter=Condition(lambda: app.flag_jump_mode))(goto_top)
    app.kb.add("g", filter=Condition(lambda: app.flag_jump_mode))(goto_top)
    app.kb.add("b", filter=Condition(lambda: app.flag_jump_mode))(goto_bottom)
    app.kb.add("G", filter=Condition(lambda: app.flag_jump_mode))(goto_bottom)
    app.kb.add("p", filter=Condition(lambda: app.flag_jump_mode))(goto_parent)
    app.kb.add("n", filter=Condition(lambda: app.flag_jump_mode))(goto_next)
    app.kb.add("K", filter=Condition(lambda: app.flag_jump_mode))(jump_to_key)

    # Return all hot keys as a list
    # No conditional labels in jump mode
    hot_keys = [
        Label("t/g → Go to Top"),
        Label("b/G → Go to Bottom"),
        Label("p → Go to Parent"),
        Label("n → Next Parent Group"),
        Label("K → Jump to Key Containing"),
        Label("q → Exit Goto Mode"),
    ]

    return hot_keys
