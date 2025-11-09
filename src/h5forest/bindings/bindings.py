"""A module containing the keybindings for the basic UI.

This module contains the keybindings for the basic UI. These keybindings are
always active and are not dependent on any leader key. The functions in this
module should not be called directly, but are intended to be used by the main
application.
"""

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_app_bindings(app):
    """
    Set up the keybindings for the basic UI.

    This includes basic closing functionality and leader keys for different
    modes. These are always active and are not dependent on any leader key.
    """

    def exit_app(event):
        """Exit the app."""
        event.app.exit()

    def goto_leader_mode(event):
        """Enter goto mode."""
        app._flag_normal_mode = False
        app._flag_jump_mode = True

    def dataset_leader_mode(event):
        """Enter dataset mode."""
        app._flag_normal_mode = False
        app._flag_dataset_mode = True

    def window_leader_mode(event):
        """Enter window mode."""
        app._flag_normal_mode = False
        app._flag_window_mode = True

    def plotting_leader_mode(event):
        """Enter plotting mode."""
        app._flag_normal_mode = False
        app._flag_plotting_mode = True

    def hist_leader_mode(event):
        """Enter hist mode."""
        app._flag_normal_mode = False
        app._flag_hist_mode = True

    @error_handler
    def exit_leader_mode(event):
        """Exit leader mode."""
        app.return_to_normal_mode()
        app.default_focus()
        event.app.invalidate()

    def expand_attributes(event):
        """Expand the attributes."""
        app.flag_expanded_attrs = True
        event.app.invalidate()

    def collapse_attributes(event):
        """Collapse the attributes."""
        app.flag_expanded_attrs = False
        event.app.invalidate()

    def search_leader_mode(event):
        """Enter search mode."""
        app._flag_normal_mode = False
        app._flag_search_mode = True
        app.search_content.text = ""
        app.search_content.buffer.cursor_position = 0
        app.shift_focus(app.search_content)
        event.app.invalidate()

    @error_handler
    def restore_tree_to_initial(event):
        """Restore the tree to initial state (as when app was opened)."""
        # Clear any saved filtering state
        app.tree.original_tree_text = None
        app.tree.original_tree_text_split = None
        app.tree.original_nodes_by_row = None
        app.tree.filtered_node_rows = []

        # Close all children of the root to collapse everything
        for child in app.tree.root.children:
            child.close_node()

        # Clear the root's children list
        app.tree.root.children = []

        # Reopen just the root level to restore initial state
        app.tree.root.open_node()

        # Rebuild tree from root - shows tree as when first opened
        tree_text = app.tree.get_tree_text()

        # Update the display
        app.tree_buffer.set_document(
            Document(text=tree_text, cursor_position=0),
            bypass_readonly=True,
        )

        # Invalidate to refresh display
        event.app.invalidate()

    # Bind the functions
    app.kb.add("q", filter=Condition(lambda: app.flag_normal_mode))(exit_app)
    app.kb.add("c-q")(exit_app)
    app.kb.add("g", filter=Condition(lambda: app.flag_normal_mode))(
        goto_leader_mode
    )
    app.kb.add("d", filter=Condition(lambda: app.flag_normal_mode))(
        dataset_leader_mode
    )
    app.kb.add("w", filter=Condition(lambda: app.flag_normal_mode))(
        window_leader_mode
    )
    app.kb.add("p", filter=Condition(lambda: app.flag_normal_mode))(
        plotting_leader_mode
    )
    app.kb.add("H", filter=Condition(lambda: app.flag_normal_mode))(
        hist_leader_mode
    )
    app.kb.add("q", filter=Condition(lambda: not app.flag_normal_mode))(
        exit_leader_mode
    )
    app.kb.add(
        "A",
        filter=Condition(
            lambda: app.flag_normal_mode and not app.flag_expanded_attrs
        ),
    )(expand_attributes)
    app.kb.add(
        "A",
        filter=Condition(
            lambda: app.flag_normal_mode and app.flag_expanded_attrs
        ),
    )(collapse_attributes)

    # Only including the search if the tree has focus
    app.kb.add(
        "s",
        filter=Condition(
            lambda: app.flag_normal_mode
            and app.app.layout.has_focus(app.tree_content.content)
        ),
    )(search_leader_mode)

    # Bind 'r' to restore tree to initial state
    app.kb.add(
        "r",
        filter=Condition(lambda: app.flag_normal_mode),
    )(restore_tree_to_initial)

    # Add the hot keys
    hot_keys = [
        ConditionalContainer(
            Label("A → Expand Attributes"),
            filter=Condition(lambda: not app.flag_expanded_attrs),
        ),
        ConditionalContainer(
            Label("A → Shrink Attributes"),
            filter=Condition(lambda: app.flag_expanded_attrs),
        ),
        Label("d → Dataset Mode"),
        Label("g → Goto Mode"),
        Label("H → Histogram Mode"),
        Label("p → Plotting Mode"),
        Label("w → Window Mode"),
        ConditionalContainer(
            Label("s → Search"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content.content)
            ),
        ),
        Label("r → Restore Tree"),
        Label("q → Exit"),
    ]

    return hot_keys
