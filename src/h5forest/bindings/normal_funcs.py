"""A submodule defining the normal mode functions for H5Forest bindings.

These functions are bound to keys in the H5KeyBindings defined in
h5forest.bindings. They implement the behavior of normal mode, such as
exiting the app, entering leader modes, expanding/collapsing attributes,
searching, restoring the tree, and copying keys to the clipboard.
"""

import platform
import subprocess

from prompt_toolkit.document import Document

from h5forest.errors import error_handler


def exit_app(event):
    """Exit the app."""
    event.app.exit()


def goto_leader_mode(event):
    """Enter goto mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_jump_mode = True


def dataset_leader_mode(event):
    """Enter dataset mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_dataset_mode = True


def window_leader_mode(event):
    """Enter window mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_window_mode = True


def plotting_leader_mode(event):
    """Enter plotting mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_plotting_mode = True


def hist_leader_mode(event):
    """Enter hist mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app._flag_normal_mode = False
    app._flag_hist_mode = True


@error_handler
def exit_leader_mode(event):
    """Exit leader mode."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app.return_to_normal_mode()
    app.default_focus()
    event.app.invalidate()


@error_handler
def restore_tree_to_initial(event):
    """Restore the tree to initial state (as when app was opened)."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

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
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

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
