"""A module containing utility functions and classes for the HDF5 viewer."""

import os

from prompt_toolkit.application import get_app
from prompt_toolkit.layout import ConditionalContainer, HSplit, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl


class DynamicTitle:
    """
    A class to represent a dynamic title for the application.

    This can be used to update any title in the application dynamically.

    Attributes:
         title (str): The title to display.
    """

    def __init__(self, initial_title="Initial Title"):
        """
        Initialise the title.

        Args:
            initial_title (str): The initial title to display.
        """
        self.title = initial_title

    def __call__(self):
        """Return the current title."""
        return self.title

    def update_title(self, new_title):
        """
        Update the title.

        Args:
            new_title (str): The new title to display.
        """
        self.title = new_title


def get_window_size():
    """
    Get the terminal window size in lines and characters.

    Returns:
        tuple: The number of lines and characters in the terminal window.
    """
    rows, columns = os.popen("stty size", "r").read().split()
    return int(rows), int(columns)


class DynamicLabelLayout:
    """
    A layout container that dynamically arranges labels across multiple rows.

    This class wraps a list of labels or a callable that returns labels,
    and distributes them across multiple rows based on available terminal
    width. It ensures labels don't overlap and adjusts on window resize.

    Attributes:
        labels (list or callable): List of Label widgets, or a callable that
            returns a list of Labels when called.
        padding (int): Space between labels (default: 1).
        min_rows (int): Minimum number of rows to display (default: 1).
    """

    def __init__(self, labels, padding=1, min_rows=1):
        """
        Initialize the dynamic label layout.

        Args:
            labels (list or callable): List of Label widgets, or a callable
                that returns a list of Labels when called.
            padding (int): Space between labels (default: 1).
            min_rows (int): Minimum number of rows (default: 1).
        """
        self.labels = labels
        self.padding = padding
        self.min_rows = min_rows

    def _estimate_label_width(self, label):
        """
        Estimate the display width of a label.

        Args:
            label: A Label or ConditionalContainer widget.

        Returns:
            int: Estimated width in characters.
        """
        # For ConditionalContainer, get the inner label
        if isinstance(label, ConditionalContainer):
            inner = label.content
            # Extract text from Label widget
            if hasattr(inner, "text"):
                text = inner.text
            else:
                # Fallback estimate
                return 20
        else:
            # Direct Label widget
            if hasattr(label, "text"):
                text = label.text
            else:
                return 20

        # Add padding to the text length
        return len(text) + self.padding

    def _distribute_labels(self, available_width):
        """
        Distribute labels evenly across rows in a grid layout.

        This method calculates how many labels can fit per row, then
        distributes labels left-to-right, top-to-bottom to create
        aligned columns.

        Args:
            available_width (int): Terminal width in characters.

        Returns:
            list: List of lists, each containing labels for one row.
        """
        if available_width <= 0:
            available_width = 80  # Fallback width

        if not self.labels:
            # Return empty rows matching min_rows
            return [[] for _ in range(self.min_rows)]

        # Calculate maximum label width to ensure all labels fit
        label_widths = [
            self._estimate_label_width(label) for label in self.labels
        ]
        max_label_width = max(label_widths) if label_widths else 20

        # Calculate how many labels can fit per row based on max width
        # All labels will be padded to max_label_width, so we can fit:
        # available_width // max_label_width labels per row
        labels_per_row = max(1, available_width // max_label_width)

        # Distribute labels evenly across rows in grid fashion
        rows = []
        for i in range(0, len(self.labels), labels_per_row):
            row = self.labels[i : i + labels_per_row]
            rows.append(row)

        # Ensure minimum number of rows
        while len(rows) < self.min_rows:
            rows.append([])

        return rows

    def _get_label_text(self, label):
        """
        Extract text from a label or conditional container.

        Args:
            label: A Label or ConditionalContainer widget.

        Returns:
            str: The label's text content.
        """
        if isinstance(label, ConditionalContainer):
            inner = label.content
            if hasattr(inner, "text"):
                return inner.text
            return ""
        else:
            if hasattr(label, "text"):
                return label.text
            return ""

    def _create_padded_label(self, label, width):
        """
        Create a label padded to a specific width.

        Args:
            label: Original Label or ConditionalContainer.
            width: Target width in characters.

        Returns:
            Label with padded text (no conditional wrapping).
        """
        from prompt_toolkit.widgets import Label

        text = self._get_label_text(label)
        # Pad with spaces to reach target width
        padded_text = text.ljust(width)

        # Always return a regular Label without ConditionalContainer wrapping
        # This ensures proper grid alignment without gaps from hidden labels
        # Note: This means all labels are always visible in the grid
        return Label(padded_text)

    def __pt_container__(self):
        """
        Generate the prompt_toolkit container dynamically.

        This method is called by prompt_toolkit during rendering, allowing
        the layout to adjust to the current terminal size.

        Returns:
            HSplit: Container with labels arranged in multiple rows.
        """
        try:
            # Get current terminal width
            app = get_app()
            output = app.output
            size = output.get_size()
            available_width = size.columns
        except Exception:
            # Fallback if app is not available
            available_width = 80

        # Get current labels (call if callable, otherwise use as-is)
        current_labels = (
            self.labels() if callable(self.labels) else self.labels
        )

        # Temporarily store current labels for distribution
        original_labels = self.labels
        self.labels = current_labels

        # Distribute labels across rows
        rows = self._distribute_labels(available_width)

        # Restore original labels reference
        self.labels = original_labels

        if not rows or all(not row for row in rows):
            # All rows are empty
            row_containers = []
            for _ in range(self.min_rows):
                row_containers.append(
                    Window(
                        FormattedTextControl(text=""),
                        height=1,
                    )
                )
            return HSplit(row_containers)

        # Calculate max label width for padding (for grid alignment)
        # Find the width needed for the widest label
        max_text_width = 0
        for row in rows:
            for label in row:
                text = self._get_label_text(label)
                max_text_width = max(max_text_width, len(text))

        # Add padding to account for spacing between labels
        column_width = max_text_width + self.padding

        # Find the maximum row length to ensure all rows have same count
        max_row_length = (
            max(len(row) for row in rows if row) if any(rows) else 0
        )

        # Create VSplit for each row with padded labels
        row_containers = []
        for row in rows:
            if row:
                # Pad all labels in this row to the same width
                padded_labels = [
                    self._create_padded_label(label, column_width)
                    for label in row
                ]

                # Pad row with empty labels to match max_row_length
                while len(padded_labels) < max_row_length:
                    from prompt_toolkit.widgets import Label

                    padded_labels.append(Label(" " * column_width))

                row_containers.append(VSplit(padded_labels))
            else:
                # Empty row - add empty labels matching max_row_length
                if max_row_length > 0:
                    from prompt_toolkit.widgets import Label

                    empty_labels = [
                        Label(" " * column_width)
                        for _ in range(max_row_length)
                    ]
                    row_containers.append(VSplit(empty_labels))
                else:
                    # No labels at all - add an empty window
                    row_containers.append(
                        Window(
                            FormattedTextControl(text=""),
                            height=1,
                        )
                    )

        return HSplit(row_containers)
