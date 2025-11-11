"""Unit tests for h5forest.h5_forest module - H5Forest main application."""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.mouse_events import MouseEventType


@pytest.fixture(autouse=True)
def mock_window_size():
    """Mock get_window_size for all tests in this module."""
    with patch("h5forest.h5_forest.get_window_size", return_value=(24, 80)):
        yield


class TestH5ForestSingleton:
    """Test H5Forest singleton pattern."""

    def test_singleton_creates_single_instance(self, temp_h5_file):
        """Test that H5Forest implements singleton pattern."""
        from h5forest.h5_forest import H5Forest

        # Create first instance
        app1 = H5Forest(temp_h5_file)
        # Create second instance
        app2 = H5Forest(temp_h5_file)

        # Should be the same instance
        assert app1 is app2

    def test_singleton_only_initializes_once(self, temp_h5_file):
        """Test that singleton only calls _init once."""
        from h5forest.h5_forest import H5Forest

        with patch.object(H5Forest, "_init") as mock_init:
            # Create first instance
            H5Forest(temp_h5_file)
            # Create second instance
            H5Forest(temp_h5_file)

            # _init should only be called once
            assert mock_init.call_count == 1


class TestH5ForestInitialization:
    """Test H5Forest initialization."""

    def test_init_creates_tree(self, temp_h5_file):
        """Test that initialization creates a Tree object."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.tree is not None
        assert hasattr(app.tree, "root")

    def test_init_creates_tree_processor(self, temp_h5_file):
        """Test that initialization creates a TreeProcessor."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.tree_processor is not None
        assert app.tree_processor.tree == app.tree

    def test_init_sets_flags(self, temp_h5_file):
        """Test that initialization sets all flags correctly."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Check all flags are set
        assert app.flag_values_visible is False
        assert app.flag_progress_bar is False
        assert app.flag_expanded_attrs is False
        assert app._flag_normal_mode is True
        assert app._flag_jump_mode is False
        assert app._flag_dataset_mode is False
        assert app._flag_window_mode is False
        assert app._flag_plotting_mode is False
        assert app._flag_hist_mode is False
        assert app._flag_search_mode is False

    def test_init_creates_keybindings(self, temp_h5_file):
        """Test that initialization creates KeyBindings."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert isinstance(app.kb, KeyBindings)
        assert app.hot_keys is not None
        assert app.dataset_keys is not None
        assert app.goto_keys is not None
        assert app.window_keys is not None
        assert app.plot_keys is not None
        assert app.hist_keys is not None
        assert app.search_keys is not None

    def test_init_creates_plotters(self, temp_h5_file):
        """Test that initialization creates plotter objects."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.scatter_plotter is not None
        assert app.histogram_plotter is not None

    def test_init_creates_text_areas(self, temp_h5_file):
        """Test that initialization creates all text areas."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.tree_buffer is not None
        assert app.tree_content is not None
        assert app.metadata_content is not None
        assert app.attributes_content is not None
        assert app.values_content is not None
        assert app.mini_buffer_content is not None
        assert app.progress_bar_content is not None
        assert app.plot_content is not None
        assert app.hist_content is not None

    def test_init_creates_frames(self, temp_h5_file):
        """Test that initialization creates all frames."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.tree_frame is not None
        assert app.metadata_frame is not None
        assert app.attrs_frame is not None
        assert app.values_frame is not None
        assert app.plot_frame is not None
        assert app.hist_frame is not None
        assert app.hotkeys_panel is not None

    def test_init_creates_application(self, temp_h5_file):
        """Test that initialization creates Application object."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.app is not None
        assert app.layout is not None

    def test_prev_row_initialized_to_none(self, temp_h5_file):
        """Test that prev_row is initialized to None."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.prev_row is None

    def test_user_input_initialized_to_none(self, temp_h5_file):
        """Test that user_input is initialized to None."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        assert app.user_input is None


