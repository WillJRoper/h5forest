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
    def restore_filtered_tree(event):
        """Restore the original tree when viewing filtered search results."""
        # Clear any saved filtering state
        app.tree.original_tree_text = None
        app.tree.original_tree_text_split = None
        app.tree.original_nodes_by_row = None
        app.tree.filtered_node_rows = []

        # Reset the flag
        app.flag_tree_filtered = False

        # Restore to the initial tree state (as when app first opened)
        app.tree_buffer.set_document(
            Document(text=app.initial_tree_text, cursor_position=0),
            bypass_readonly=True,
        )

        # Update tree state to match
        app.tree.tree_text = app.initial_tree_text
        app.tree.tree_text_split = app.initial_tree_text.split("\n")

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

    # Bind Esc to restore original tree when viewing filtered results
    app.kb.add(
        "escape",
        filter=Condition(lambda: app.flag_normal_mode and app.flag_tree_filtered),
    )(restore_filtered_tree)

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
        ConditionalContainer(
            Label("Esc → Restore Tree"),
            filter=Condition(lambda: app.flag_tree_filtered),
        ),
        Label("q → Exit"),
    ]

    return hot_keys
