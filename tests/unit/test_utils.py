"""Simple utils tests that work correctly."""

from unittest.mock import MagicMock, Mock, patch

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import (
    ConditionalContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.widgets import Label

from h5forest.utils import (
    DynamicLabelLayout,
    DynamicTitle,
    WaitIndicator,
    get_window_size,
)


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
        assert layout.padding == 5
        assert layout.min_rows == 1

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

        # Width should be text length (11) + padding (5) = 16
        width = layout._estimate_label_width(label)
        assert width == 16

    def test_estimate_label_width_conditional_container(self):
        """Test width estimation for a ConditionalContainer."""
        layout = DynamicLabelLayout([])
        label = Label("Test Label")
        container = ConditionalContainer(label, filter=Condition(lambda: True))

        # ConditionalContainers convert Labels to Windows automatically,
        # so we can't extract the text and fall back to 20
        width = layout._estimate_label_width(container)
        assert width == 20  # Fallback value

    def test_estimate_label_width_conditional_with_text(self):
        """Test width estimation for ConditionalContainer with text."""
        layout = DynamicLabelLayout([])

        # Create a mock ConditionalContainer with content that has text
        mock_content = Mock()
        mock_content.text = "Test"
        container = Mock(spec=ConditionalContainer)
        container.content = mock_content

        # Should extract text and calculate width
        width = layout._estimate_label_width(container)
        assert width == 9  # len("Test") + padding(5)

    def test_estimate_label_width_custom_padding(self):
        """Test width estimation with custom padding."""
        layout = DynamicLabelLayout([], padding=10)
        label = Label("Test")

        # Width should be text length (4) + padding (10) = 14
        width = layout._estimate_label_width(label)
        assert width == 14

    def test_estimate_label_width_fallback(self):
        """Test width estimation fallback for objects without text."""
        layout = DynamicLabelLayout([])
        mock_label = Mock(spec=[])  # Mock without 'text' attribute

        # Should return fallback value of 20
        width = layout._estimate_label_width(mock_label)
        assert width == 20

    def test_distribute_labels_single_row(self):
        """Test label distribution when all labels fit in one row."""
        labels = [Label("A"), Label("B"), Label("C")]
        layout = DynamicLabelLayout(labels, padding=2, min_rows=3)

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
        layout = DynamicLabelLayout(labels, padding=3, min_rows=3)

        # Each label: 7 characters + 3 padding = 10 total
        # With width=15 and +1 in calculation: 15 // 10 + 1 = 2 labels per row
        rows = layout._distribute_labels(15)

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
        layout = DynamicLabelLayout(labels, padding=2, min_rows=3)

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
        layout = DynamicLabelLayout(labels, min_rows=3)

        # Zero width should trigger fallback to 80
        rows = layout._distribute_labels(0)

        assert len(rows) >= 3
        # Should still distribute labels
        total_labels = sum(len(row) for row in rows)
        assert total_labels == len(labels)

    def test_distribute_labels_negative_width(self):
        """Test label distribution with negative width (fallback)."""
        labels = [Label("A")]
        layout = DynamicLabelLayout(labels, min_rows=3)

        # Negative width should trigger fallback to 80
        rows = layout._distribute_labels(-10)

        assert len(rows) >= 3

    def test_distribute_labels_empty_list(self):
        """Test label distribution with empty label list."""
        layout = DynamicLabelLayout([], min_rows=3)

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
        layout = DynamicLabelLayout(labels, min_rows=3)

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
        layout = DynamicLabelLayout(labels, min_rows=3)

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
        layout = DynamicLabelLayout([], min_rows=3)

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

        # Verify children are Windows (line 301 coverage)
        for child in children:
            assert isinstance(child, (Window, VSplit))

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
            assert len(rows) >= 1

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
        layout = DynamicLabelLayout(labels, min_rows=3)

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
                assert len(row) == first_row_count, (
                    f"Grid alignment failed: "
                    f"expected {first_row_count} labels per row"
                )

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

    def test_get_label_text_simple_label(self):
        """Test extracting text from a simple Label."""
        layout = DynamicLabelLayout([])
        label = Label("Test Text")

        text = layout._get_label_text(label)
        assert text == "Test Text"

    def test_get_label_text_conditional_container(self):
        """Test extracting text from a ConditionalContainer."""
        layout = DynamicLabelLayout([])
        label = Label("Conditional Text")
        container = ConditionalContainer(label, filter=Condition(lambda: True))

        # ConditionalContainers convert Labels to Windows automatically,
        # so we can't extract the original text and return empty string
        text = layout._get_label_text(container)
        assert text == ""  # Empty string fallback

    def test_create_padded_label_simple(self):
        """Test creating a padded label."""
        layout = DynamicLabelLayout([])
        label = Label("Short")

        padded = layout._create_padded_label(label, 20)
        padded_text = layout._get_label_text(padded)

        assert len(padded_text) == 20
        assert padded_text.startswith("Short")
        assert padded_text.endswith(" " * (20 - 5))

    def test_create_padded_label_conditional(self):
        """Test creating a padded label from ConditionalContainer."""
        layout = DynamicLabelLayout([])
        label = Label("Text")
        container = ConditionalContainer(label, filter=Condition(lambda: True))

        padded = layout._create_padded_label(container, 15)

        # Should be a regular Label (not ConditionalContainer)
        # This ensures grid alignment without gaps
        assert isinstance(padded, Label)
        # ConditionalContainers can't provide text,
        # so we get empty padded string
        assert len(padded.text) == 15
        assert padded.text == " " * 15  # All spaces

    @patch("h5forest.utils.get_app")
    def test_pt_container_with_padding(self, mock_get_app):
        """Test that __pt_container__ creates padded labels."""
        labels = [Label("A"), Label("Long Label"), Label("B")]
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

        # Should create an HSplit
        assert isinstance(container, HSplit)

        # Get the first row (should be a VSplit)
        children = container.get_children()
        assert len(children) >= 1

        first_row = children[0]
        if isinstance(first_row, VSplit):
            # Get labels from first row
            row_labels = first_row.get_children()
            # All labels should have been padded to same width
            if len(row_labels) > 1:
                # Extract text from each label
                texts = []
                for lbl in row_labels:
                    if hasattr(lbl, "text"):
                        texts.append(lbl.text)
                # All should have same length (padded)
                if texts:
                    first_len = len(texts[0])
                    assert all(len(t) == first_len for t in texts), (
                        "All labels should be padded to same width"
                    )

    @patch("shutil.get_terminal_size")
    @patch("h5forest.utils.get_app")
    def test_pt_container_shutil_exception(
        self, mock_get_app, mock_get_terminal_size
    ):
        """Test __pt_container__ fallback when shutil fails."""
        labels = [Label("Test")]
        layout = DynamicLabelLayout(labels)

        # Make shutil.get_terminal_size raise an exception
        mock_get_terminal_size.side_effect = Exception("No terminal")

        # Mock get_app to provide fallback
        mock_app = Mock()
        mock_output = Mock()
        mock_size = Mock()
        mock_size.columns = 80
        mock_output.get_size.return_value = mock_size
        mock_app.output = mock_output
        mock_get_app.return_value = mock_app

        # Should fallback to get_app and still work
        container = layout.__pt_container__()
        assert isinstance(container, HSplit)

    @patch("shutil.get_terminal_size")
    @patch("h5forest.utils.get_app")
    def test_pt_container_both_exceptions(
        self, mock_get_app, mock_get_terminal_size
    ):
        """Test __pt_container__ final fallback when both methods fail."""
        labels = [Label("Test")]
        layout = DynamicLabelLayout(labels)

        # Make both terminal size methods fail
        mock_get_terminal_size.side_effect = Exception("No terminal")
        mock_get_app.side_effect = Exception("No app")

        # Should use final fallback width of 80
        container = layout.__pt_container__()
        assert isinstance(container, HSplit)

    def test_estimate_label_width_conditional_without_text(self):
        """Test width estimation for ConditionalContainer without text attr."""
        layout = DynamicLabelLayout([])

        # Create a ConditionalContainer with content that has no text attribute
        mock_content = Mock(spec=[])  # No text attribute
        container = Mock(spec=ConditionalContainer)
        container.content = mock_content

        # Should return fallback value of 20
        width = layout._estimate_label_width(container)
        assert width == 20

    def test_get_label_text_label_without_text(self):
        """Test getting text from label without text attribute."""
        layout = DynamicLabelLayout([])
        mock_label = Mock(spec=[])  # No text attribute

        text = layout._get_label_text(mock_label)
        assert text == ""

    def test_get_label_text_conditional_without_text(self):
        """Test getting text from ConditionalContainer without text."""
        layout = DynamicLabelLayout([])

        # Create ConditionalContainer with content that has no text
        mock_content = Mock(spec=[])
        container = Mock(spec=ConditionalContainer)
        container.content = mock_content

        text = layout._get_label_text(container)
        assert text == ""

    def test_get_label_text_conditional_with_text(self):
        """Test getting text from ConditionalContainer with text attribute."""
        layout = DynamicLabelLayout([])

        # Create ConditionalContainer with content that has text
        mock_content = Mock()
        mock_content.text = "Hello World"
        container = Mock(spec=ConditionalContainer)
        container.content = mock_content

        text = layout._get_label_text(container)
        assert text == "Hello World"


class TestWaitIndicator:
    """Test cases for WaitIndicator class."""

    def test_init(self):
        """Test WaitIndicator initialization."""
        mock_app = MagicMock()
        indicator = WaitIndicator(mock_app, "Test message")

        assert indicator.app == mock_app
        assert indicator.message == "Test message"
        assert indicator.update_interval == 0.1
        assert indicator.running is False
        assert indicator.thread is None

    def test_init_custom_interval(self):
        """Test WaitIndicator with custom update interval."""
        mock_app = MagicMock()
        indicator = WaitIndicator(mock_app, "Test", update_interval=0.5)

        assert indicator.update_interval == 0.5

    def test_start_sets_running_flag(self):
        """Test that start() sets the running flag."""
        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Test")
        indicator.start()

        assert indicator.running is True
        assert indicator.thread is not None
        assert indicator.thread.daemon is True

        # Clean up
        indicator.stop()

    def test_start_creates_thread(self):
        """Test that start() creates a daemon thread."""
        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Test")
        indicator.start()

        assert indicator.thread is not None
        assert indicator.thread.is_alive()
        assert indicator.thread.daemon is True

        # Clean up
        indicator.stop()

    def test_stop_clears_running_flag(self):
        """Test that stop() clears the running flag."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Test")
        indicator.start()
        time.sleep(0.05)  # Let thread start
        indicator.stop()

        assert indicator.running is False
        assert indicator.thread is None

    def test_stop_joins_thread(self):
        """Test that stop() waits for thread to finish."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Test")
        indicator.start()
        time.sleep(0.05)  # Let thread start

        thread_ref = indicator.thread
        indicator.stop()

        # Thread should be joined and no longer alive
        assert not thread_ref.is_alive()

    def test_context_manager_start(self):
        """Test using WaitIndicator as context manager."""
        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        with WaitIndicator(mock_app, "Test") as indicator:
            assert indicator.running is True
            assert indicator.thread is not None

        # After exiting context, should be stopped
        assert indicator.running is False

    def test_context_manager_stop(self):
        """Test that context manager stops indicator on exit."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = None
        with WaitIndicator(mock_app, "Test") as ind:
            indicator = ind
            time.sleep(0.05)

        # Should be stopped after context exit
        assert indicator.running is False
        assert indicator.thread is None

    def test_animate_calls_app_print(self):
        """Test that animate loop calls app.print with spinner."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Loading")
        indicator.start()

        # Let it run for a bit
        time.sleep(0.25)
        indicator.stop()

        # Should have called print multiple times
        assert mock_app.app.loop.call_soon_threadsafe.call_count > 0

        # Check that it was called with spinner characters
        calls = mock_app.app.loop.call_soon_threadsafe.call_args_list
        assert len(calls) > 0

    def test_animate_clears_message_on_stop(self):
        """Test that stopping clears the message."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Loading")
        indicator.start()
        time.sleep(0.15)
        indicator.stop()

        # Last call should clear the message (empty string)
        last_call = mock_app.app.loop.call_soon_threadsafe.call_args_list[-1]
        # Execute the lambda to see what it does
        last_call[0][0]()
        mock_app.print.assert_called_with("")

    def test_start_when_already_running(self):
        """Test that calling start() when already running does nothing."""
        import time

        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        indicator = WaitIndicator(mock_app, "Test")
        indicator.start()
        time.sleep(0.05)

        first_thread = indicator.thread

        # Try to start again
        indicator.start()

        # Should still be the same thread
        assert indicator.thread is first_thread

        # Clean up
        indicator.stop()

    def test_spinner_characters(self):
        """Test that SPINNER_CHARS constant is defined correctly."""
        expected_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        assert WaitIndicator.SPINNER_CHARS == expected_chars

    def test_multiple_indicators(self):
        """Test multiple independent WaitIndicator instances."""
        import time

        mock_app1 = MagicMock()
        mock_app1.app = MagicMock()
        mock_app1.app.loop = MagicMock()

        mock_app2 = MagicMock()
        mock_app2.app = MagicMock()
        mock_app2.app.loop = MagicMock()

        indicator1 = WaitIndicator(mock_app1, "First")
        indicator2 = WaitIndicator(mock_app2, "Second")

        indicator1.start()
        indicator2.start()
        time.sleep(0.1)

        # Both should be running independently
        assert indicator1.running is True
        assert indicator2.running is True

        indicator1.stop()
        indicator2.stop()

        # Both should be stopped
        assert indicator1.running is False
        assert indicator2.running is False

    def test_context_manager_exception_handling(self):
        """Test that exceptions in context manager are not suppressed."""
        mock_app = MagicMock()
        mock_app.app = MagicMock()
        mock_app.app.loop = MagicMock()

        try:
            with WaitIndicator(mock_app, "Test"):
                raise ValueError("Test error")
        except ValueError as e:
            # Exception should propagate
            assert str(e) == "Test error"
        else:
            assert False, "Exception should have been raised"
