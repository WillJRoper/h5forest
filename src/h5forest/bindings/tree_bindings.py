"""A module containing the keybindings for the file tree.

This module contains the keybinding functions for the file tree. The functions
in this module should not be called directly, but are intended to be used by
the application.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_tree_bindings(app):
    """
    Set up the keybindings for the basic UI.

    These are always active and are not dependent on any leader key.
    """

    @error_handler
    def move_up_ten(event):
        """Move up ten lines."""
        app.tree_buffer.cursor_up(10)

    @error_handler
    def move_down_ten(event):
        """Move down ten lines."""
        app.tree_buffer.cursor_down(10)

    @error_handler
    def expand_collapse_node(event):
        """
        Expand the node under the cursor.

        This uses lazy loading so only the group at the expansion point
        will be loaded.
        """
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

    # Bind the functions
    app.kb.add(
        "{",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_up_ten)
    app.kb.add(
        "}",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_down_ten)
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(expand_collapse_node)

    # Add hot keys
    hot_keys = [
        ConditionalContainer(
            Label("Enter → Open Group"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content)
            ),
        ),
        ConditionalContainer(
            Label("{/} → Move Up/Down 10 Lines"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content)
            ),
        ),
    ]

    return hot_keys
