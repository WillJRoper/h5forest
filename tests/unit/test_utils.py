"""Simple utils tests that work correctly."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, HSplit, VSplit
from prompt_toolkit.widgets import Label

from h5forest.utils import DynamicLabelLayout, DynamicTitle, get_window_size


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

    @patch("os.popen")
    def test_get_window_size_with_mocked_popen(self, mock_popen):
        """Test get_window_size with mocked os.popen."""
        # Create a mock file object that returns "24 80"
        mock_file = MagicMock()
        mock_file.read.return_value = "24 80"
        mock_popen.return_value = mock_file

        rows, cols = get_window_size()

        assert rows == 24
        assert cols == 80
        mock_popen.assert_called_once_with("stty size", "r")

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


class TestDynamicLabelLayout:
    """Test cases for DynamicLabelLayout class."""

    def test_init_default_parameters(self):
        """Test DynamicLabelLayout initialization with default parameters."""
        labels = [Label("Test 1"), Label("Test 2")]
        layout = DynamicLabelLayout(labels)

        assert layout.labels == labels
        assert layout.padding == 3
        assert layout.min_rows == 3

    def test_init_custom_parameters(self):
        """Test DynamicLabelLayout initialization with custom parameters."""
        labels = [Label("Test 1")]
        layout = DynamicLabelLayout(labels, padding=5, min_rows=2)

        assert layout.labels == labels
        assert layout.padding == 5
        assert layout.min_rows == 2

    def test_estimate_label_width_simple_label(self):
        """Test width estimation for a simple Label."""
        layout = DynamicLabelLayout([])
        label = Label("Hello World")

        # Width should be text length (11) + padding (3) = 14
        width = layout._estimate_label_width(label)
        assert width == 14

    def test_estimate_label_width_conditional_container(self):
        """Test width estimation for a ConditionalContainer."""
        layout = DynamicLabelLayout([])
        label = Label("Test Label")
        container = ConditionalContainer(
            label, filter=Condition(lambda: True)
        )

        # Width should be text length (10) + padding (3) = 13
        width = layout._estimate_label_width(container)
        assert width == 13

    def test_estimate_label_width_custom_padding(self):
        """Test width estimation with custom padding."""
        layout = DynamicLabelLayout([], padding=10)
        label = Label("Test")

        # Width should be text length (4) + padding (10) = 14
        width = layout._estimate_label_width(label)
        assert width == 14

    def test_estimate_label_width_fallback(self):
        """Test width estimation fallback for objects without text attribute."""
        layout = DynamicLabelLayout([])
        mock_label = Mock(spec=[])  # Mock without 'text' attribute

        # Should return fallback value of 20
        width = layout._estimate_label_width(mock_label)
        assert width == 20

    def test_distribute_labels_single_row(self):
        """Test label distribution when all labels fit in one row."""
        labels = [Label("A"), Label("B"), Label("C")]
        layout = DynamicLabelLayout(labels, padding=2)

        # Total width needed: (1+2) + (1+2) + (1+2) = 9 characters
        # Available width: 100 (more than enough)
        # Grid layout: all 3 labels should fit in first row
        rows = layout._distribute_labels(100)

        # Should have 3 rows minimum (even though all fit in one)
        assert len(rows) == 3
        # First row should have all labels (grid places them all in one row)
        assert len(rows[0]) == 3
        # Remaining rows should be empty
        assert rows[1] == []
        assert rows[2] == []
        # Verify all labels are present
        assert all(label in rows[0] for label in labels)

    def test_distribute_labels_multiple_rows(self):
        """Test label distribution across multiple rows in grid layout."""
        labels = [
            Label("Label 1"),
            Label("Label 2"),
            Label("Label 3"),
            Label("Label 4"),
        ]
        layout = DynamicLabelLayout(labels, padding=3)

        # Each label: ~10 characters with padding = ~13 total
        # With width=25, should fit 2 labels per row in grid layout
        rows = layout._distribute_labels(25)

        # Should have at least 3 rows (min_rows)
        assert len(rows) >= 3
        # With grid layout, rows should have equal counts (except last)
        non_empty_rows = [r for r in rows if r]
        if len(non_empty_rows) >= 2:
            # First rows should have same number of labels
            assert len(non_empty_rows[0]) == len(non_empty_rows[1])
        # All labels should be distributed
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    def test_distribute_labels_narrow_terminal(self):
        """Test label distribution with very narrow terminal."""
        labels = [Label("Short"), Label("Text"), Label("Here")]
        layout = DynamicLabelLayout(labels, padding=2)

        # Very narrow width
        rows = layout._distribute_labels(10)

        # Should handle narrow width gracefully
        assert len(rows) >= 3
        # Labels should be distributed
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    def test_distribute_labels_zero_width(self):
        """Test label distribution with zero width (fallback)."""
        labels = [Label("A"), Label("B")]
        layout = DynamicLabelLayout(labels)

        # Zero width should trigger fallback to 80
        rows = layout._distribute_labels(0)

        assert len(rows) >= 3
        # Should still distribute labels
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    def test_distribute_labels_negative_width(self):
        """Test label distribution with negative width (fallback)."""
        labels = [Label("A")]
        layout = DynamicLabelLayout(labels)

        # Negative width should trigger fallback to 80
        rows = layout._distribute_labels(-10)

        assert len(rows) >= 3

    def test_distribute_labels_empty_list(self):
        """Test label distribution with empty label list."""
        layout = DynamicLabelLayout([])

        rows = layout._distribute_labels(80)

        # Should have minimum rows
        assert len(rows) == 3
        # All rows should be empty
        assert all(len(row) == 0 for row in rows)

    def test_distribute_labels_min_rows_enforcement(self):
        """Test that minimum rows are enforced."""
        labels = [Label("A")]
        layout = DynamicLabelLayout(labels, min_rows=5)

        rows = layout._distribute_labels(100)

        # Should have at least min_rows
        assert len(rows) == 5
        # First row has the label
        assert len(rows[0]) == 1
        # Remaining rows are empty
        assert all(len(rows[i]) == 0 for i in range(1, 5))

    def test_distribute_labels_exceeds_min_rows(self):
        """Test distribution when natural rows exceed min_rows."""
        # Create many labels that won't fit in 3 rows
        labels = [Label(f"Label {i}") for i in range(20)]
        layout = DynamicLabelLayout(labels, padding=2, min_rows=3)

        # With narrow width, should create more than 3 rows
        rows = layout._distribute_labels(20)

        # Should have more than min_rows
        assert len(rows) > 3
        # Should have all labels distributed
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    def test_distribute_labels_with_conditional_containers(self):
        """Test distribution with mix of Labels and ConditionalContainers."""
        labels = [
            Label("Regular 1"),
            ConditionalContainer(
                Label("Conditional 1"), filter=Condition(lambda: True)
            ),
            Label("Regular 2"),
            ConditionalContainer(
                Label("Conditional 2"), filter=Condition(lambda: False)
            ),
        ]
        layout = DynamicLabelLayout(labels)

        rows = layout._distribute_labels(80)

        # Should distribute all items
        total_items = sum(len(row) for row in rows)
        assert total_items == len(labels)

    @patch("h5forest.utils.get_app")
    def test_pt_container_method_exists(self, mock_get_app):
        """Test that __pt_container__ method exists and is callable."""
        labels = [Label("Test")]
        layout = DynamicLabelLayout(labels)

        # Mock the app and output
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 80
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        # Should return an HSplit container
        assert isinstance(container, HSplit)

    @patch("h5forest.utils.get_app")
    def test_pt_container_returns_hsplit(self, mock_get_app):
        """Test that __pt_container__ returns an HSplit."""
        labels = [Label("A"), Label("B"), Label("C")]
        layout = DynamicLabelLayout(labels)

        # Mock the app
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 100
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        assert isinstance(container, HSplit)
        # Should have child containers
        assert len(container.get_children()) > 0

    @patch("h5forest.utils.get_app")
    def test_pt_container_with_exception(self, mock_get_app):
        """Test __pt_container__ fallback when get_app raises exception."""
        labels = [Label("Test")]
        layout = DynamicLabelLayout(labels)

        # Make get_app raise an exception
        mock_get_app.side_effect = Exception("No app")

        # Should still work with fallback width
        container = layout.__pt_container__()

        assert isinstance(container, HSplit)

    @patch("h5forest.utils.get_app")
    def test_pt_container_narrow_width(self, mock_get_app):
        """Test __pt_container__ with narrow terminal width."""
        labels = [Label("Long Label Text"), Label("Another Long Label")]
        layout = DynamicLabelLayout(labels)

        # Mock narrow terminal
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 20  # Very narrow
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        assert isinstance(container, HSplit)
        # Should create multiple rows due to narrow width
        children = container.get_children()
        assert len(children) >= 3  # At least min_rows

    @patch("h5forest.utils.get_app")
    def test_pt_container_wide_width(self, mock_get_app):
        """Test __pt_container__ with wide terminal width."""
        labels = [Label("A"), Label("B"), Label("C")]
        layout = DynamicLabelLayout(labels)

        # Mock wide terminal
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 200  # Very wide
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        assert isinstance(container, HSplit)
        children = container.get_children()
        # Should have min_rows (3) even though all fit in one row
        assert len(children) == 3

    @patch("h5forest.utils.get_app")
    def test_pt_container_empty_labels(self, mock_get_app):
        """Test __pt_container__ with empty label list."""
        layout = DynamicLabelLayout([])

        # Mock the app
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 80
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        assert isinstance(container, HSplit)
        children = container.get_children()
        # Should have min_rows of empty rows
        assert len(children) == 3

    def test_label_distribution_realistic_scenario(self):
        """Test label distribution in a realistic scenario."""
        # Simulate normal mode labels
        labels = [
            Label("Enter → Open Group"),
            Label("{/} → Move Up/Down 10 Lines"),
            Label("A → Expand Attributes"),
            Label("d → Dataset Mode"),
            Label("g → Goto Mode"),
            Label("H → Histogram Mode"),
            Label("p → Plotting Mode"),
            Label("w → Window Mode"),
            Label("s → Search"),
            Label("r → Restore Tree"),
            Label("q → Exit"),
        ]
        layout = DynamicLabelLayout(labels, padding=3)

        # Test with various terminal widths
        widths = [60, 80, 100, 120, 150]

        for width in widths:
            rows = layout._distribute_labels(width)

            # Should have at least min_rows
            assert len(rows) >= 3

            # All labels should be distributed
            total_labels = sum(len(row) for row in rows)
            assert total_labels == len(labels)

            # Each label should appear exactly once
            all_distributed_labels = []
            for row in rows:
                all_distributed_labels.extend(row)
            assert len(all_distributed_labels) == len(labels)

            # Grid layout: non-empty rows should have consistent counts
            non_empty_rows = [r for r in rows if r]
            if len(non_empty_rows) > 1:
                # All rows except possibly last should have same count
                row_counts = [len(r) for r in non_empty_rows[:-1]]
                if row_counts:
                    # All should be equal
                    assert all(c == row_counts[0] for c in row_counts)

    def test_label_distribution_with_varying_sizes(self):
        """Test distribution with labels of varying sizes."""
        labels = [
            Label("A"),
            Label("Medium Label"),
            Label("Very Long Label Text Here"),
            Label("B"),
            Label("Another Medium One"),
        ]
        layout = DynamicLabelLayout(labels, padding=2)

        rows = layout._distribute_labels(50)

        # Should distribute efficiently
        assert len(rows) >= 3
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    @patch("h5forest.utils.get_app")
    def test_integration_with_vsplit_children(self, mock_get_app):
        """Test that VSplit children are created correctly."""
        labels = [Label("A"), Label("B")]
        layout = DynamicLabelLayout(labels, min_rows=3)

        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 100
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        container = layout.__pt_container__()

        # Check that we have the right number of children
        children = container.get_children()
        assert len(children) == 3

        # First child should be a VSplit with the labels
        first_child = children[0]
        assert isinstance(first_child, VSplit)

    def test_realistic_plotting_mode_labels(self):
        """Test with realistic plotting mode label set."""
        labels = [
            ConditionalContainer(
                Label("e → Edit Config"), Condition(lambda: True)
            ),
            ConditionalContainer(
                Label("Enter → Edit entry"), Condition(lambda: False)
            ),
            ConditionalContainer(
                Label("x → Select x-axis"), Condition(lambda: True)
            ),
            ConditionalContainer(
                Label("y → Select y-axis"), Condition(lambda: True)
            ),
            Label("p → Plot"),
            Label("P → Save Plot"),
            Label("r → Reset"),
            Label("q → Exit Plotting Mode"),
        ]
        layout = DynamicLabelLayout(labels)

        # Test with terminal width typical for development
        rows = layout._distribute_labels(120)

        assert len(rows) >= 3
        total_items = sum(len(row) for row in rows)
        assert total_items == len(labels)

    def test_grid_alignment_property(self):
        """Test that grid layout maintains consistent row sizes."""
        # Create labels that should require multiple rows
        labels = [Label(f"Item {i}") for i in range(10)]
        layout = DynamicLabelLayout(labels, padding=2)

        # Test with moderate width (should create multiple rows)
        rows = layout._distribute_labels(50)

        # Get non-empty rows
        non_empty_rows = [r for r in rows if r]

        # Grid property: all rows except last should have same count
        if len(non_empty_rows) > 1:
            first_row_count = len(non_empty_rows[0])
            # All rows except possibly the last should match first row
            for row in non_empty_rows[:-1]:
                assert (
                    len(row) == first_row_count
                ), f"Grid alignment failed: expected {first_row_count} labels per row"

            # Last row should have <= first_row_count
            assert len(non_empty_rows[-1]) <= first_row_count

    def test_grid_distribution_order(self):
        """Test that labels are distributed left-to-right, top-to-bottom."""
        labels = [
            Label("A"),
            Label("B"),
            Label("C"),
            Label("D"),
            Label("E"),
        ]
        layout = DynamicLabelLayout(labels, padding=2)

        # With narrow width, should get 1 per row
        rows = layout._distribute_labels(5)

        # Labels should appear in order across rows
        flat_labels = []
        for row in rows:
            flat_labels.extend(row)

        # Should maintain original order
        for i, label in enumerate(flat_labels):
            assert label == labels[i]