class TestH5ForestRun:
    """Test H5Forest run method."""

    def test_run_calls_app_run(self, temp_h5_file):
        """Test that run method calls app.run()."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.run = MagicMock()

        app.run()

        app.app.run.assert_called_once()


class TestH5ForestProperties:
    """Test H5Forest property methods."""

    def test_current_row_property(self, temp_h5_file):
        """Test current_row property."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Create simple text: "a\nb\nc" (3 rows)
        # Row 0: "a" (position 0)
        # Row 1: "b" (position 2, after "a\n")
        # Row 2: "c" (position 4, after "a\nb\n")
        text = "a\nb\nc"
        # Position cursor at row 2 (position 4)
        doc = Document(text, cursor_position=4)
        app.tree_buffer.set_document(doc, bypass_readonly=True)

        assert app.current_row == 2

    def test_current_column_property(self, temp_h5_file):
        """Test current_column property."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Set cursor at column 10 of first line
        text = "0123456789ABCDEFGHIJ"
        doc = Document(text, cursor_position=10)
        app.tree_buffer.set_document(doc, bypass_readonly=True)

        assert app.current_column == 10

    def test_current_position_property(self, temp_h5_file):
        """Test current_position property."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Set cursor at position 100
        text = "x" * 200
        doc = Document(text, cursor_position=100)
        app.tree_buffer.set_document(doc, bypass_readonly=True)

        assert app.current_position == 100

    def test_flag_normal_mode_property_true(self, temp_h5_file):
        """Test flag_normal_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_normal_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_normal_mode is True

    def test_flag_normal_mode_property_false_when_focused(self, temp_h5_file):
        """Test flag_normal_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_normal_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_normal_mode is False

    def test_flag_jump_mode_property_true(self, temp_h5_file):
        """Test flag_jump_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_jump_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_jump_mode is True

    def test_flag_jump_mode_property_false_when_focused(self, temp_h5_file):
        """Test flag_jump_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_jump_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_jump_mode is False

    def test_flag_dataset_mode_property_true(self, temp_h5_file):
        """Test flag_dataset_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_dataset_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_dataset_mode is True

    def test_flag_dataset_mode_property_false_when_focused(self, temp_h5_file):
        """Test flag_dataset_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_dataset_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_dataset_mode is False

    def test_flag_window_mode_property_true(self, temp_h5_file):
        """Test flag_window_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_window_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_window_mode is True

    def test_flag_window_mode_property_false_when_focused(self, temp_h5_file):
        """Test flag_window_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_window_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_window_mode is False

    def test_flag_plotting_mode_property_true(self, temp_h5_file):
        """Test flag_plotting_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_plotting_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_plotting_mode is True

    def test_flag_plotting_mode_property_false_when_focused(
        self, temp_h5_file
    ):
        """Test flag_plotting_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_plotting_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_plotting_mode is False

    def test_flag_hist_mode_property_true(self, temp_h5_file):
        """Test flag_hist_mode property when mini buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_hist_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_hist_mode is True

    def test_flag_hist_mode_property_false_when_focused(self, temp_h5_file):
        """Test flag_hist_mode property when mini buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_hist_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_hist_mode is False

    def test_flag_search_mode_property_true(self, temp_h5_file):
        """Test flag_search_mode property when search buffer is focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_search_mode = True
        app.app.layout.has_focus = MagicMock(return_value=True)

        assert app.flag_search_mode is True

    def test_flag_search_mode_property_false_when_not_focused(
        self, temp_h5_file
    ):
        """Test flag_search_mode property when search buffer not focused."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_search_mode = True
        app.app.layout.has_focus = MagicMock(return_value=False)

        assert app.flag_search_mode is False


