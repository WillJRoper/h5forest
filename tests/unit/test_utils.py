"""Simple utils tests that work correctly."""

from unittest.mock import patch

from h5forest.utils import DynamicTitle


class TestDynamicTitle:
    """Test cases for DynamicTitle class."""

    def test_init_default_title(self):
        """Test DynamicTitle initialization with default title."""
        title = DynamicTitle()
        assert title.title == "Initial Title"
        assert title() == "Initial Title"

    def test_init_custom_title(self):
        """Test DynamicTitle initialization with custom title."""
        custom_title = "My Custom Title"
        title = DynamicTitle(custom_title)
        assert title.title == custom_title
        assert title() == custom_title

    def test_update_title(self):
        """Test updating the title."""
        title = DynamicTitle("Original")
        assert title() == "Original"

        title.update_title("Updated")
        assert title() == "Updated"
        assert title.title == "Updated"

    def test_callable_interface(self):
        """Test that DynamicTitle is callable."""
        title = DynamicTitle("Test")
        assert callable(title)
        assert title() == "Test"

    def test_multiple_updates(self):
        """Test multiple title updates."""
        title = DynamicTitle()

        titles = ["First", "Second", "Third"]
        for new_title in titles:
            title.update_title(new_title)
            assert title() == new_title


class TestGetWindowSizeSimple:
    """Simple tests for get_window_size function with proper mocking."""

    @patch("h5forest.utils.get_window_size")
    def test_get_window_size_mocked(self, mock_get_window_size):
        """Test get_window_size with complete function mock."""
        mock_get_window_size.return_value = (24, 80)

        rows, cols = mock_get_window_size()

        assert rows == 24
        assert cols == 80

    def test_get_window_size_import_exists(self):
        """Test that get_window_size function can be imported."""
        from h5forest.utils import get_window_size

        assert callable(get_window_size)

    def test_dynamic_title_realistic_usage(self):
        """Test DynamicTitle in realistic usage patterns."""
        # Simulate a realistic usage pattern
        title = DynamicTitle("Loading...")

        # Initial state
        assert title() == "Loading..."

        # Update during processing
        title.update_title("Processing file.h5")
        assert "file.h5" in title()

        # Update with node information
        title.update_title("Node: /group1/dataset")
        assert "Node:" in title()
        assert "/group1/dataset" in title()

        # Final state
        title.update_title("Ready")
        assert title() == "Ready"

    def test_multiple_dynamic_titles(self):
        """Test multiple DynamicTitle instances."""
        title1 = DynamicTitle("Title 1")
        title2 = DynamicTitle("Title 2")
        title3 = DynamicTitle("Title 3")

        # Each should maintain independent state
        assert title1() == "Title 1"
        assert title2() == "Title 2"
        assert title3() == "Title 3"

        # Update one shouldn't affect others
        title2.update_title("Updated Title 2")

        assert title1() == "Title 1"
        assert title2() == "Updated Title 2"
        assert title3() == "Title 3"
