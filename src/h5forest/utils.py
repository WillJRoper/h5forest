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

    This class wraps a list of labels (including ConditionalContainers) and
    distributes them across multiple rows based on available terminal width.
    It ensures labels don't overlap and automatically adjusts on window resize.

    Attributes:
        labels (list): List of Label or ConditionalContainer widgets.
        padding (int): Space between labels (default: 3).
        min_rows (int): Minimum number of rows to display (default: 3).
    """

    def __init__(self, labels, padding=3, min_rows=3):
        """
        Initialize the dynamic label layout.

        Args:
            labels (list): List of Label or ConditionalContainer widgets.
            padding (int): Space between labels (default: 3).
            min_rows (int): Minimum number of rows (default: 3).
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
        Distribute labels across rows based on available width.

        Args:
            available_width (int): Terminal width in characters.

        Returns:
            list: List of lists, each containing labels for one row.
        """
        if available_width <= 0:
            available_width = 80  # Fallback width

        rows = []
        current_row = []
        current_width = 0

        for label in self.labels:
            label_width = self._estimate_label_width(label)

            # Check if this label fits in the current row
            if current_width + label_width <= available_width:
                current_row.append(label)
                current_width += label_width
            else:
                # Start a new row if current row is not empty
                if current_row:
                    rows.append(current_row)
                    current_row = [label]
                    current_width = label_width
                else:
                    # Label is too wide for available width, add it anyway
                    current_row.append(label)
                    rows.append(current_row)
                    current_row = []
                    current_width = 0

        # Add the last row if not empty
        if current_row:
            rows.append(current_row)

        # Ensure minimum number of rows
        while len(rows) < self.min_rows:
            rows.append([])

        return rows

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

        # Distribute labels across rows
        rows = self._distribute_labels(available_width)

        # Create VSplit for each row
        row_containers = []
        for row in rows:
            if row:
                row_containers.append(VSplit(row))
            else:
                # Empty row - add an empty window
                row_containers.append(
                    Window(
                        FormattedTextControl(text=""),
                        height=1,
                    )
                )

        return HSplit(row_containers)