class TestH5ForestModeManagement:
    """Test H5Forest mode management."""

    def test_return_to_normal_mode(self, temp_h5_file):
        """Test return_to_normal_mode resets all flags."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Set some flags to non-normal state
        app._flag_normal_mode = False
        app._flag_jump_mode = True
        app._flag_dataset_mode = True
        app._flag_window_mode = True
        app._flag_plotting_mode = True
        app._flag_hist_mode = True
        app._flag_search_mode = True

        # Return to normal mode
        app.return_to_normal_mode()

        # Check all flags reset
        assert app._flag_normal_mode is True
        assert app._flag_jump_mode is False
        assert app._flag_dataset_mode is False
        assert app._flag_window_mode is False
        assert app._flag_plotting_mode is False
        assert app._flag_hist_mode is False
        assert app._flag_search_mode is False


class TestH5ForestCursorOperations:
    """Test H5Forest cursor operations."""

    def test_set_cursor_position(self, temp_h5_file):
        """Test set_cursor_position updates cursor."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        text = "line1\nline2\nline3"
        new_pos = 10

        app.set_cursor_position(text, new_pos)

        # Verify document was updated
        assert app.tree_buffer.document.text == text
        assert app.tree_buffer.document.cursor_position == new_pos

    def test_cursor_moved_action_successful(self, temp_h5_file):
        """Test cursor_moved_action when node exists."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Use the actual tree nodes that were created
        if len(app.tree.nodes_by_row) > 0:
            # Create mock event
            mock_event = Mock()

            # The cursor starts at row 0, so cursor_moved_action should work

            # Call cursor_moved_action
            app.cursor_moved_action(mock_event)

            # Metadata should still be set (might be same as initial)
            assert app.metadata_content.text is not None
            assert app.attributes_content.text is not None

    def test_cursor_moved_action_index_error(self, temp_h5_file):
        """Test cursor_moved_action when IndexError occurs."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Mock tree to raise IndexError
        app.tree.get_current_node = MagicMock(side_effect=IndexError)
        app.tree.tree_text = "line1\nline2\nline3"
        app.tree.tree_text_split = ["line1", "line2", "line3"]
        # Mock the height property
        with patch.object(
            type(app.tree),
            "height",
            new_callable=lambda: property(lambda self: 3),
        ):
            # Mock set_cursor_position
            app.set_cursor_position = MagicMock()

            # Create mock event
            mock_event = Mock()

            # Call cursor_moved_action
            app.cursor_moved_action(mock_event)

            # Verify cursor was repositioned (should be called)
            assert app.set_cursor_position.called

            # Verify text was cleared
            assert app.metadata_content.text == ""
            assert app.attributes_content.text == ""


