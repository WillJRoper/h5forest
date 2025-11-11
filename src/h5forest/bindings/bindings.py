"""A module containing the keybindings for the basic UI.

This module contains the keybindings for the basic UI. These keybindings are
always active and are not dependent on any leader key. The functions in this
module should not be called directly, but are intended to be used by the main
application.
"""

import platform
import subprocess
import threading

from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.config import translate_key_label
from h5forest.errors import error_handler
from h5forest.utils import WaitIndicator


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
        app.mode_title.update_title("Goto Mode")

    def dataset_leader_mode(event):
        """Enter dataset mode."""
        app._flag_normal_mode = False
        app._flag_dataset_mode = True
        app.mode_title.update_title("Dataset Mode")

    def window_leader_mode(event):
        """Enter window mode."""
        app._flag_normal_mode = False
        app._flag_window_mode = True
        app.mode_title.update_title("Window Mode")

    def plotting_leader_mode(event):
        """Enter plotting mode."""
        app._flag_normal_mode = False
        app._flag_plotting_mode = True
        app.mode_title.update_title("Plotting Mode")

    def hist_leader_mode(event):
        """Enter hist mode."""
        app._flag_normal_mode = False
        app._flag_hist_mode = True
        app.mode_title.update_title("Histogram Mode")

    @error_handler
    def exit_leader_mode(event):
        """Exit leader mode."""
        app.return_to_normal_mode()
        app.default_focus()
        event.app.invalidate()

    def expand_attributes(event):
        """Expand the attributes."""
        app.flag_expanded_attrs = True
        app.update_hotkeys_panel()
        event.app.invalidate()

    def collapse_attributes(event):
        """Collapse the attributes."""
        app.flag_expanded_attrs = False
        app.update_hotkeys_panel()
        event.app.invalidate()

    def search_leader_mode(event):
        """Enter search mode."""

        app._flag_normal_mode = False
        app._flag_search_mode = True
        app.mode_title.update_title("Search Mode")
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
                    from prompt_toolkit.document import Document

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
            thread = threading.Thread(
                target=monitor_index_building, daemon=True
            )
            thread.start()

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

    @error_handler
    def copy_key(event):
        """Copy the HDF5 key of the current node to the clipboard."""
        # Get the current node
        node = app.tree.get_current_node(app.current_row)

        # Get the HDF5 key path (without filename and leading slashes)
        hdf5_key = node.path.lstrip("/")

        # Copy to clipboard using platform-specific command
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ["pbcopy"],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            elif system == "Windows":
                process = subprocess.Popen(
                    ["clip"],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            else:  # Linux and others
                process = subprocess.Popen(
                    ["xclip", "-selection", "clipboard"],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            # Write the path to clipboard
            process.communicate(input=hdf5_key.encode("utf-8"))

            if process.returncode == 0:
                app.print(f"Copied {hdf5_key} into the clipboard")
            else:
                app.print("Error: Failed to copy to clipboard")

        except FileNotFoundError:
            # Clipboard tool not found
            if system == "Linux":
                app.print(
                    "Error: xclip not found. Install with: apt install xclip"
                )
            else:
                app.print("Error: Clipboard tool not available")
        except Exception as e:
            app.print(f"Error copying to clipboard: {e}")

        event.app.invalidate()

    # Get keybindings from config
    quit_key = app.config.get_keymap("normal_mode", "quit")
    copy_key_binding = app.config.get_keymap("normal_mode", "copy_path")
    toggle_attrs_key = app.config.get_keymap(
        "normal_mode", "expand_attributes"
    )
    restore_key = app.config.get_keymap("normal_mode", "restore_tree")

    # Leader keys for different modes
    goto_leader = app.config.get_keymap("jump_mode", "leader")
    dataset_leader = app.config.get_keymap("dataset_mode", "leader")
    window_leader = app.config.get_keymap("window_mode", "leader")
    plot_leader = app.config.get_keymap("plot_mode", "leader")
    hist_leader = app.config.get_keymap("hist_mode", "leader")
    search_leader = app.config.get_keymap("search_mode", "leader")

    # Bind the functions
    app.kb.add(quit_key, filter=Condition(lambda: app.flag_normal_mode))(
        exit_app
    )
    app.kb.add("c-q")(exit_app)
    app.kb.add(goto_leader, filter=Condition(lambda: app.flag_normal_mode))(
        goto_leader_mode
    )
    app.kb.add(dataset_leader, filter=Condition(lambda: app.flag_normal_mode))(
        dataset_leader_mode
    )
    app.kb.add(window_leader, filter=Condition(lambda: app.flag_normal_mode))(
        window_leader_mode
    )
    app.kb.add(plot_leader, filter=Condition(lambda: app.flag_normal_mode))(
        plotting_leader_mode
    )
    app.kb.add(hist_leader, filter=Condition(lambda: app.flag_normal_mode))(
        hist_leader_mode
    )
    app.kb.add(quit_key, filter=Condition(lambda: not app.flag_normal_mode))(
        exit_leader_mode
    )
    app.kb.add(
        toggle_attrs_key,
        filter=Condition(
            lambda: app.flag_normal_mode and not app.flag_expanded_attrs
        ),
    )(expand_attributes)
    app.kb.add(
        toggle_attrs_key,
        filter=Condition(
            lambda: app.flag_normal_mode and app.flag_expanded_attrs
        ),
    )(collapse_attributes)

    # Only including the search if the tree has focus
    app.kb.add(
        search_leader,
        filter=Condition(
            lambda: app.flag_normal_mode
            and app.app.layout.has_focus(app.tree_content.content)
        ),
    )(search_leader_mode)

    # Bind 'r' to restore tree to initial state
    app.kb.add(
        restore_key,
        filter=Condition(lambda: app.flag_normal_mode),
    )(restore_tree_to_initial)

    # Bind 'c' to copy the HDF5 key to clipboard
    app.kb.add(
        copy_key_binding,
        filter=Condition(lambda: app.flag_normal_mode),
    )(copy_key)

    # Return all possible hot keys as a dict
    # The app will use property methods to filter based on state
    hot_keys = {
        "expand_attrs": Label(
            f"{translate_key_label(toggle_attrs_key)} → Expand Attributes"
        ),
        "shrink_attrs": Label(
            f"{translate_key_label(toggle_attrs_key)} → Shrink Attributes"
        ),
        "dataset_mode": Label(
            f"{translate_key_label(dataset_leader)} → Dataset Mode"
        ),
        "goto_mode": Label(f"{translate_key_label(goto_leader)} → Goto Mode"),
        "hist_mode": Label(
            f"{translate_key_label(hist_leader)} → Histogram Mode"
        ),
        "plotting_mode": Label(
            f"{translate_key_label(plot_leader)} → Plotting Mode"
        ),
        "window_mode": Label(
            f"{translate_key_label(window_leader)} → Window Mode"
        ),
        "search": Label(f"{translate_key_label(search_leader)} → Search"),
        "restore_tree": Label(
            f"{translate_key_label(restore_key)} → Restore Tree"
        ),
        "copy_key": Label(
            f"{translate_key_label(copy_key_binding)} → Copy Key"
        ),
        "exit": Label(f"{translate_key_label(quit_key)} → Exit"),
    }

    return hot_keys
