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

from h5forest.bindings.utils import translate_key_label
from h5forest.errors import error_handler
from h5forest.utils import WaitIndicator


def exit_app(event):
    """Exit the app."""
    event.app.exit()


def goto_leader_mode(event):
    """Enter goto mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app._flag_normal_mode = False
    app._flag_jump_mode = True
    app.mode_title.update_title("Goto Mode")


def dataset_leader_mode(event):
    """Enter dataset mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app._flag_normal_mode = False
    app._flag_dataset_mode = True
    app.mode_title.update_title("Dataset Mode")


def window_leader_mode(event):
    """Enter window mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app._flag_normal_mode = False
    app._flag_window_mode = True
    app.mode_title.update_title("Window Mode")


def plotting_leader_mode(event):
    """Enter plotting mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app._flag_normal_mode = False
    app._flag_plotting_mode = True
    app.mode_title.update_title("Plotting Mode")


def hist_leader_mode(event):
    """Enter hist mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app._flag_normal_mode = False
    app._flag_hist_mode = True
    app.mode_title.update_title("Histogram Mode")


@error_handler
def exit_leader_mode(event):
    """Exit leader mode."""
    # Access the application instance
    app = event.app.h5forest_app

    app.return_to_normal_mode()
    app.default_focus()
    event.app.invalidate()


def expand_attributes(event):
    """Expand the attributes."""
    # Access the application instance
    app = event.app.h5forest_app

    app.flag_expanded_attrs = True
    app.update_hotkeys_panel()
    event.app.invalidate()


def collapse_attributes(event):
    """Collapse the attributes."""
    # Access the application instance
    app = event.app.h5forest_app

    app.flag_expanded_attrs = False
    app.update_hotkeys_panel()
    event.app.invalidate()


def search_leader_mode(event):
    """Enter search mode."""
    # Access the application instance
    app = event.app.h5forest_app

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
def restore_tree_to_initial(event):
    """Restore the tree to initial state (as when app was opened)."""
    # Access the application instance
    app = event.app.h5forest_app

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
    # Access the application instance
    app = event.app.h5forest_app

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


class H5KeyBindings:
    """A class holding and applying keybindings based on application state."""

    def __init__(self, app):
        """Initialize the keybindings."""

        # Attach the application instance
        self.app = app

        # Attach the config instance
        self.config = app.config

        # Define attributes to hold all the keys
        self.dataset_leader_key = self.config.get_keymap(
            "dataset_mode",
            "leader",
        )
        self.goto_leader_key = self.config.get_keymap(
            "jump_mode",
            "leader",
        )
        self.hist_leader_key = self.config.get_keymap(
            "hist_mode",
            "leader",
        )
        self.plot_leader_key = self.config.get_keymap(
            "plot_mode",
            "leader",
        )
        self.window_leader_key = self.config.get_keymap(
            "window_mode",
            "leader",
        )
        self.search_leader_key = self.config.get_keymap(
            "search_mode",
            "leader",
        )
        self.restore_key = self.config.get_keymap(
            "normal_mode",
            "restore_tree",
        )
        self.copy_key_binding = self.config.get_keymap(
            "normal_mode",
            "copy_path",
        )
        self.quit_key = self.config.get_keymap(
            "normal_mode",
            "quit",
        )
        self.toggle_attrs_key = self.config.get_keymap(
            "normal_mode",
            "expand_attributes",
        )

        # Define attributes to hold all the different labels
        self.dataset_mode_label = Label(
            f"{translate_key_label(self.dataset_leader_key)} → Dataset Mode"
        )
        self.goto_mode_label = Label(
            f"{translate_key_label(self.goto_leader_key)} → Goto Mode"
        )
        self.hist_mode_label = Label(
            f"{translate_key_label(self.hist_leader_key)} → Histogram Mode"
        )
        self.plotting_mode_label = Label(
            f"{translate_key_label(self.plot_leader_key)} → Plotting Mode"
        )
        self.window_mode_label = Label(
            f"{translate_key_label(self.window_leader_key)} → Window Mode"
        )
        self.search_label = Label(
            f"{translate_key_label(self.search_leader_key)} → Search"
        )
        self.restore_tree_label = Label(
            f"{translate_key_label(self.restore_key)} → Restore Tree"
        )
        self.copy_key_label = Label(
            f"{translate_key_label(self.copy_key_binding)} → Copy Key"
        )
        self.exit_label = Label(f"{translate_key_label(self.quit_key)} → Exit")
        self.expand_attrs_label = Label(
            f"{translate_key_label(self.toggle_attrs_key)} → Expand Attributes"
        )
        self.shrink_attrs_label = Label(
            f"{translate_key_label(self.toggle_attrs_key)} → Shrink Attributes"
        )

    def bind_function(self, key, function, filter_lambda):
        """Bind a function to a key with a filter condition.

        Args:
            key (str): The key to bind the function to.
            function (callable): The function to bind.
            filter_lambda (callable): A lambda function that returns a boolean
                indicating whether the binding should be active.
        """
        self.app.kb.add(key, filter=Condition(filter_lambda))(function)

    def _init_normal_mode_bindings(self):
        """Initialize normal mode keybindings."""
        # For clarity extract the app instance
        app = self.app

        # Bind mode leader keys
        self.bind_function(
            self.goto_leader_key,
            goto_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.dataset_leader_key,
            dataset_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.window_leader_key,
            window_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.hist_leader_key,
            hist_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.plot_leader_key,
            plotting_leader_mode,
            lambda: app.flag_normal_mode,
        )

        # Bind the search leader key but only if tree has focus
        self.bind_function(
            self.search_leader_key,
            search_leader_mode,
            lambda: app.flag_normal_mode
            and app.app.layout.has_focus(app.tree_content.content),
        )

        # Binding the expand/collapse attributes keys
        self.bind_function(
            self.toggle_attrs_key,
            expand_attributes,
            lambda: app.flag_normal_mode and not app.flag_expanded_attrs,
        )
        self.bind_function(
            self.toggle_attrs_key,
            collapse_attributes,
            lambda: app.flag_normal_mode and app.flag_expanded_attrs,
        )

        # Bind the tree restoration key
        self.bind_function(
            self.restore_key,
            restore_tree_to_initial,
            lambda: app.flag_normal_mode,
        )

        # Bind the copy key
        self.bind_function(
            self.copy_key_binding,
            copy_key,
            lambda: app.flag_normal_mode,
        )

        # Binding the quitting machinery
        self.bind_function(
            self.quit_key,
            exit_app,
            lambda: app.flag_normal_mode,
        )

        # Bind exiting a leader mode
        self.bind_function(
            self.quit_key,
            exit_leader_mode,
            lambda: not app.flag_normal_mode,
        )

    def _init_bindings(self):
        """Initialize all keybindings."""

        self._init_normal_mode_bindings()

    def _get_normal_labels(self):
        """Get the labels that are always shown in normal mode."""
        # Show expand/collapse attributes key based on current state
        if self.app.flag_expanded_attrs:
            toggle_attr_label = self.shrink_attrs_label
        else:
            toggle_attr_label = self.expand_attrs_label

        labels = [
            self.goto_mode_label,
            self.dataset_mode_label,
            self.window_mode_label,
            self.hist_mode_label,
            self.plotting_mode_label,
            self.search_label,
            self.copy_key_label,
            toggle_attr_label,
            self.restore_tree_label,
            self.exit_label,
        ]

        return labels

    def get_current_hotkeys(self):
        """Get the current hotkeys based on application state."""
        # Get the application instance for clarity
        app = self.app

        # Initialise a list in which we will store the hotkey labels to show
        # Note that order matters here as it defines the order in which the
        # hotkeys are shown in the UI
        hotkeys = []

        # Are we in normal mode?
        if app.flag_normal_mode:
            # Yes - show normal mode hotkeys
            hotkeys.extend(self._get_normal_labels())