class TestH5ForestLayout:
    """Test H5Forest layout functionality."""

    def test_layout_with_values_visible(self, temp_h5_file):
        """Test layout when values are visible."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Enable values and trigger layout rebuild
        app.flag_values_visible = True
        app._init_layout()

        # Verify layout still exists
        assert app.layout is not None
        assert app.tree_frame is not None
        assert app.values_frame is not None

    def test_layout_with_plotting_mode(self, temp_h5_file):
        """Test layout when plotting mode is active."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Enable plotting mode and trigger layout rebuild
        app._flag_plotting_mode = True
        app._init_layout()

        # Verify layout components exist
        assert app.layout is not None
        assert app.plot_frame is not None

    def test_layout_with_scatter_plot(self, temp_h5_file):
        """Test layout when scatter plot exists."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Add data to scatter plotter and rebuild layout
        app.scatter_plotter.x_data = [1, 2, 3]
        app.scatter_plotter.y_data = [1, 2, 3]
        app._init_layout()

        # Verify scatter plotter exists and has the attributes
        assert hasattr(app.scatter_plotter, "x_data")
        assert hasattr(app.scatter_plotter, "y_data")

    def test_layout_with_hist_mode(self, temp_h5_file):
        """Test layout when histogram mode is active."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Enable hist mode and trigger layout rebuild
        app._flag_hist_mode = True
        app._init_layout()

        # Verify layout components exist
        assert app.layout is not None
        assert app.hist_frame is not None

    def test_layout_with_histogram(self, temp_h5_file):
        """Test layout when histogram exists."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Verify histogram plotter exists
        assert app.histogram_plotter is not None

    def test_layout_with_expanded_attrs(self, temp_h5_file):
        """Test layout when attributes are expanded."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Enable expanded attrs and trigger layout rebuild
        app.flag_expanded_attrs = True
        app._init_layout()

        # Verify layout components exist
        assert app.layout is not None
        assert app.expanded_attrs_frame is not None

    def test_tree_width_calculation(self, temp_h5_file):
        """Test tree_width closure with different visibility flags."""
        from unittest.mock import patch

        from h5forest.h5_forest import H5Forest

        # Mock get_window_size to return known values
        with patch("h5forest.h5_forest.get_window_size") as mock_size:
            mock_size.return_value = (100, 40)  # 100 rows, 40 columns

            # Test with flag_values_visible
            app = H5Forest(temp_h5_file)
            app.flag_values_visible = True
            app._init_layout()
            # Width function is stored in container
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20  # 40 columns // 2

            # Test with flag_plotting_mode (property accessor)
            app = H5Forest(temp_h5_file)
            app._flag_plotting_mode = True
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20

            # Test with scatter_plotter having data (len > 0)
            app = H5Forest(temp_h5_file)
            app.scatter_plotter.plot_params = {"x": "test"}
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20

            # Test with flag_hist_mode (property accessor)
            app = H5Forest(temp_h5_file)
            app._flag_hist_mode = True
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20

            # Test with histogram_plotter having data
            app = H5Forest(temp_h5_file)
            app.histogram_plotter.plot_params = {"data": "test"}
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20

            # Test with flag_expanded_attrs
            app = H5Forest(temp_h5_file)
            app.flag_expanded_attrs = True
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            assert width == 20

            # Test default case (all flags false, full width)
            app = H5Forest(temp_h5_file)
            # Don't set flags - they should default to False
            app._init_layout()
            width_func = app.tree_frame.container.width
            assert callable(width_func)
            width = width_func()
            # Should be full width when no split conditions are met
            assert width >= 20  # At least half width

    def test_tree_width_calculation_with_mocked_layout(self, temp_h5_file):
        """Test tree_width function branches with properly mocked layout.

        This test ensures all elif branches are covered by mocking the
        app.layout.has_focus() method so that flag properties work correctly.
        """
        from unittest.mock import MagicMock, patch

        from h5forest.h5_forest import H5Forest

        # Mock get_window_size to return known values
        with patch("h5forest.h5_forest.get_window_size") as mock_size:
            mock_size.return_value = (100, 40)  # 100 rows, 40 columns

            # Test elif branch for flag_plotting_mode
            app = H5Forest(temp_h5_file)
            app._flag_plotting_mode = True
            # Mock layout.has_focus to return False so property returns True
            app.app.layout.has_focus = MagicMock(return_value=False)
            app._init_layout()
            width_func = app.tree_frame.container.width
            width = width_func()
            assert width == 20  # Should be half width

            # Test elif branch for flag_hist_mode
            app = H5Forest(temp_h5_file)
            # Ensure all earlier flags are False
            app.flag_values_visible = False
            app._flag_plotting_mode = False
            app.scatter_plotter.plot_params = {}  # Ensure empty
            app._flag_hist_mode = True
            app.app.layout.has_focus = MagicMock(return_value=False)
            app._init_layout()
            width_func = app.tree_frame.container.width
            width = width_func()
            assert width == 20  # Should be half width

            # Test elif branch for flag_expanded_attrs
            app = H5Forest(temp_h5_file)
            # Ensure all earlier flags are False
            app.flag_values_visible = False
            app._flag_plotting_mode = False
            app._flag_hist_mode = False
            app.scatter_plotter.plot_params = {}
            app.histogram_plotter.plot_params = {}
            app.flag_expanded_attrs = True
            app.app.layout.has_focus = MagicMock(return_value=False)
            app._init_layout()
            width_func = app.tree_frame.container.width
            width = width_func()
            assert width == 20  # Should be half width

            # Test else branch (all flags False)
            app = H5Forest(temp_h5_file)
            # Explicitly ensure all flags are False
            app.flag_values_visible = False
            app._flag_plotting_mode = False
            app._flag_hist_mode = False
            app.flag_expanded_attrs = False
            app.scatter_plotter.plot_params = {}
            app.histogram_plotter.plot_params = {}
            app.app.layout.has_focus = MagicMock(return_value=False)
            app._init_layout()
            width_func = app.tree_frame.container.width
            width = width_func()
            assert width == 40  # Should be full width


