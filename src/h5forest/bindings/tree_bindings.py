"""A module containing the keybindings for the file tree.

This module contains the keybinding functions for the file tree. The functions
in this module should not be called directly, but are intended to be used by
the application.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Label

from h5forest.config import translate_key_label
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
    # Get navigation keys from config early (needed for bindings below)
    jump_up_key = app.config.get_keymap("tree_navigation", "jump_up_10")
    jump_down_key = app.config.get_keymap("tree_navigation", "jump_down_10")
    expand_collapse_key = app.config.get_keymap(
        "tree_navigation",
        "expand/collapse",
    )

    # Bind jump keys
    app.kb.add(
        jump_up_key,
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_up_ten)
    app.kb.add(
        jump_down_key,
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_down_ten)

    app.kb.add(
        expand_collapse_key,
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(expand_collapse_node)

    # Get other navigation keys from config
    move_up_key = app.config.get_keymap("tree_navigation", "move_up")
    move_down_key = app.config.get_keymap("tree_navigation", "move_down")
    move_left_key = app.config.get_keymap("tree_navigation", "move_left")
    move_right_key = app.config.get_keymap("tree_navigation", "move_right")

    # Bind navigation keys (respecting vim_mode for hjkl)
    # Only bind vim navigation if vim mode is enabled
    if app.config.is_vim_mode_enabled():
        app.kb.add("h", filter=Condition(lambda: not app.flag_search_mode))(
            move_left
        )
        app.kb.add("j", filter=Condition(lambda: not app.flag_search_mode))(
            move_down
        )
        app.kb.add("k", filter=Condition(lambda: not app.flag_search_mode))(
            move_up
        )
        app.kb.add("l", filter=Condition(lambda: not app.flag_search_mode))(
            move_right
        )

    # If the normal movement keys are just up/down/left/right, we don't
    # need to bind them again, otherwise we do
    if move_up_key not in ["k", "up"]:
        app.kb.add(
            move_up_key,
            filter=Condition(lambda: not app.flag_search_mode),
        )(move_up)
    if move_down_key not in ["j", "down"]:
        app.kb.add(
            move_down_key,
            filter=Condition(lambda: not app.flag_search_mode),
        )(move_down)
    if move_left_key not in ["h", "left"]:
        app.kb.add(
            move_left_key,
            filter=Condition(lambda: not app.flag_search_mode),
        )(move_left)
    if move_right_key not in ["l", "right"]:
        app.kb.add(
            move_right_key,
            filter=Condition(lambda: not app.flag_search_mode),
        )(move_right)

    # Return all possible hot keys as a dict
    # The app will use property methods to filter based on state
    hot_keys = {
        "open_group": Label(
            f"{translate_key_label(expand_collapse_key)} → Open/Close Group"
        ),
        "move_ten": Label(
            f"{translate_key_label(jump_up_key)}/"
            f"{translate_key_label(jump_down_key)} → Up/Down 10 Lines"
        ),
    }

    return hot_keys
