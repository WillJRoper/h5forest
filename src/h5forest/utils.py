"""A module containing utility functions and classes for the HDF5 viewer."""
import os


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
    """Get the terminal window size."""
    rows, columns = os.popen("stty size", "r").read().split()
    return int(rows), int(columns)


def calculate_new_cursor_position(current_row, node, text):
    """Calculate the new cursor position after text update."""
    # Split the text
    lines = text.split("\n")

    # Sum all the characters up to position.
    # +1 for newline characters
    new_position = sum(len(lines[i]) + 1 for i in range(current_row))
    return new_position