class TestH5ForestPrintAndInput:
    """Test H5Forest print and input methods."""

    def test_print_single_string(self, temp_h5_file):
        """Test print with single string argument (no timeout)."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()

        # Explicitly set timeout=None to test without timeout
        app.print("Hello, World!", timeout=None)

        assert app.mini_buffer_content.text == "Hello, World!"
        app.app.invalidate.assert_called_once()

    def test_print_multiple_args(self, temp_h5_file):
        """Test print with multiple arguments (no timeout)."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()

        # Explicitly set timeout=None to test without timeout
        app.print("Hello", "World", 123, timeout=None)

        assert app.mini_buffer_content.text == "Hello World 123"
        app.app.invalidate.assert_called_once()

    def test_print_with_timeout(self, temp_h5_file):
        """Test print with timeout clears message after specified time."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()
        app.app.loop = MagicMock()

        # Print with a short timeout
        app.print("Temporary message", timeout=0.1)

        # Message should be set immediately
        assert app.mini_buffer_content.text == "Temporary message"
        app.app.invalidate.assert_called()

        # Wait for timeout plus a small buffer
        time.sleep(0.15)

        # The clear function should have been called via call_soon_threadsafe
        app.app.loop.call_soon_threadsafe.assert_called_once()

        # Execute the lambda that was passed to call_soon_threadsafe
        clear_func = app.app.loop.call_soon_threadsafe.call_args[0][0]
        clear_func()

        # Message should now be cleared
        assert app.mini_buffer_content.text == ""

    def test_print_with_none_timeout(self, temp_h5_file):
        """Test print with timeout=None does not start a thread."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()
        app.app.loop = MagicMock()

        # Print with timeout=None for persistent message
        app.print("Persistent message", timeout=None)

        # Message should be set
        assert app.mini_buffer_content.text == "Persistent message"

        # Wait a bit to ensure no thread is clearing the message
        time.sleep(0.15)

        # call_soon_threadsafe should not have been called
        app.app.loop.call_soon_threadsafe.assert_not_called()

        # Message should still be there
        assert app.mini_buffer_content.text == "Persistent message"

    def test_print_default_timeout(self, temp_h5_file):
        """Test print with default timeout (5 seconds)."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()
        app.app.loop = MagicMock()

        # Print with default timeout (should be 5 seconds)
        app.print("Default timeout message")

        # Message should be set immediately
        assert app.mini_buffer_content.text == "Default timeout message"
        app.app.invalidate.assert_called()

        # The thread should be started, but not cleared yet since we're not
        # waiting 5 seconds, We'll just verify that the message is still there
        # after a short time
        time.sleep(0.15)
        assert app.mini_buffer_content.text == "Default timeout message"

    def test_input_setup(self, temp_h5_file):
        """Test input method sets up correctly."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.shift_focus = MagicMock()
        app.app.invalidate = MagicMock()

        # Store current focus

        # Mock callback
        callback = MagicMock()

        # Call input
        app.input("Enter value:", callback, mini_buffer_text="default")

        # Verify setup
        assert app.user_input is None
        assert app.input_buffer_content.text == "Enter value:"
        assert app.mini_buffer_content.document.text == "default"
        assert app.mini_buffer_content.document.cursor_position == len(
            "default"
        )
        app.shift_focus.assert_called_once_with(app.mini_buffer_content)

    def test_input_on_enter(self, temp_h5_file):
        """Test input method setup."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Count bindings before
        initial_bindings = len(app.kb.bindings)

        # Create a simple callback
        def test_callback():
            pass

        # Set up input - this should add enter and escape bindings
        app.input("Test:", test_callback)

        # Should have added bindings (2: enter and escape)
        assert len(app.kb.bindings) >= initial_bindings + 2

        # Verify input was set up
        assert app.input_buffer_content.text == "Test:"
        assert app.user_input is None

    def test_input_callback_execution(self, temp_h5_file):
        """Test that input callback is executed on enter."""

        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Track if callback was called
        callback_executed = []

        def test_callback():
            callback_executed.append(app.user_input)

        # Store initial binding count
        initial_bindings = len(app.kb.bindings)

        # Set up input - this adds the on_enter binding
        app.input("Enter value:", test_callback)

        # Verify bindings were added
        assert len(app.kb.bindings) > initial_bindings

        # Simulate typing
        app.mini_buffer_content.text = "test_value"

        # Mock has_focus to return True for mini_buffer_content
        def mock_has_focus(widget):
            return widget == app.mini_buffer_content

        app.app.layout.has_focus = mock_has_focus

        # Find the newly added bindings (last 2: enter and escape)
        new_bindings = app.kb.bindings[initial_bindings:]

        # Find the enter binding from new bindings
        # The "enter" key might be represented differently
        on_enter_binding = None
        for binding in new_bindings:
            # Check for enter, c-m (Control-M, which is enter), or return
            if binding.keys in [("enter",), ("c-m",), ("<enter>",)]:
                on_enter_binding = binding
                break

        # If not found, just take the first new binding with a filter
        if on_enter_binding is None:
            for binding in new_bindings:
                if binding.filter is not None:
                    on_enter_binding = binding
                    break

        # Assert we found the binding
        msg = (
            f"Enter binding not found. Keys: {[b.keys for b in new_bindings]}"
        )
        assert on_enter_binding is not None, msg

        # Verify filter exists and passes
        assert on_enter_binding.filter is not None
        assert on_enter_binding.filter()

        # Call the on_enter handler
        mock_event = Mock()
        on_enter_binding.handler(mock_event)

        # Verify on_enter was executed (lines 785-791)
        assert app.user_input == "test_value"  # Line 785
        assert app.input_buffer_content.text == ""  # Line 788
        assert len(callback_executed) == 1  # Line 791
        assert callback_executed[0] == "test_value"

    def test_input_on_escape(self, temp_h5_file):
        """Test input method on_esc callback."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.return_to_normal_mode = MagicMock()
        app.shift_focus = MagicMock()

        # Store current focus

        # Set up input
        callback = MagicMock()
        app.input("Test:", callback)

        # Find the on_esc handler (escape binding)
        esc_bindings = [b for b in app.kb.bindings if b.keys == ("escape",)]
        assert len(esc_bindings) > 0

        # Get the last escape binding (the one added by input)
        esc_binding = esc_bindings[-1]

        # Create mock event
        mock_event = Mock()

        # Call the handler
        esc_binding.handler(mock_event)

        # Verify
        assert app.input_buffer_content.text == ""
        app.return_to_normal_mode.assert_called_once()
        # shift_focus called once in input(), once in on_esc
        assert app.shift_focus.call_count == 2

    def test_prompt_yes_no_yes_response(self, temp_h5_file):
        """Test prompt_yn method with 'y' response."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()

        # Track callbacks
        yes_called = []
        no_called = []

        def on_yes():
            yes_called.append(True)

        def on_no():
            no_called.append(True)

        # Store initial binding count
        initial_bindings = len(app.kb.bindings)

        # Call prompt_yn
        app.prompt_yn("Continue?", on_yes, on_no)

        # Verify prompt was set
        assert app.input_buffer_content.text == "Continue?"
        assert app.mini_buffer_content.text == ""

        # Verify bindings were added (y, n, escape)
        assert len(app.kb.bindings) >= initial_bindings + 3

        # Find the 'y' binding
        new_bindings = app.kb.bindings[initial_bindings:]
        y_binding = None
        for binding in new_bindings:
            if "y" in binding.keys:
                y_binding = binding
                break

        assert y_binding is not None

        # Simulate pressing 'y'
        mock_event = Mock()
        y_binding.handler(mock_event)

        # Verify yes callback was called
        assert len(yes_called) == 1
        assert len(no_called) == 0
        # Verify prompt was cleared
        assert app.input_buffer_content.text == ""

    def test_prompt_yes_no_no_response(self, temp_h5_file):
        """Test prompt_yn method with 'n' response."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()

        # Track callbacks
        yes_called = []
        no_called = []

        def on_yes():
            yes_called.append(True)

        def on_no():
            no_called.append(True)

        initial_bindings = len(app.kb.bindings)

        # Call prompt_yn
        app.prompt_yn("Delete?", on_yes, on_no)

        # Find the 'n' binding
        new_bindings = app.kb.bindings[initial_bindings:]
        n_binding = None
        for binding in new_bindings:
            if "n" in binding.keys:
                n_binding = binding
                break

        assert n_binding is not None

        # Simulate pressing 'n'
        mock_event = Mock()
        n_binding.handler(mock_event)

        # Verify no callback was called
        assert len(yes_called) == 0
        assert len(no_called) == 1

    def test_prompt_yes_no_escape_response(self, temp_h5_file):
        """Test prompt_yn method with escape key (treated as 'no')."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.invalidate = MagicMock()

        # Track callbacks
        yes_called = []
        no_called = []

        def on_yes():
            yes_called.append(True)

        def on_no():
            no_called.append(True)

        initial_bindings = len(app.kb.bindings)

        # Call prompt_yn
        app.prompt_yn("Continue?", on_yes, on_no)

        # Find the escape binding
        new_bindings = app.kb.bindings[initial_bindings:]
        esc_binding = None
        for binding in new_bindings:
            if "escape" in binding.keys:
                esc_binding = binding
                break

        assert esc_binding is not None

        # Simulate pressing escape
        mock_event = Mock()
        esc_binding.handler(mock_event)

        # Verify no callback was called (escape is treated as no)
        assert len(yes_called) == 0
        assert len(no_called) == 1


class TestH5ForestFocusManagement:
    """Test H5Forest focus management."""

    def test_default_focus(self, temp_h5_file):
        """Test default_focus shifts focus to tree."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.layout.focus = MagicMock()

        app.default_focus()

        app.app.layout.focus.assert_called_once_with(app.tree_content)

    def test_shift_focus(self, temp_h5_file):
        """Test shift_focus shifts focus to specified area."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app.app.layout.focus = MagicMock()

        target_area = Mock()
        app.shift_focus(target_area)

        app.app.layout.focus.assert_called_once_with(target_area)


class TestH5ForestMouseHandler:
    """Test H5Forest mouse handler creation."""

    def test_create_mouse_handler_on_mouse_up(self, temp_h5_file):
        """Test mouse handler focuses content on mouse up."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Create handler for a test area
        test_area = Mock()
        handler = app._create_mouse_handler(test_area)

        # Create mock mouse event
        mock_event = Mock()
        mock_event.event_type = MouseEventType.MOUSE_UP

        # Mock get_app
        with patch("h5forest.h5_forest.get_app") as mock_get_app:
            mock_layout = Mock()
            mock_get_app.return_value.layout = mock_layout

            # Call handler
            handler(mock_event)

            # Verify focus was called
            mock_layout.focus.assert_called_once_with(test_area)

    def test_create_mouse_handler_ignores_other_events(self, temp_h5_file):
        """Test mouse handler ignores non-MOUSE_UP events."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        test_area = Mock()
        handler = app._create_mouse_handler(test_area)

        # Create mock mouse event with different type
        mock_event = Mock()
        mock_event.event_type = MouseEventType.MOUSE_DOWN

        # Mock get_app
        with patch("h5forest.h5_forest.get_app") as mock_get_app:
            mock_layout = Mock()
            mock_get_app.return_value.layout = mock_layout

            # Call handler
            handler(mock_event)

            # Verify focus was NOT called
            mock_layout.focus.assert_not_called()


class TestH5ForestSearchTextChanged:
    """Test H5Forest search text changed handler."""

    def test_on_search_text_changed_filters_tree(self, temp_h5_file):
        """Test _on_search_text_changed filters tree."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_search_mode = True

        # Mock tree filter - it will be called during text assignment
        # so we need to reset it after
        app.tree.filter_tree = MagicMock(return_value="filtered text")

        # Setting text will trigger the handler via on_text_changed
        app.search_content.text = "search query"

        # Reset the mock after the automatic call
        app.tree.filter_tree.reset_mock()

        # Create mock event
        mock_event = Mock()

        # Mock app.app.loop for thread-safe calls
        app.app = MagicMock()
        app.app.loop = MagicMock()

        # Mock threading.Timer to execute immediately (debouncing uses timers)
        with patch("h5forest.h5_forest.threading.Timer") as mock_timer:
            # Make Timer execute the target function immediately
            def mock_timer_constructor(*args, **kwargs):
                target = kwargs.get("target") or args[1]
                mock_instance = MagicMock()

                def start():
                    target()  # Execute immediately instead of after delay

                mock_instance.start = start
                mock_instance.cancel = MagicMock()
                mock_instance.daemon = True
                return mock_instance

            mock_timer.side_effect = mock_timer_constructor

            # Mock get_app
            with patch("h5forest.h5_forest.get_app") as mock_get_app:
                mock_get_app.return_value.invalidate = MagicMock()

                # Call handler
                app._on_search_text_changed(mock_event)

                # Verify filter was called with the search query
                app.tree.filter_tree.assert_called_with("search query")

                # Verify call_soon_threadsafe was called to update display
                app.app.loop.call_soon_threadsafe.assert_called()

                # Execute the callback that was passed to call_soon_threadsafe
                callback = app.app.loop.call_soon_threadsafe.call_args[0][0]
                callback()

            # Verify document was updated
            assert app.tree_buffer.document.text == "filtered text"
            assert app.tree_buffer.document.cursor_position == 0

            # Verify invalidate was called
            mock_get_app.return_value.invalidate.assert_called_once()

    def test_on_search_text_changed_ignores_when_not_in_search_mode(
        self, temp_h5_file
    ):
        """Test _on_search_text_changed does nothing when not in search."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_search_mode = False

        # Mock tree filter
        app.tree.filter_tree = MagicMock()

        # Create mock event
        mock_event = Mock()

        # Call handler
        app._on_search_text_changed(mock_event)

        # Verify filter was NOT called
        app.tree.filter_tree.assert_not_called()

    def test_on_search_text_changed_cancels_previous_timer(self, temp_h5_file):
        """Test that typing multiple times cancels previous timer."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)
        app._flag_search_mode = True
        app.tree.filter_tree = MagicMock(return_value="filtered")
        app.search_content.text = "query"

        # Mock app.app.loop
        app.app = MagicMock()
        app.app.loop = MagicMock()

        # Track created timers
        timers = []

        with patch("h5forest.h5_forest.threading.Timer") as mock_timer:

            def create_timer(*args, **kwargs):
                timer = MagicMock()
                timer.cancel = MagicMock()
                timer.start = MagicMock()
                timer.daemon = True
                timers.append(timer)
                return timer

            mock_timer.side_effect = create_timer

            # Simulate rapid typing - call handler multiple times
            mock_event = Mock()
            app._on_search_text_changed(mock_event)
            app._on_search_text_changed(mock_event)
            app._on_search_text_changed(mock_event)

            # Should have created 3 timers
            assert len(timers) == 3

            # First two timers should have been cancelled
            timers[0].cancel.assert_called_once()
            timers[1].cancel.assert_called_once()

            # Last timer should not be cancelled
            timers[2].cancel.assert_not_called()

            # All timers should have been started
            for timer in timers:
                timer.start.assert_called_once()


