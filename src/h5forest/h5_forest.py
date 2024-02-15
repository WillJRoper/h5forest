"""The main application for the HDF5 Forest.

This application provides a CLI application for exploring HDF5 files. This is
enabled by the h5forest entry point set up when the package is installed.

Example Usage:
    h5forest /path/to/file.hdf5

"""
import sys
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
from h5forest.utils import (
    DynamicTitle,
    get_window_size,
    calculate_new_cursor_position,
)


class H5Forest:
    def __init__(self, hdf5_filepath):
        """ """

        # We do, set up the Tree with the file
        # This will parse the root of the HDF5 file ready to populate the
        # tree text area
        self.tree = Tree(hdf5_filepath)

        # Define flags we need to control behaviour
        self.flag_values_visible = False

        # Set up the keybindings
        self.kb = KeyBindings()
        self._init_app_bindings()
        self._init_tree_bindings()

        # Attributes for dynamic titles
        self.value_title = DynamicTitle("Values")

        # Set up the text areas that will populate the layout
        self.tree_content = None
        self.metadata_content = None
        self.attributes_content = None
        self.values_content = None
        self._init_text_areas()

        # Set up the list of hotkeys to be displayed in different situations
        self.hotkeys_panel = Label(
            "CTRL-q → Exit    RET → Open Node    v → View Values    "
            "CTRL-v → Close Value View    CTRL-t → Jump to top"
        )

        # We need to hang on to some information to avoid over the
        # top computations running in the background for threaded functions
        self.prev_row = None

        # Set up the layout
        self.tree_frame = None
        self.metadata_frame = None
        self.attrs_frame = None
        self.values_frame = None
        self.layout = None
        self._init_layout()

        # With all that done we can set up the application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True,
        )

    def run(self):
        """Run the application."""
        self.app.run()

    @property
    def current_row(self):
        """Return the row under the cursor."""
        # Get the tree content
        doc = self.tree_content.document

        # Get the current cursor row
        current_row = doc.cursor_position_row

        return current_row

    def _init_app_bindings(self):
        """Set up the keybindings for the UI."""

        @self.kb.add("c-q")
        def exit_app(event):
            """Exit the app."""
            event.app.exit()

        @self.kb.add("c-v")
        def close_values(event):
            """Close the value pane."""
            self.flag_values_visible = False
            self.values_content.text = ""

    def _init_tree_bindings(self):
        """Set up the keybindings for the UI."""

        @self.kb.add("enter")
        def expand_collapse_node(event):
            """
            Expand the node under the cursor.

            This uses lazy loading so only the group at the expansion point
            will be loaded.
            """
            # Directly use `tree_content` instead of trying to get it from
            # the focus
            doc = self.tree_content.document

            # Get the current cursor row and position
            current_row = doc.cursor_position_row

            # Get the node under the cursor
            node = self.tree.get_current_node(current_row)

            # If we have a dataset, redirect to show_values as a safe fall back
            if node.is_dataset:
                show_values(event)
                return

            # If the node is already open, close it
            if node.is_expanded:
                self.tree.close_node(node, current_row, self.tree_content)
            else:  # Otherwise, open it
                self.tree.update_tree_text(
                    node, current_row, self.tree_content
                )

            # After updating, calculate the new cursor position
            new_cursor_position = calculate_new_cursor_position(
                current_row, node, self.tree_content.text
            )

            self.set_cursor_position(
                self.tree_content.text, new_cursor_pos=new_cursor_position
            )

        @self.kb.add("c-t")
        def jump_to_top(event):
            """Jump to the top of the tree."""
            self.set_cursor_position(self.tree_content.text, new_cursor_pos=0)

        @self.kb.add("c-b")
        def jump_to_bottom(event):
            """Jump to the bottom of the tree."""
            self.set_cursor_position(
                self.tree_content.text,
                new_cursor_pos=len(self.tree_content.text),
            )

        @self.kb.add("v")
        def show_values(event):
            """
            Show the values of a dataset.

            This will truncate the value list if the array is large so as not
            to flood memory.
            """
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Get the value string
            text = node.get_value_text()

            # Ensure there's something to draw
            if len(text) == 0:
                return

            self.value_title.update_title(f"Values: {node.path}")

            # Update the text
            self.values_content.text = text

            # Flag that there are values to show
            self.flag_values_visible = True

    def _init_text_areas(self):
        """Initialise the text areas which will contain all information."""
        # Text area for the tree itself
        self.tree_content = TextArea(
            text=self.tree.get_tree_text(),
            scrollbar=True,
            read_only=True,
        )

        #
        self.metadata_content = TextArea(
            text="Metadata details here...",
            scrollbar=False,
            focusable=False,
            read_only=True,
        )

        self.attributes_content = TextArea(
            text="Attributes here...",
            read_only=True,
            scrollbar=True,
            focusable=True,
        )

        self.values_content = TextArea(
            text="Values here...",
            read_only=True,
            scrollbar=True,
            focusable=False,
        )

    def set_cursor_position(self, text, new_cursor_pos):
        """
        Set the cursor position in the tree.

        This is a horrid workaround but seems to be the only way to do it
        in prompt_toolkit. We reset the entire Document with the
        tree content text and a new cursor position.
        """
        # Create a new tree_content document with the updated cursor
        # position
        self.tree_content.document = Document(
            text=text, cursor_position=new_cursor_pos
        )

    def cursor_moved_action(self):
        """
        Apply changes when the cursor has been moved.

        This will update the metadata and attribute outputs to display
        what is currently under the cursor.
        """
        while True:
            # Check if we even have to update anything
            if self.current_row == self.prev_row:
                continue
            else:
                self.prev_row = self.current_row

            # Get the current node
            try:
                node = self.tree.get_current_node(self.current_row)
                self.metadata_content.text = node.get_meta_text()
                self.attributes_content.text = node.get_attr_text()

            except IndexError:
                self.set_cursor_position(
                    self.tree_content.text,
                    new_cursor_pos=len(self.tree_content.text),
                )
                self.metadata_content.text = ""
                self.attributes_content.text = ""

            get_app().invalidate()

    def _init_layout(self):
        """Intialise the layout."""
        # Get the window size
        rows, columns = get_window_size()

        # Create each individual element of the UI before packaging it
        # all into the layout
        self.tree_frame = Frame(self.tree_content, title="HDF5 Structure")
        self.metadata_frame = Frame(
            self.metadata_content, title="Metadata", height=10
        )
        self.attrs_frame = Frame(self.attributes_content, title="Attributes")
        self.values_frame = Frame(
            self.values_content, title=self.value_title, width=columns // 3
        )

        # Wrap those frames that need it in conditional containers
        self.values_frame = ConditionalContainer(
            content=self.values_frame,
            filter=Condition(lambda: self.flag_values_visible),
        )

        # Layout using split views
        self.layout = Layout(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit(
                                [
                                    self.tree_frame,
                                    self.metadata_frame,
                                ]
                            ),
                            self.attrs_frame,
                            self.values_frame,
                        ]
                    ),
                    self.hotkeys_panel,
                ]
            )
        )


def main():
    """Intialise and run the application."""
    # First port of call, check we have been given a valid input
    if len(sys.argv) != 2:
        print("Usage: h5forest /path/to/file.hdf5")
        sys.exit(1)

    # Extract the filepath
    filepath = sys.argv[1]

    # Set up the app
    app = H5Forest(filepath)

    # Kick off a thread to track changes to the automatically populated
    # frames
    thread1 = threading.Thread(target=app.cursor_moved_action)
    thread1.daemon = True
    thread1.start()

    # Lets get going!
    app.run()


if __name__ == "__main__":
    main()
