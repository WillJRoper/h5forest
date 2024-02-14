import argparse
import threading

from prompt_toolkit import Application
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import HSplit, VSplit, ConditionalContainer
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Frame, TextArea, Label
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit.document import Document

from h5forest.tree import Tree
from h5forest.utils import DynamicTitle, get_window_size

# Setup command line args
parser = argparse.ArgumentParser(description="HDF5 file viewer")
parser.add_argument("--filepath", help="The HDF5 file to view")

# Parse the command line args
args = parser.parse_args()

# Set up the Tree object
tree = Tree(args.filepath)

# Set up some global flags
values_visible = [False]


# Keybindings for the application
kb = KeyBindings()


@kb.add("c-q")
def exit_app(event):
    event.app.exit()


# Assuming `hdf5_structure` is defined outside to be accessible
hdf5_structure = TextArea(
    text=tree.get_tree_text(),
    scrollbar=True,
    read_only=True,
)

metadata_content = TextArea(
    text="Metadata details here...",
    scrollbar=False,
    focusable=False,
    read_only=True,
)

attributes_content = TextArea(
    text="Attributes here...",
    read_only=True,
    scrollbar=True,
    focusable=False,
)

values_content = TextArea(
    text="Values here...",
    read_only=True,
    scrollbar=True,
    focusable=False,
)

# Define a list of hotkeys
hotkeys_panel = Label(
    "C-q → Exit    RET → Open Node    v → View Values    "
    "C-v → Close Value View    C-t → Jump to top"
)

# Create dynamic title for the values view
value_title = DynamicTitle("Values")


def set_cursor_position(text, new_cursor_pos):
    # Create a new document for the TextArea with the updated cursor position
    hdf5_structure.document = Document(
        text=text, cursor_position=new_cursor_pos
    )


def calculate_new_cursor_position(current_row, node, text):
    """
    Calculate the new cursor position after text update.
    This function needs to be implemented based on how the text structure changes.
    """
    # Example calculation; this needs to be specific to your application's logic
    # For simplicity, let's assume the cursor should move to the beginning of the same row
    lines = text.split("\n")
    new_position = sum(
        len(lines[i]) + 1 for i in range(current_row)
    )  # +1 for newline characters
    return new_position


def cursor_moved_action():
    while True:
        # Directly use `hdf5_structure` instead of trying to get it from the
        # focus
        doc = hdf5_structure.document

        # Get the current cursor row
        current_row = doc.cursor_position_row

        # Get the current node
        try:
            node = tree.get_current_node(current_row)
            metadata_content.text = node.get_meta_text()
            attributes_content.text = node.get_attr_text()

        except IndexError:
            set_cursor_position(
                hdf5_structure.text,
                new_cursor_pos=len(hdf5_structure.text),
            )
            metadata_content.text = ""
            attributes_content.text = ""

        get_app().invalidate()


@kb.add("enter")
def expand_collapse_node(event):
    """
    Expand the node under the cursor.

    This uses lazy loading so only the group at the expansion point will be
    loaded.
    """

    # Directly use `hdf5_structure` instead of trying to get it from the focus
    doc = hdf5_structure.document

    # Get the current cursor row and position
    current_row = doc.cursor_position_row

    # Get the node under the cursor
    node = tree.get_current_node(current_row)

    # If we have a dataset, redirect to show_values as a safe fall back
    if node.is_dataset:
        show_values(event)
        return

    # If the node is already open, close it
    if node.is_expanded:
        tree.close_node(node, current_row, hdf5_structure)
    else:  # Otherwise, open it
        tree.update_tree_text(node, current_row, hdf5_structure)

    # After updating, calculate the new cursor position
    # This is simplified; you'll need to adjust logic based on how text is updated
    new_cursor_position = calculate_new_cursor_position(
        current_row, node, hdf5_structure.text
    )

    set_cursor_position(
        hdf5_structure.text, new_cursor_pos=new_cursor_position
    )


@kb.add("c-t")
def jump_to_top(event):
    """Jump to the top of the tree."""
    set_cursor_position(hdf5_structure.text, new_cursor_pos=0)


@kb.add("c-b")
def jump_to_bottom(event):
    """Jump to the bottom of the tree."""
    set_cursor_position(
        hdf5_structure.text, new_cursor_pos=len(hdf5_structure.text)
    )


@kb.add("v")
def show_values(event):
    """
    Show the values of a dataset.

    This will truncate the value list if the array is large so as not to flood
    memory.
    """
    # Directly use `hdf5_structure` instead of trying to get it from the focus
    doc = hdf5_structure.document

    # Get the current cursor row and position
    current_row = doc.cursor_position_row

    # Get the node under the cursor
    node = tree.get_current_node(current_row)

    # Get the value string
    text = node.get_value_text()

    # Ensure there's something to draw
    if len(text) == 0:
        return

    value_title.update_title(f"Values: {node.path}")

    # Update the text
    values_content.text = text

    # Flag that there are values to show
    values_visible[0] = True


@kb.add("c-v")
def close_values(event):
    """Close the value pane."""
    values_visible[0] = False
    values_content.text = ""


# Function to create the application layout
def create_layout():
    # Get the window size
    rows, columns = get_window_size()

    # Layout using split views
    layout = Layout(
        HSplit(
            [
                VSplit(
                    [
                        HSplit(
                            [
                                Frame(hdf5_structure, title="HDF5 Structure"),
                                Frame(
                                    metadata_content,
                                    height=10,
                                    title="Metadata",
                                ),
                            ]
                        ),
                        Frame(attributes_content, title="Attributes"),
                        ConditionalContainer(
                            content=Frame(
                                values_content,
                                width=columns // 3,
                                title=value_title,
                            ),
                            filter=Condition(lambda: values_visible[0]),
                        ),
                    ]
                ),
                hotkeys_panel,
            ]
        )
    )

    return layout


# Initialize and run the application
def main():
    layout = create_layout()
    app = Application(layout=layout, key_bindings=kb, full_screen=True)

    # Kick off a thread to track changes to the automatically populated
    # frames
    thread1 = threading.Thread(target=cursor_moved_action)
    thread1.daemon = True
    thread1.start()

    app.run()


if __name__ == "__main__":
    main()