class TestH5ForestMain:
    """Test main entry point function."""

    def test_main_with_no_args(self):
        """Test main function with no arguments."""
        from h5forest.h5_forest import main

        with patch("sys.argv", ["h5forest"]):
            # argparse exits with code 2 on argument errors
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Verify exit code (argparse uses 2 for argument errors)
            assert exc_info.value.code == 2

    def test_main_with_too_many_args(self):
        """Test main function with too many arguments."""
        from h5forest.h5_forest import main

        with patch("sys.argv", ["h5forest", "file1.h5", "file2.h5"]):
            # argparse exits with code 2 on argument errors
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Verify exit code (argparse uses 2 for argument errors)
            assert exc_info.value.code == 2

    def test_main_with_valid_file(self, temp_h5_file):
        """Test main function with valid file."""
        from h5forest.h5_forest import H5Forest, main

        with patch("sys.argv", ["h5forest", temp_h5_file]):
            with patch.object(H5Forest, "run") as mock_run:
                main()

                # Verify run was called
                mock_run.assert_called_once()


class TestH5ForestIntegration:
    """Integration tests for H5Forest."""

    def test_full_initialization_flow(self, temp_h5_file):
        """Test complete initialization creates functioning app."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Verify all major components exist and are connected
        assert app.tree is not None
        assert app.tree_processor.tree == app.tree
        assert app.app is not None
        assert app.layout is not None

        # Verify tree buffer has content
        assert app.tree_buffer.document.text != ""

        # Verify keybindings are registered
        assert len(app.kb.bindings) > 0

    def test_metadata_updates_on_cursor_move(self, temp_h5_file):
        """Test metadata updates when cursor moves."""
        from h5forest.h5_forest import H5Forest

        app = H5Forest(temp_h5_file)

        # Get initial metadata

        # Simulate cursor movement
        if len(app.tree.nodes_by_row) > 1:
            mock_event = Mock()

            # Move cursor to row 1
            text = "\n".join(
                [f"line {i}" for i in range(len(app.tree.nodes_by_row))]
            )
            doc = Document(text, cursor_position=len("line 0\n"))
            app.tree_buffer.set_document(doc, bypass_readonly=True)

            app.cursor_moved_action(mock_event)

            # Metadata should be updated (might be same or different)
            assert app.metadata_content.text is not None
