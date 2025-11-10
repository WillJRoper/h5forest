"""The main application for the HDF5 Forest.

This application provides a CLI application for exploring HDF5 files. This is
enabled by the h5forest entry point set up when the package is installed.

Example Usage:
    h5forest /path/to/file.hdf5

"""

import sys
import threading

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ConditionalContainer, HSplit, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.widgets import Frame, TextArea

from h5forest._version import __version__
from h5forest.bindings import (
    _init_app_bindings,
    _init_dataset_bindings,
    _init_goto_bindings,
    _init_hist_bindings,
    _init_plot_bindings,
    _init_search_bindings,
    _init_tree_bindings,
    _init_window_bindings,
)
from h5forest.plotting import HistogramPlotter, ScatterPlotter
from h5forest.styles import style
from h5forest.tree import Tree, TreeProcessor
from h5forest.utils import DynamicLabelLayout, DynamicTitle, get_window_size


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

        # Set up the tree processor
        self.tree_processor = TreeProcessor(self.tree)

        # Define flags we need to control behaviour
        self.flag_values_visible = False
        self.flag_progress_bar = False
        self.flag_expanded_attrs = False

        # Define the leader key mode flags
        # NOTE: These must be unset when the leader mode is exited, and in
        # _flag_normal_mode when the escape key is pressed
        self._flag_normal_mode = True
        self._flag_jump_mode = False
        self._flag_dataset_mode = False
        self._flag_window_mode = False
        self._flag_plotting_mode = False
        self._flag_hist_mode = False
        self._flag_search_mode = False

        # Timer for debouncing search input
        self.search_timer = None

        # Set up the main app and tree bindings. Store the raw label
        # dicts/lists so we can filter them dynamically using property methods
        self.kb = KeyBindings()
        self._app_keys_dict = _init_app_bindings(self)
        self._tree_keys_dict = _init_tree_bindings(self)
        self._dataset_keys_list = _init_dataset_bindings(self)
        self._goto_keys_list = _init_goto_bindings(self)
        self._window_keys_dict = _init_window_bindings(self)
        self._plot_keys_dict = _init_plot_bindings(self)
        self._hist_keys_dict = _init_hist_bindings(self)
        self._search_keys_list = _init_search_bindings(self)

        # Attributes for dynamic titles
        self.value_title = DynamicTitle("Values")
        self.mode_title = DynamicTitle("Normal Mode")

        # Attach the hexbin plotter
        self.scatter_plotter = ScatterPlotter()
        self.histogram_plotter = HistogramPlotter()

        # Set up the text areas that will populate the layout
        self.tree_buffer = None
        self.tree_content = None
        self.metadata_content = None
        self.attributes_content = None
        self.values_content = None
        self.mini_buffer_content = None
        self.progress_bar_content = None
        self.plot_content = None
        self.hist_content = None
        self._init_text_areas()

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
        self.hotkeys_panel = None
        self.layout = None
        self._init_layout()

        # Intialise a container for user input
        self.user_input = None

        # With all that done we can set up the application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=False,
            style=style,
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
        doc = self.tree_buffer.document

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
        doc = self.tree_buffer.document

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
        return self.tree_buffer.document.cursor_position

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

    @property
    def flag_search_mode(self):
        """
        Return the search mode flag.

        This accounts for whether we are in search mode and the search
        buffer has focus.

        Returns:
            bool:
                The flag for search mode.
        """
        return self._flag_search_mode and self.app.layout.has_focus(
            self.search_content
        )

    def _get_hot_keys(self):
        """
        Get the hot keys for normal mode based on current state.

        Returns:
            list: List of Label widgets.
        """
        labels = []

        # Always show Enter to open group in normal mode
        labels.append(self._tree_keys_dict["open_group"])

        # Mode-switching keys
        labels.append(self._app_keys_dict["dataset_mode"])
        labels.append(self._app_keys_dict["goto_mode"])
        labels.append(self._app_keys_dict["hist_mode"])
        labels.append(self._app_keys_dict["plotting_mode"])
        labels.append(self._app_keys_dict["window_mode"])
        labels.append(self._app_keys_dict["search"])

        # Other hot keys
        labels.append(self._tree_keys_dict["move_ten"])

        if not self.flag_expanded_attrs:
            labels.append(self._app_keys_dict["expand_attrs"])
        else:
            labels.append(self._app_keys_dict["shrink_attrs"])

        labels.append(self._app_keys_dict["restore_tree"])
        labels.append(self._app_keys_dict["exit"])

        return labels

    @property
    def hot_keys(self):
        """
        Return the hot keys for normal mode, filtered based on current state.

        This combines app and tree keys and filters based on flags like
        flag_expanded_attrs and tree focus.

        Returns:
            DynamicLabelLayout: Layout with filtered labels.
        """
        return DynamicLabelLayout(self._get_hot_keys)

    def _get_dataset_keys(self):
        """Get the hot keys for dataset mode."""
        return self._dataset_keys_list

    @property
    def dataset_keys(self):
        """
        Return the hot keys for dataset mode.

        No filtering needed for dataset mode.

        Returns:
            DynamicLabelLayout: Layout with dataset labels.
        """
        return DynamicLabelLayout(self._get_dataset_keys)

    def _get_goto_keys(self):
        """Get the hot keys for goto mode."""
        return self._goto_keys_list

    @property
    def goto_keys(self):
        """
        Return the hot keys for goto mode.

        No filtering needed for goto mode.

        Returns:
            DynamicLabelLayout: Layout with goto labels.
        """
        return DynamicLabelLayout(self._get_goto_keys)

    def _get_window_keys(self):
        """
        Get the hot keys for window mode based on current state.

        Returns:
            list: List of Label widgets.
        """
        labels = []

        # Check if app exists (it won't during initialization)
        has_app = hasattr(self, "app") and self.app is not None

        # Show "move to X" only if not already focused on X
        if not has_app or not self.app.layout.has_focus(self.tree_content):
            labels.append(self._window_keys_dict["move_tree"])

        if not has_app or not self.app.layout.has_focus(
            self.attributes_content
        ):
            labels.append(self._window_keys_dict["move_attrs"])

        if self.flag_values_visible and (
            not has_app or not self.app.layout.has_focus(self.values_content)
        ):
            labels.append(self._window_keys_dict["move_values"])

        if not has_app or not self.app.layout.has_focus(self.plot_content):
            labels.append(self._window_keys_dict["move_plot"])

        if not has_app or not self.app.layout.has_focus(self.hist_content):
            labels.append(self._window_keys_dict["move_hist"])

        labels.append(self._window_keys_dict["exit"])

        return labels

    @property
    def window_keys(self):
        """
        Return the hot keys for window mode, filtered based on current state.

        Filters based on focus and flag_values_visible.

        Returns:
            DynamicLabelLayout: Layout with filtered labels.
        """
        return DynamicLabelLayout(self._get_window_keys)

    def _get_plot_keys(self):
        """
        Get the hot keys for plotting mode, filtered based on current state.

        Returns:
            list: List of Label widgets for current state.
        """
        labels = []

        # Check if app exists (it won't during initialization)
        has_app = hasattr(self, "app") and self.app is not None

        # If config panel is focused, show only config-specific keys
        if has_app and self.app.layout.has_focus(self.plot_content):
            labels.append(self._plot_keys_dict["edit_tree"])
            labels.append(self._plot_keys_dict["edit_entry"])
            labels.append(self._plot_keys_dict["exit_config"])
            return labels

        # Otherwise show full tree view keys
        labels.append(self._plot_keys_dict["edit_config"])

        # Show axis selection only if not already set
        if "x" not in self.scatter_plotter.plot_params:
            labels.append(self._plot_keys_dict["select_x"])

        if "y" not in self.scatter_plotter.plot_params:
            labels.append(self._plot_keys_dict["select_y"])

        # Show scale toggles
        labels.append(self._plot_keys_dict["toggle_x_scale"])
        labels.append(self._plot_keys_dict["toggle_y_scale"])

        # Show plot/save only if there are params
        if len(self.scatter_plotter) > 0:
            labels.append(self._plot_keys_dict["plot"])
            labels.append(self._plot_keys_dict["save_plot"])

        labels.append(self._plot_keys_dict["reset"])
        labels.append(self._plot_keys_dict["exit_mode"])

        return labels

    @property
    def plot_keys(self):
        """
        Return the hot keys for plotting mode, filtered based on current state.

        Filters based on plot_params and focus.

        Returns:
            DynamicLabelLayout: Layout with filtered labels.
        """
        return DynamicLabelLayout(self._get_plot_keys)

    def _get_hist_keys(self):
        """
        Get the hot keys for histogram mode, filtered on current state.

        Returns:
            list: List of Label widgets for current state.
        """
        labels = []

        # Check if app exists (it won't during initialization)
        has_app = hasattr(self, "app") and self.app is not None

        # If config panel is focused, show only config-specific keys
        if has_app and self.app.layout.has_focus(self.hist_content):
            labels.append(self._hist_keys_dict["edit_tree"])
            labels.append(self._hist_keys_dict["edit_entry"])
            labels.append(self._hist_keys_dict["exit_config"])
            return labels

        # Otherwise show full tree view keys
        labels.append(self._hist_keys_dict["edit_config"])
        labels.append(self._hist_keys_dict["select_data"])
        labels.append(self._hist_keys_dict["edit_bins"])
        labels.append(self._hist_keys_dict["toggle_x_scale"])
        labels.append(self._hist_keys_dict["toggle_y_scale"])
        labels.append(self._hist_keys_dict["show_hist"])
        labels.append(self._hist_keys_dict["save_hist"])
        labels.append(self._hist_keys_dict["reset"])
        labels.append(self._hist_keys_dict["exit_mode"])

        return labels

    @property
    def hist_keys(self):
        """
        Return the hot keys for histogram mode, filtered on current state.

        Filters based on plot_params and focus.

        Returns:
            DynamicLabelLayout: Layout with filtered labels.
        """
        return DynamicLabelLayout(self._get_hist_keys)

    def _get_search_keys(self):
        """Get the hot keys for search mode."""
        return self._search_keys_list

    @property
    def search_keys(self):
        """
        Return the hot keys for search mode.

        No filtering needed for search mode.

        Returns:
            DynamicLabelLayout: Layout with search labels.
        """
        return DynamicLabelLayout(self._get_search_keys)

    def return_to_normal_mode(self):
        """Return to normal mode."""
        self._flag_normal_mode = True
        self._flag_jump_mode = False
        self._flag_dataset_mode = False
        self._flag_window_mode = False
        self._flag_plotting_mode = False
        self._flag_hist_mode = False
        self._flag_search_mode = False
        self.mode_title.update_title("Normal Mode")

    def _init_text_areas(self):
        """Initialise the content for each frame."""
        # Buffer for the tree content itself
        self.tree_buffer = Buffer(
            on_cursor_position_changed=self.cursor_moved_action,
            read_only=True,
        )

        # Set the text of the buffer
        self.tree_buffer.set_document(
            Document(
                text=self.tree.get_tree_text(),
                cursor_position=0,
            ),
            bypass_readonly=True,
        )

        self.tree_content = Window(
            content=BufferControl(
                buffer=self.tree_buffer,
                input_processors=[self.tree_processor],
                focusable=True,
            ),
        )
        self.tree_content.content.mouse_handler = self._create_mouse_handler(
            self.tree_content
        )

        # Get the root node, we'll need to to populate the initial metadata
        # and attributes
        root_node = self.tree.root

        self.metadata_content = TextArea(
            text="Metadata details here...",
            scrollbar=False,
            focusable=False,
            read_only=True,
        )
        self.metadata_content.text = root_node.get_meta_text()

        self.attributes_content = TextArea(
            text="Attributes here...",
            read_only=True,
            scrollbar=True,
            focusable=True,
        )
        self.attributes_content.text = root_node.get_attr_text()
        self.attributes_content.control.mouse_handler = (
            self._create_mouse_handler(self.attributes_content)
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

        # A buffer that will be used for searching
        self.search_content = TextArea(
            text="",
            scrollbar=False,
            focusable=True,
            read_only=False,
            height=1,
            multiline=False,
        )
        # Attach on_text_changed handler for real-time search
        self.search_content.buffer.on_text_changed += (
            self._on_search_text_changed
        )

        self.plot_content = TextArea(
            text=self.scatter_plotter.default_plot_text,
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
        self.tree_buffer.set_document(
            Document(text=text, cursor_position=new_cursor_pos),
            bypass_readonly=True,
        )

    def cursor_moved_action(self, event):
        """
        Apply changes when the cursor has been moved.

        This will update the metadata and attribute outputs to display
        what is currently under the cursor.
        """
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

        def tree_width():
            """Return the width of the tree."""
            # If values, hist, or plot are visible, the tree should fill half
            # the full width
            if self.flag_values_visible:
                return columns // 2
            elif self.flag_plotting_mode or len(self.scatter_plotter) > 0:
                return columns // 2
            elif self.flag_hist_mode or len(self.histogram_plotter) > 0:
                return columns // 2
            elif self.flag_expanded_attrs:
                return columns // 2
            else:
                return columns

        # Create each individual element of the UI before packaging it
        # all into the layout
        self.tree_frame = Frame(
            self.tree_content,
            title="HDF5 File Tree",
            width=tree_width,
        )

        # Set up the metadata and attributes frames with their shared height
        # function controlling their height (these are placed next to each
        # other in a VSplit below)
        self.metadata_frame = Frame(
            self.metadata_content,
            title="Metadata",
            height=10,
        )
        self.attrs_frame = ConditionalContainer(
            Frame(
                self.attributes_content,
                title="Attributes",
                height=10,
                width=columns // 2,
            ),
            filter=Condition(lambda: not self.flag_expanded_attrs),
        )
        self.expanded_attrs_frame = ConditionalContainer(
            Frame(
                self.attributes_content,
                title="Attributes",
                width=columns // 2,
            ),
            filter=Condition(lambda: self.flag_expanded_attrs),
        )

        # Set up the values frame (this is where we'll display the values of
        # a dataset)
        self.values_frame = Frame(
            self.values_content,
            title=self.value_title,
        )

        # Set up the mini buffer and input buffer (these are where we'll
        # display messages to the user and accept input)
        self.mini_buffer = Frame(
            self.mini_buffer_content,
            height=3,
        )
        self.input_buffer = ConditionalContainer(
            Frame(
                self.input_buffer_content,
                height=3,
            ),
            filter=Condition(lambda: len(self.input_buffer_content.text) > 0),
        )

        # Search buffer
        self.search_buffer = ConditionalContainer(
            Frame(
                self.search_content,
                height=3,
            ),
            filter=Condition(lambda: self._flag_search_mode),
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
                    content=self.goto_keys,
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
                ConditionalContainer(
                    content=self.search_keys,
                    filter=Condition(lambda: self.flag_search_mode),
                ),
            ]
        )
        self.hotkeys_frame = ConditionalContainer(
            Frame(self.hotkeys_panel, title=self.mode_title),
            filter=Condition(
                lambda: self.flag_normal_mode
                or self.flag_jump_mode
                or self.flag_dataset_mode
                or self.flag_window_mode
                or self.flag_plotting_mode
                or self.flag_hist_mode
                or self.flag_search_mode
            ),
        )

        # Set up the plot frame
        self.plot_frame = ConditionalContainer(
            Frame(
                self.plot_content,
                title="Plotting",
            ),
            filter=Condition(
                lambda: self.flag_plotting_mode
                or len(self.scatter_plotter) > 0
            ),
        )

        # Set up the plot frame
        self.hist_frame = ConditionalContainer(
            Frame(
                self.hist_content,
                title="Histogram",
            ),
            filter=Condition(
                lambda: self.flag_hist_mode or len(self.histogram_plotter) > 0
            ),
        )

        # Set up the progress bar and buffer conditional containers
        self.progress_frame = ConditionalContainer(
            Frame(self.progress_bar_content, height=3),
            filter=Condition(lambda: self.flag_progress_bar),
        )
        buffers = HSplit(
            [
                self.input_buffer,
                self.mini_buffer,
                self.search_buffer,
            ]
        )

        # Layout using split views
        self.layout = Layout(
            HSplit(
                [
                    VSplit(
                        [
                            self.tree_frame,
                            HSplit(
                                [
                                    self.expanded_attrs_frame,
                                    self.values_frame,
                                    self.plot_frame,
                                    self.hist_frame,
                                ],
                                width=Dimension(min=0, max=columns // 2),
                            ),
                        ]
                    ),
                    VSplit(
                        [
                            self.metadata_frame,
                            self.attrs_frame,
                        ],
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
        # Store the current focus
        current_focus = self.app.layout.current_window

        # Prepare to recieve an input
        self.user_input = None

        # Set the input read-only text
        self.input_buffer_content.text = prompt
        self.mini_buffer_content.document = Document(
            mini_buffer_text, cursor_position=len(mini_buffer_text)
        )
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

        def on_esc(event):
            """Return to normal mode."""
            # Clear buffers_content TextArea after processing
            self.input_buffer_content.text = ""
            self.return_to_normal_mode()
            self.shift_focus(current_focus)

        # Add a temporary keybinding for Enter specific to this input action
        self.kb.add(
            "enter",
            filter=Condition(
                lambda: self.app.layout.has_focus(self.mini_buffer_content)
            ),
        )(on_enter)
        self.kb.add(
            "escape",
            filter=Condition(
                lambda: self.app.layout.has_focus(self.mini_buffer_content)
            ),
        )(on_esc)

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
        self.update_hotkeys_panel()

    def update_hotkeys_panel(self):
        """
        Update the hotkeys panel to reflect current focus and state.

        This method reconstructs the hotkeys panel content based on the
        current mode and focus state. It should be called whenever focus
        changes or when the displayed hotkeys need to be refreshed.
        """
        # Reconstruct the hotkeys panel with fresh label layouts
        from prompt_toolkit.filters import Condition
        from prompt_toolkit.layout.containers import ConditionalContainer

        self.hotkeys_panel.children = [
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_hot_keys),
                filter=Condition(lambda: self.flag_normal_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_goto_keys),
                filter=Condition(lambda: self.flag_jump_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_dataset_keys),
                filter=Condition(lambda: self.flag_dataset_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_window_keys),
                filter=Condition(lambda: self.flag_window_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_plot_keys),
                filter=Condition(lambda: self.flag_plotting_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_hist_keys),
                filter=Condition(lambda: self.flag_hist_mode),
            ),
            ConditionalContainer(
                content=DynamicLabelLayout(self._get_search_keys),
                filter=Condition(lambda: self.flag_search_mode),
            ),
        ]

        # Force a redraw of the interface to reflect updated hotkeys
        if hasattr(self, "app") and self.app is not None:
            self.app.invalidate()

    def _create_mouse_handler(self, content_area):
        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                get_app().layout.focus(content_area)

        return mouse_handler

    def _on_search_text_changed(self, event):
        """
        Handle search text changes for real-time filtering with debouncing.

        This is called whenever the user types in the search buffer.
        It debounces the search to avoid excessive filtering while typing.
        """
        # Only filter if we're actually in search mode
        if not self._flag_search_mode:
            return

        # Cancel any existing timer
        if self.search_timer is not None:
            self.search_timer.cancel()

        # Define the search function to execute after delay
        def perform_search():
            # Get the current search query
            query = self.search_content.text

            # Filter the tree based on the query
            filtered_text = self.tree.filter_tree(query)

            # Update the tree display on the main thread
            self.app.loop.call_soon_threadsafe(
                lambda: self._update_search_display(filtered_text)
            )

        # Schedule the search to run after 50ms
        self.search_timer = threading.Timer(0.05, perform_search)
        self.search_timer.daemon = True
        self.search_timer.start()

    def _update_search_display(self, filtered_text):
        """Update the tree display with filtered results."""
        self.tree_buffer.set_document(
            Document(text=filtered_text, cursor_position=0),
            bypass_readonly=True,
        )
        get_app().invalidate()


def main():
    """Initialise and run the application."""
    # First port of call, check we have been given a valid input
    if len(sys.argv) != 2:
        print("Usage: h5forest /path/to/file.hdf5")
        sys.exit(1)

    # Extract the filepath
    filepath = sys.argv[1]

    # Set up the app
    app = H5Forest(filepath)

    # Lets get going!
    app.run()
