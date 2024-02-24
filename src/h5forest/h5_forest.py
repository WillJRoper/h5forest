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

from h5forest.plotting import DensityPlotter, HistogramPlotter
from h5forest.tree import Tree
from h5forest.utils import DynamicTitle, get_window_size
from h5forest._version import __version__


class H5Forest:
    """
    The main application for the HDF5 Forest.

    This class is a singleton. Any attempt to create a new instance will
    return the existing instance. This makes the instance available globally.

    Attributes:
        tree (Tree):
            The tree object representing the HDF5 file. Each Group or
            Dataset in the HDF5 file is represented by a Node object.
        flag_values_visible (bool):
            A flag to control the visibility of the values text area.
        _flag_normal_mode (bool):
            A flag to control the normal mode of the application.
        _flag_jump_mode (bool):
            A flag to control the jump mode of the application.
        _flag_dataset_mode (bool):
            A flag to control the dataset mode of the application.
        _flag_window_mode (bool):
            A flag to control the window mode of the application.
        jump_keys (VSplit):
            The hotkeys for the jump mode.
        dataset_keys (VSplit):
            The hotkeys for the dataset mode.
        window_keys (VSplit):
            The hotkeys for the window mode.
        kb (KeyBindings):
            The keybindings for the application.
        value_title (DynamicTitle):
            A dynamic title for the values text area.
        tree_content (TextArea):
            The text area for the tree.
        metadata_content (TextArea):
            The text area for the metadata.
        attributes_content (TextArea):
            The text area for the attributes.
        values_content (TextArea):
            The text area for the values.
        mini_buffer_content (TextArea):
            The text area for the mini buffer.
        hot_keys (VSplit):
            The hotkeys for the application.
        hotkeys_panel (HSplit):
            The panel to display hotkeys.
        prev_row (int):
            The previous row the cursor was on. This means we can avoid
            updating the metadata and attributes when the cursor hasn't moved.
        tree_frame (Frame):
            The frame for the tree text area.
        metadata_frame (Frame):
            The frame for the metadata text area.
        attrs_frame (Frame):
            The frame for the attributes text area.
        values_frame (Frame):
            The frame for the values text area.
        mini_buffer (Frame):
            The frame for the mini buffer text area.
        layout (Layout):
            The layout of the application.
        user_input (str):
            A container for the user input from the most recent mini buffer.
        app (Application):
            The main application object.
    """

    # Singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the class.

        This method ensures that only one instance of the class is created.

        This method takes precendence over the usual __init__ method.
        """
        if cls._instance is None:
            cls._instance = super(H5Forest, cls).__new__(cls)
            # Call the init method explicitly to initialize the instance
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def _init(self, hdf5_filepath):
        """
        Initialise the application.

        Constructs all the frames necessary for the app, builds the HDF5 tree
        (populating only the root), and populates the Layout.

        Args:
            hdf5_filepath (str):
                The path to the HDF5 file to be explored.
        """
        # We do, set up the Tree with the file
        # This will parse the root of the HDF5 file ready to populate the
        # tree text area
        self.tree = Tree(hdf5_filepath)

        # Define flags we need to control behaviour
        self.flag_values_visible = False
        self.flag_progress_bar = False

        # Define the leader key mode flags
        # NOTE: These must be unset when the leader mode is exited, and in
        # _flag_normal_mode when the escape key is pressed
        self._flag_normal_mode = True
        self._flag_jump_mode = False
        self._flag_dataset_mode = False
        self._flag_window_mode = False
        self._flag_plotting_mode = False
        self._flag_hist_mode = False

        # Intialise the different leader key mode hot keys
        self.jump_keys = VSplit(
            [
                Label("t → Jump to Top"),
                Label("b → Jump to Bottom"),
                Label("p → Jump to Parent"),
                Label("n → Jump to Next"),
                Label("k → Jump to Next Key"),
                Label("q → Exit Jump Mode"),
            ]
        )
        self.dataset_keys = VSplit(
            [
                Label("v → Show Values"),
                Label("V → Show Values In Range"),
                Label("m → Get Minimum and Maximum"),
                Label("M → Get Mean"),
                Label("s → Get Standard Deviation"),
                Label("c → Close Value View"),
                Label("q → Exit Dataset Mode"),
            ]
        )
        self.window_keys = VSplit(
            [
                ConditionalContainer(
                    Label("t → Move to Tree"),
                    Condition(
                        lambda: not self.app.layout.has_focus(
                            self.tree_content
                        )
                    ),
                ),
                ConditionalContainer(
                    Label("a → Move to Attributes"),
                    Condition(
                        lambda: not self.app.layout.has_focus(
                            self.attributes_content
                        )
                    ),
                ),
                ConditionalContainer(
                    Label("v → Move to Values"),
                    Condition(
                        lambda: self.flag_values_visible
                        and not self.app.layout.has_focus(self.values_content)
                    ),
                ),
                ConditionalContainer(
                    Label("p → Move to Plot"),
                    Condition(
                        lambda: not self.app.layout.has_focus(
                            self.plot_content
                        )
                    ),
                ),
                Label("q → Exit Window Mode"),
            ]
        )
        self.plot_keys = VSplit(
            [
                ConditionalContainer(
                    Label("Enter → Edit entry"),
                    Condition(
                        lambda: self.app.layout.has_focus(self.plot_content)
                    ),
                ),
                ConditionalContainer(
                    Label("x → Select x-axis"),
                    filter=Condition(
                        lambda: "x" not in self.density_plotter.plot_params
                    ),
                ),
                ConditionalContainer(
                    Label("y → Select y-axis"),
                    filter=Condition(
                        lambda: "y" not in self.density_plotter.plot_params
                    ),
                ),
                ConditionalContainer(
                    Label("w → Select Weights"),
                    filter=Condition(
                        lambda: "weights"
                        not in self.density_plotter.plot_params
                    ),
                ),
                ConditionalContainer(
                    Label("c → Compute Density (Count)"),
                    filter=Condition(
                        lambda: "x" in self.density_plotter.plot_params
                        and "y" in self.density_plotter.plot_params
                        and self.density_plotter.count_density is None
                    ),
                ),
                ConditionalContainer(
                    Label("s → Compute Density (Sum)"),
                    filter=Condition(
                        lambda: "x" in self.density_plotter.plot_params
                        and "y" in self.density_plotter.plot_params
                        and "color" in self.density_plotter.plot_params
                        and self.density_plotter.sum_density is None
                    ),
                ),
                ConditionalContainer(
                    Label("m → Compute Density (Mean)"),
                    filter=Condition(
                        lambda: "x" in self.density_plotter.plot_params
                        and "y" in self.density_plotter.plot_params
                        and "color" in self.density_plotter.plot_params
                        and self.density_plotter.mean_density is None
                    ),
                ),
                ConditionalContainer(
                    Label("C → Show Density (Count)"),
                    filter=Condition(
                        lambda: self.density_plotter.count_density is not None
                    ),
                ),
                ConditionalContainer(
                    Label("S → Show Density (Sum)"),
                    filter=Condition(
                        lambda: self.density_plotter.sum_density is not None
                    ),
                ),
                ConditionalContainer(
                    Label("M → Show Density (Mean)"),
                    filter=Condition(
                        lambda: self.density_plotter.mean_density is not None
                    ),
                ),
                ConditionalContainer(
                    Label("CTRL-c → Save Density (Count)"),
                    filter=Condition(
                        lambda: self.density_plotter.count_density is not None
                    ),
                ),
                ConditionalContainer(
                    Label("CTRL-s → Save Density (Sum)"),
                    filter=Condition(
                        lambda: self.density_plotter.sum_density is not None
                    ),
                ),
                ConditionalContainer(
                    Label("CTRL-M → Save Density (Mean)"),
                    filter=Condition(
                        lambda: self.density_plotter.mean_density is not None
                    ),
                ),
                Label("r → Reset"),
                Label("q → Exit Plotting Mode"),
            ]
        )
        self.hist_keys = VSplit(
            [
                ConditionalContainer(
                    Label("Enter → Edit entry"),
                    Condition(
                        lambda: self.app.layout.has_focus(self.hist_content)
                    ),
                ),
                ConditionalContainer(
                    Label("d → Select data"),
                    filter=Condition(
                        lambda: "data"
                        not in self.histogram_plotter.plot_params
                    ),
                ),
                ConditionalContainer(
                    Label("h → Compute Histogram"),
                    filter=Condition(
                        lambda: "data" in self.histogram_plotter.plot_params
                        and self.histogram_plotter.hist is None
                    ),
                ),
                ConditionalContainer(
                    Label("H → Show Histogram"),
                    filter=Condition(
                        lambda: self.histogram_plotter.hist is not None
                    ),
                ),
                ConditionalContainer(
                    Label("CTRL-h → Save Histogram"),
                    filter=Condition(
                        lambda: self.histogram_plotter.hist is not None
                    ),
                ),
                Label("r → Reset"),
                Label("q → Exit Hist Mode"),
            ]
        )

        # set up the keybindings
        self.kb = KeyBindings()
        self._init_leader_bindings()
        self._init_app_bindings()
        self._init_dataset_bindings()
        self._init_jump_bindings()
        self._init_window_bindings()
        self._init_plot_bindings()
        self._init_hist_bindings()

        # Attributes for dynamic titles
        self.value_title = DynamicTitle("Values")

        # Attach the hexbin plotter
        self.density_plotter = DensityPlotter()
        self.histogram_plotter = HistogramPlotter()

        # Set up the text areas that will populate the layout
        self.tree_content = None
        self.metadata_content = None
        self.attributes_content = None
        self.values_content = None
        self.mini_buffer_content = None
        self.progress_bar_content = None
        self.plot_content = None
        self.hist_content = None
        self._init_text_areas()

        # Set up the list of hotkeys and leaders for the UI
        # These will always be displayed unless the user is in a leader mode
        self.hot_keys = VSplit(
            [
                Label("Enter → Open Group"),
                Label("d → Dataset Mode"),
                Label("h → Hist Mode"),
                Label("j → Jump Mode"),
                Label("p → Plotting Mode"),
                Label("w → Window Mode"),
                Label("{ → Move Up 10 Lines"),
                Label("} → Move Down 10 Lines"),
                Label("q → Exit"),
            ]
        )
        self.hotkeys_panel = None

        # We need to hang on to some information to avoid over the
        # top computations running in the background for threaded functions
        self.prev_row = None

        # Set up the layout
        self.tree_frame = None
        self.metadata_frame = None
        self.attrs_frame = None
        self.values_frame = None
        self.plot_frame = None
        self.hist_frame = None
        self.layout = None
        self._init_layout()

        # Intialise a container for user input
        self.user_input = None

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
        """
        Return the row under the cursor.

        Returns:
            int:
                The row under the cursor.
        """
        # Get the tree content
        doc = self.tree_content.document

        # Get the current cursor row
        current_row = doc.cursor_position_row

        return current_row

    @property
    def current_column(self):
        """
        Return the column under the cursor.

        Returns:
            int:
                The column under the cursor.
        """
        # Get the tree content
        doc = self.tree_content.document

        # Get the current cursor row
        current_col = doc.cursor_position_col

        return current_col

    @property
    def current_position(self):
        """
        Return the current position in the tree.

        Returns:
            int:
                The current position in the tree.
        """
        return self.tree_content.document.cursor_position

    @property
    def flag_normal_mode(self):
        """
        Return the normal mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for normal mode.
        """
        return self._flag_normal_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    @property
    def flag_jump_mode(self):
        """
        Return the jump mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for jump mode.
        """
        return self._flag_jump_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    @property
    def flag_dataset_mode(self):
        """
        Return the dataset mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for dataset mode.
        """
        return self._flag_dataset_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    @property
    def flag_window_mode(self):
        """
        Return the window mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for window mode.
        """
        return self._flag_window_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    @property
    def flag_plotting_mode(self):
        """
        Return the plotting mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for plotting mode.
        """
        return self._flag_plotting_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    @property
    def flag_hist_mode(self):
        """
        Return the histogram mode flag.

        This accounts for whether we are awaiting user input in the mini
        buffer.

        Returns:
            bool:
                The flag for histogram mode.
        """
        return self._flag_hist_mode and not self.app.layout.has_focus(
            self.mini_buffer_content
        )

    def return_to_normal_mode(self):
        """Return to normal mode."""
        self._flag_normal_mode = True
        self._flag_jump_mode = False
        self._flag_dataset_mode = False
        self._flag_window_mode = False
        self._flag_plotting_mode = False
        self._flag_hist_mode = False

    def _init_leader_bindings(self):
        """Set up the leader key bindsings."""

        @self.kb.add("j", filter=Condition(lambda: self.flag_normal_mode))
        def jump_leader_mode(event):
            """Enter jump mode."""
            self._flag_normal_mode = False
            self._flag_jump_mode = True

        @self.kb.add("d", filter=Condition(lambda: self.flag_normal_mode))
        def dataset_leader_mode(event):
            """Enter dataset mode."""
            self._flag_normal_mode = False
            self._flag_dataset_mode = True

        @self.kb.add("w", filter=Condition(lambda: self.flag_normal_mode))
        def window_leader_mode(event):
            """Enter window mode."""
            self._flag_normal_mode = False
            self._flag_window_mode = True

        @self.kb.add("p", filter=Condition(lambda: self.flag_normal_mode))
        def plotting_leader_mode(event):
            """Enter plotting mode."""
            self._flag_normal_mode = False
            self._flag_plotting_mode = True

        @self.kb.add("h", filter=Condition(lambda: self.flag_normal_mode))
        def hist_leader_mode(event):
            """Enter hist mode."""
            self._flag_normal_mode = False
            self._flag_hist_mode = True

        @self.kb.add("q")
        def exit_leader_mode(event):
            """Exit leader mode."""
            self.return_to_normal_mode()
            self.default_focus()
            event.app.invalidate()

    def _init_app_bindings(self):
        """
        Set up the keybindings for the basic UI.

        These are always active and are not dependent on any leader key.
        """

        @self.kb.add("q", filter=Condition(lambda: self.flag_normal_mode))
        def exit_app(event):
            """Exit the app."""
            event.app.exit()

        @self.kb.add("c-q")
        def other_exit_app(event):
            """Exit the app."""
            event.app.exit()

        @self.kb.add("{")
        def move_up_ten(event):
            """Move up ten lines."""
            # Get the current position
            pos = self.current_position

            # Move up 10 lines
            for row in range(self.current_row - 1, self.current_row - 11, -1):
                # Compute the position at this row
                pos -= len(self.tree.tree_text_split[row]) + 1

                if pos < 0:
                    pos = 0
                    break

            # Move the cursor
            self.set_cursor_position(self.tree.tree_text, pos)

        @self.kb.add("}")
        def move_down_ten(event):
            """Move down ten lines."""
            # Get the current position
            pos = self.current_position

            # Move down 10 lines
            for row in range(self.current_row, self.current_row + 10):
                # Compute the position at this row
                pos += len(self.tree.tree_text_split[row]) + 1

                if row + 1 > self.tree.height - 1:
                    pos = self.tree.length - len(
                        self.tree.tree_text_split[self.tree.height - 1]
                    )
                    break

            # Ensure we don't overshoot
            if pos > self.tree.length:
                pos = self.tree.length - len(
                    self.tree.tree_text_split[self.tree.height - 1]
                )

            # Move the cursor
            self.set_cursor_position(self.tree.tree_text, pos)

        @self.kb.add(
            "enter",
            filter=Condition(
                lambda: self.app.layout.has_focus(self.tree_content)
            ),
        )
        def expand_collapse_node(event):
            """
            Expand the node under the cursor.

            This uses lazy loading so only the group at the expansion point
            will be loaded.
            """
            # Get the current cursor row and position
            current_row = self.current_row
            current_pos = self.current_position

            # Get the node under the cursor
            node = self.tree.get_current_node(current_row)

            # If we have a dataset just do nothing
            if node.is_dataset:
                self.print(f"{node.path} is not a Group")
                return

            # If the node has no children, do nothing
            if not node.has_children:
                self.print(f"{node.path} has no children")
                return

            # If the node is already open, close it
            if node.is_expanded:
                self.tree.close_node(node, current_row, self.tree_content)
            else:  # Otherwise, open it
                self.tree.update_tree_text(
                    node, current_row, self.tree_content
                )

            # Reset the cursor position post update
            self.set_cursor_position(
                self.tree.tree_text, new_cursor_pos=current_pos
            )

    def _init_dataset_bindings(self):
        """Set up the keybindings for the dataset mode."""

        @self.kb.add("v", filter=Condition(lambda: self.flag_dataset_mode))
        def show_values(event):
            """
            Show the values of a dataset.

            This will truncate the value list if the array is large so as not
            to flood memory.
            """
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

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

            # Exit values mode
            self.return_to_normal_mode()

        @self.kb.add("V", filter=Condition(lambda: self.flag_dataset_mode))
        def show_values_in_range(event):
            """Show the values of a dataset in an index range."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            def values_in_range_callback():
                """Get the start and end indices from the user input."""
                # Parse the range
                string_values = tuple(
                    [s.strip() for s in self.user_input.split("-")]
                )

                # Attempt to convert to an int
                try:
                    start_index = int(string_values[0])
                    end_index = int(string_values[1])
                except ValueError:
                    self.print(
                        "Invalid input! Input must be a integers "
                        f"separated by -, not ({self.user_input})"
                    )

                    # Exit this attempt gracefully
                    self.default_focus()
                    self.return_to_normal_mode()
                    return

                # Return focus to the tree
                self.default_focus()

                # Get the value string
                text = node.get_value_text(
                    start_index=start_index, end_index=end_index
                )

                # Ensure there's something to draw
                if len(text) == 0:
                    return

                self.value_title.update_title(f"Values: {node.path}")

                # Update the text
                self.values_content.text = text

                # Flag that there are values to show
                self.flag_values_visible = True

                # Exit values mode
                self.return_to_normal_mode()

            # Get the indices from the user
            self.input(
                "Enter the index range (seperated by -):",
                values_in_range_callback,
            )

        @self.kb.add("c", filter=Condition(lambda: self.flag_dataset_mode))
        def close_values(event):
            """Close the value pane."""
            self.flag_values_visible = False
            self.values_content.text = ""

            # Exit values mode
            self.return_to_normal_mode()

        @self.kb.add("m", filter=Condition(lambda: self.flag_dataset_mode))
        def minimum_maximum(event):
            """Show the minimum and maximum values of a dataset."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            def run_in_thread():
                # Get the value string
                vmin, vmax = node.get_min_max()

                # Print the result on the main thread
                self.app.loop.call_soon_threadsafe(
                    self.print,
                    f"{node.path}: Minimum = {vmin},  Maximum = {vmax}",
                )

                # Exit values mode
                self.return_to_normal_mode()

            # Start the operation in a new thread
            threading.Thread(target=run_in_thread, daemon=True).start()

        @self.kb.add("M", filter=Condition(lambda: self.flag_dataset_mode))
        def mean(event):
            """Show the mean of a dataset."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            def run_in_thread():
                # Get the value string
                vmean = node.get_mean()

                # Print the result on the main thread
                self.app.loop.call_soon_threadsafe(
                    self.print,
                    f"{node.path}: Mean = {vmean}",
                )

                # Exit values mode
                self.return_to_normal_mode()

            # Start the operation in a new thread
            threading.Thread(target=run_in_thread, daemon=True).start()

        @self.kb.add("s", filter=Condition(lambda: self.flag_dataset_mode))
        def std(event):
            """Show the standard deviation of a dataset."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            def run_in_thread():
                # Get the value string
                vstd = node.get_std()

                # Print the result on the main thread
                self.app.loop.call_soon_threadsafe(
                    self.print,
                    f"{node.path}: Standard Deviation = {vstd}",
                )

                # Exit values mode
                self.return_to_normal_mode()

            # Start the operation in a new thread
            threading.Thread(target=run_in_thread, daemon=True).start()

    def _init_jump_bindings(self):
        """Set up the keybindings for the jump mode."""

        @self.kb.add("t", filter=Condition(lambda: self.flag_jump_mode))
        def jump_to_top(event):
            """Jump to the top of the tree."""
            self.set_cursor_position(self.tree.tree_text, new_cursor_pos=0)

            # Exit jump mode
            self.return_to_normal_mode()

        @self.kb.add("b", filter=Condition(lambda: self.flag_jump_mode))
        def jump_to_bottom(event):
            """Jump to the bottom of the tree."""
            self.set_cursor_position(
                self.tree.tree_text, new_cursor_pos=self.tree.length
            )

            # Exit jump mode
            self.return_to_normal_mode()

        @self.kb.add("p", filter=Condition(lambda: self.flag_jump_mode))
        def jump_to_parent(event):
            """Jump to the parent of the current node."""
            # Get the current node
            node = self.tree.get_current_node(self.current_row)

            # Get the node's parent
            parent = node.parent

            # if we're at the top, do nothing
            if parent is None:
                self.print(f"{node.path} is a root Group!")
                self.return_to_normal_mode()
                return

            # Get position of the first character in this row
            pos = self.current_position - self.current_column

            # Loop backwards until we hit the parent
            for row in range(self.current_row - 1, -1, -1):
                # Compute the position at this row
                pos -= len(self.tree.tree_text_split[row]) + 1

                # If we are at the parent stop
                if self.tree.get_current_node(row) is parent:
                    break

            # Safety check, avoid doing something stupid
            if pos < 0:
                pos = 0

            # Move the cursor
            self.set_cursor_position(self.tree.tree_text, pos)

            self.return_to_normal_mode()

        @self.kb.add("n", filter=Condition(lambda: self.flag_jump_mode))
        def jump_to_next(event):
            """Jump to the next node."""
            # Get the current node
            node = self.tree.get_current_node(self.current_row)

            # Get the depth of this node and the target depth
            depth = node.depth
            target_depth = depth - 1 if depth > 0 else 0

            # Get the position of the first character in this row
            pos = self.current_position - self.current_column

            # Do nothing if we are at the end
            if self.current_row == self.tree.height - 1:
                self.return_to_normal_mode()
                return

            # Loop forwards until we hit the next node at the level above
            # this node's depth. If at the root just move to the next
            # root group.
            for row in range(self.current_row, self.tree.height):
                # Compute the position at this row
                pos += len(self.tree.tree_text_split[row]) + 1

                # Ensure we don't over shoot
                if row + 1 > self.tree.height:
                    self.return_to_normal_mode()
                    return

                # If we are at the next node stop
                if self.tree.get_current_node(row + 1).depth == target_depth:
                    break

            # Move the cursor
            self.set_cursor_position(self.tree.tree_text, pos)

            self.return_to_normal_mode()

        @self.kb.add("k", filter=Condition(lambda: self.flag_jump_mode))
        def jump_to_key(event):
            """Jump to next key containing user input."""

            def jump_to_key_callback():
                """Jump to next key containing user input."""
                # Unpack user input
                key = self.user_input.strip()

                # Get the position of the first character in this row
                pos = self.current_position - self.current_column

                # Loop over keys until we find a key containing the
                # user input
                for row in range(self.current_row, self.tree.height):
                    # Compute the position at this row
                    pos += len(self.tree.tree_text_split[row]) + 1

                    # Ensure we don't over shoot
                    if row + 1 > self.tree.height - 1:
                        self.print("Couldn't find matching key!")
                        self.default_focus()
                        self.return_to_normal_mode()
                        return

                    # If we are at the next node stop
                    if key in self.tree.get_current_node(row + 1).name:
                        break

                # Return to normal
                self.default_focus()
                self.return_to_normal_mode()

                # Move the cursor
                self.set_cursor_position(self.tree.tree_text, pos)

            # Get the indices from the user
            self.input(
                "Jump to next key containing:",
                jump_to_key_callback,
            )

    def _init_window_bindings(self):
        """Set up the keybindings for the window mode."""

        @self.kb.add("t", filter=Condition(lambda: self.flag_window_mode))
        def move_tree(event):
            """Move focus to the tree."""
            self.shift_focus(self.tree_content)
            self.return_to_normal_mode()

        @self.kb.add("a", filter=Condition(lambda: self.flag_window_mode))
        def move_attr(event):
            """Move focus to the attributes."""
            self.shift_focus(self.attributes_content)
            self.return_to_normal_mode()

        @self.kb.add(
            "v",
            filter=Condition(
                lambda: self.flag_window_mode and self.flag_values_visible
            ),
        )
        def move_values(event):
            """Move focus to values."""
            self.shift_focus(self.values_content)
            self.return_to_normal_mode()

        @self.kb.add("p", filter=Condition(lambda: self.flag_window_mode))
        def move_plot(event):
            """Move focus to the plot."""
            self.shift_focus(self.plot_content)

            # Plotting is special case where we also want to enter plotting
            # mode
            self._flag_normal_mode = False
            self._flag_window_mode = False
            self._flag_plotting_mode = True

        @self.kb.add("h", filter=Condition(lambda: self.flag_window_mode))
        def move_hist(event):
            """Move focus to the plot."""
            self.shift_focus(self.hist_content)

            # Plotting is special case where we also want to enter plotting
            # mode
            self._flag_normal_mode = False
            self._flag_window_mode = False
            self._flag_hist_mode = True

        @self.kb.add("escape")
        def move_to_default(event):
            """
            Move focus to the default area.

            This is the tree content.
            """
            self.default_focus()
            self.return_to_normal_mode()

    def _init_plot_bindings(self):
        """Set up the keybindings for the plotting mode."""

        @self.kb.add("x", filter=Condition(lambda: self.flag_plotting_mode))
        def select_x(event):
            """Select the x-axis."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            self.plot_content.text = self.density_plotter.set_x_key(node)

            self.return_to_normal_mode()

        @self.kb.add("y", filter=Condition(lambda: self.flag_plotting_mode))
        def select_y(event):
            """Select the y-axis."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            self.plot_content.text = self.density_plotter.set_y_key(node)

            self.return_to_normal_mode()

        @self.kb.add("w", filter=Condition(lambda: self.flag_plotting_mode))
        def select_color(event):
            """Select the color-axis."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            self.plot_content.text = self.density_plotter.set_color_key(node)

            self.return_to_normal_mode()

        @self.kb.add(
            "enter",
            filter=Condition(
                lambda: self.app.layout.has_focus(self.plot_content)
            ),
        )
        def edit_plot_entry(event):
            """Edit plot param under cursor."""
            # Get the current position and row in the plot content
            current_row = self.plot_content.document.cursor_position_row
            current_pos = self.plot_content.document.cursor_position

            # Get the current row text  in the plot content split into
            # key and value
            split_line = self.density_plotter.get_row(current_row).split(": ")

            # Split the current plot content into lines
            split_text = self.plot_content.text.split("\n")

            def edit_plot_entry_callback():
                """Edit the plot param under cursor."""
                # Strip the user input
                user_input = self.user_input.strip()

                # And set the text here
                split_text[current_row] = (
                    f"{split_line[0]}:  ".ljust(13) + f"{user_input}"
                )

                # And display the new text
                self.plot_content.text = "\n".join(split_text)
                self.density_plotter.plot_text = self.plot_content.text

                # And shift focus back to the plot content
                self.shift_focus(self.plot_content)

                # And put the cursor back where it was
                self.plot_content.document = Document(
                    text=self.plot_content.text, cursor_position=current_pos
                )

            # Get the modified entry from the user
            self.input(split_line[0], edit_plot_entry_callback)

        @self.kb.add("c", filter=Condition(lambda: self.flag_plotting_mode))
        def get_count_density(event):
            """Get the count density of the dataset."""

            def run_in_thread():
                """Make the plot."""
                self.density_plotter.compute_counts(self.plot_content.text)

            threading.Thread(target=run_in_thread, daemon=True).start()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("s", filter=Condition(lambda: self.flag_plotting_mode))
        def get_sum_density(event):
            """Get the sum density of the dataset."""

            def run_in_thread():
                """Make the plot."""
                self.density_plotter.compute_sums(self.plot_content.text)

            threading.Thread(target=run_in_thread, daemon=True).start()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("m", filter=Condition(lambda: self.flag_plotting_mode))
        def get_mean_density(event):
            """Get the mean density of the dataset."""

            def run_in_thread():
                """Make the plot."""
                self.density_plotter.compute_means(self.plot_content.text)

            threading.Thread(target=run_in_thread, daemon=True).start()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("C", filter=Condition(lambda: self.flag_plotting_mode))
        def plot_count_density(event):
            """Plot and show pcolormesh with counts in bins."""
            self.density_plotter.plot_count_density(self.plot_content.text)

            # Show it (this resets the plotter class)
            self.density_plotter.show()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("S", filter=Condition(lambda: self.flag_plotting_mode))
        def plot_sum_density(event):
            """Plot and show pcolormesh with sum in bins."""
            # Make the plot
            self.density_plotter.plot_sum_density(self.plot_content.text)

            # Show it (this resets the plotter class)
            self.density_plotter.show()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("M", filter=Condition(lambda: self.flag_plotting_mode))
        def plot_mean_density(event):
            """Plot and show pcolormesh with mean in bins."""
            # Make the plot
            self.density_plotter.plot_mean_density(self.plot_content.text)

            # Show it (this resets the plotter class)
            self.density_plotter.show()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("c-c", filter=Condition(lambda: self.flag_plotting_mode))
        def save_count(event):
            """Plot and save the density count."""
            self.density_plotter.plot_count_density(self.plot_content.text)

            self.density_plotter.save()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("c-s", filter=Condition(lambda: self.flag_plotting_mode))
        def save_sum(event):
            """Plot and save the density sum."""
            self.density_plotter.plot_sum_density(self.plot_content.text)

            self.density_plotter.save()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("c-m", filter=Condition(lambda: self.flag_plotting_mode))
        def save_mean(event):
            """Plot and save the density mean."""
            self.density_plotter.plot_mean_density(self.plot_content.text)

            self.density_plotter.save()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("r", filter=Condition(lambda: self.flag_plotting_mode))
        def reset(event):
            """Reset the plot content."""
            self.plot_content.text = self.density_plotter.reset()

    def _init_hist_bindings(self):
        """Set up the bindings for histogram mode."""

        @self.kb.add("enter", filter=Condition(lambda: self.flag_hist_mode))
        def edit_hist_entry(event):
            """Edit histogram param under cursor."""
            # Get the current position and row in the plot content
            current_row = self.hist_content.document.cursor_position_row
            current_pos = self.hist_content.document.cursor_position

            # Get the current row text  in the plot content split into
            # key and value
            split_line = self.histogram_plotter.get_row(current_row).split(
                ": "
            )

            # Split the current plot content into lines
            split_text = self.hist_content.text.split("\n")

            def edit_hist_entry_callback():
                """Edit the plot param under cursor."""
                # Strip the user input
                user_input = self.user_input.strip()

                # And set the text here
                split_text[current_row] = (
                    f"{split_line[0]}:  ".ljust(13) + f"{user_input}"
                )

                # And display the new text
                self.hist_content.text = "\n".join(split_text)
                self.histogram_plotter.plot_text = self.hist_content.text

                # And shift focus back to the plot content
                self.shift_focus(self.hist_content)

                # And put the cursor back where it was
                self.hist_content.document = Document(
                    text=self.hist_content.text, cursor_position=current_pos
                )

            # Get the modified entry from the user
            self.input(split_line[0], edit_hist_entry_callback)

        @self.kb.add("d", filter=Condition(lambda: self.flag_hist_mode))
        def select_data(event):
            """Select the data to sort into bins."""
            # Get the node under the cursor
            node = self.tree.get_current_node(self.current_row)

            # Exit if the node is not a Dataset
            if node.is_group:
                self.print(f"{node.path} is not a Dataset")
                return

            # Set the text in the plotting area
            self.hist_content.text = self.histogram_plotter.set_data_key(node)

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("h", filter=Condition(lambda: self.flag_hist_mode))
        def compute_hist(event):
            """Compute the histogram."""

            def run_in_thread():
                """Make the plot."""
                self.histogram_plotter.compute_hist(self.hist_content.text)

            threading.Thread(target=run_in_thread, daemon=True).start()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("H", filter=Condition(lambda: self.flag_hist_mode))
        def plot_hist(event):
            """Plot the histogram."""
            self.histogram_plotter.plot_hist(self.hist_content.text)

            self.histogram_plotter.show()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("c-h", filter=Condition(lambda: self.flag_hist_mode))
        def save_hist(event):
            """Plot the histogram."""
            self.histogram_plotter.plot_hist(self.hist_content.text)

            self.histogram_plotter.save()

            self.return_to_normal_mode()
            self.default_focus()

        @self.kb.add("r", filter=Condition(lambda: self.flag_hist_mode))
        def reset_hist(event):
            """Reset the histogram content."""
            self.hist_content.text = self.histogram_plotter.reset()

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

        self.mini_buffer_content = TextArea(
            text=f"Welcome to h5forest! (v{__version__})",
            scrollbar=False,
            focusable=True,
            read_only=False,
        )

        self.input_buffer_content = TextArea(
            text="",
            scrollbar=False,
            focusable=False,
            read_only=True,
        )

        self.progress_bar_content = TextArea(
            text="",
            scrollbar=False,
            focusable=False,
            read_only=True,
        )

        self.plot_content = TextArea(
            text=self.density_plotter.default_plot_text,
            scrollbar=True,
            focusable=True,
            read_only=True,
        )

        self.hist_content = TextArea(
            text=self.histogram_plotter.default_plot_text,
            scrollbar=True,
            focusable=True,
            read_only=True,
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
                    self.tree.tree_text,
                    new_cursor_pos=self.tree.length
                    - len(self.tree.tree_text_split[self.tree.height - 1]),
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
        self.tree_frame = Frame(
            self.tree_content,
            title="HDF5 File Tree",
        )
        self.metadata_frame = Frame(
            self.metadata_content, title="Metadata", height=10
        )
        self.attrs_frame = Frame(self.attributes_content, title="Attributes")
        self.values_frame = Frame(
            self.values_content,
            title=self.value_title,
        )

        # Set up the mini buffer and input buffer
        self.mini_buffer = Frame(
            self.mini_buffer_content,
            height=3,
        )
        self.input_buffer = Frame(
            self.input_buffer_content,
            height=3,
        )
        self.input_buffer = ConditionalContainer(
            self.input_buffer,
            filter=Condition(lambda: len(self.input_buffer_content.text) > 0),
        )

        # Wrap those frames that need it in conditional containers
        self.values_frame = ConditionalContainer(
            content=self.values_frame,
            filter=Condition(lambda: self.flag_values_visible),
        )

        # Set up the hotkeys panel
        self.hotkeys_panel = HSplit(
            [
                ConditionalContainer(
                    content=self.hot_keys,
                    filter=Condition(lambda: self.flag_normal_mode),
                ),
                ConditionalContainer(
                    content=self.jump_keys,
                    filter=Condition(lambda: self.flag_jump_mode),
                ),
                ConditionalContainer(
                    content=self.dataset_keys,
                    filter=Condition(lambda: self.flag_dataset_mode),
                ),
                ConditionalContainer(
                    content=self.window_keys,
                    filter=Condition(lambda: self.flag_window_mode),
                ),
                ConditionalContainer(
                    content=self.plot_keys,
                    filter=Condition(lambda: self.flag_plotting_mode),
                ),
                ConditionalContainer(
                    content=self.hist_keys,
                    filter=Condition(lambda: self.flag_hist_mode),
                ),
            ]
        )
        self.hotkeys_frame = ConditionalContainer(
            Frame(self.hotkeys_panel, height=3),
            filter=Condition(
                lambda: self.flag_normal_mode
                or self.flag_jump_mode
                or self.flag_dataset_mode
                or self.flag_window_mode
                or self.flag_plotting_mode
                or self.flag_hist_mode
            ),
        )

        # Set up the plot frame
        self.plot_frame = ConditionalContainer(
            Frame(self.plot_content, title="Plotting", height=10),
            filter=Condition(
                lambda: self.flag_plotting_mode
                or len(self.density_plotter) > 0
            ),
        )

        # Set up the plot frame
        self.hist_frame = ConditionalContainer(
            Frame(self.hist_content, title="Histogram", height=10),
            filter=Condition(
                lambda: self.flag_hist_mode or len(self.histogram_plotter) > 0
            ),
        )

        # Set up the progress bar and buffer conditional containers
        self.progress_frame = ConditionalContainer(
            Frame(self.progress_bar_content, height=3),
            filter=Condition(lambda: self.flag_progress_bar),
        )
        buffers = HSplit([self.input_buffer, self.mini_buffer])

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
                            HSplit(
                                [
                                    self.attrs_frame,
                                    self.values_frame,
                                    self.plot_frame,
                                    self.hist_frame,
                                ]
                            ),
                        ]
                    ),
                    self.hotkeys_frame,
                    self.progress_frame,
                    buffers,
                ]
            )
        )

    def print(self, *args):
        """Print a single line to the mini buffer."""
        args = [str(a) for a in args]
        self.mini_buffer_content.text = " ".join(args)
        self.app.invalidate()

    def input(self, prompt, callback, mini_buffer_text=""):
        """
        Accept input from the user.

        Note, this is pretty hacky! It will store the input into
        self.user_input which will then be processed by the passed
        callback function. This call back function must take self as
        its only argument and it must safely process the input handling
        possible errors gracefully.

        Args:
            prompt (str):
                The string/s to print to the mini buffer.
            callback (function):
                The function using user input.
        """
        # Prepare to recieve an input
        self.user_input = None

        # Set the input read-only text
        self.input_buffer_content.text = prompt
        self.mini_buffer_content.text = mini_buffer_text
        self.app.invalidate()

        # Shift focus to the mini buffer to await input
        self.shift_focus(self.mini_buffer_content)

        def on_enter(event):
            """Take the users input and process it."""
            # Read the text from the mini_buffer_content TextArea
            self.user_input = self.mini_buffer_content.text

            # Clear buffers_content TextArea after processing
            self.input_buffer_content.text = ""

            # Run the callback function
            callback()

        # Add a temporary keybinding for Enter specific to this input action
        self.kb.add(
            "enter",
            filter=Condition(
                lambda: self.app.layout.has_focus(self.mini_buffer_content)
            ),
        )(on_enter)

        # Update the app
        get_app().invalidate()

    def default_focus(self):
        """Shift the focus to the tree."""
        self.app.layout.focus(self.tree_content)

    def shift_focus(self, focused_area):
        """
        Shift the focus to a different area.

        Args:
            focused_area (TextArea):
                The text area to focus on.
        """
        self.app.layout.focus(focused_area)


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
