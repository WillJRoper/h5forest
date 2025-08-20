"""A module containing a custom progress bar.

This module contains a custom progress bar that can be used to display
progress in the application. This is needed because the prompt_toolkit
ProgressBar doesn't work within widget based applications. Additionally the
tqdm would require redirecting stdout and stderr which would break the entire
application.

Example usage:
    with ProgressBar(100) as bar:
        for i in range(100):
            bar.advance()
"""

from h5forest.utils import get_window_size


class ProgressBar:
    """
    A class to represent a progress bar.

    This class is a custom progress bar with a simple approach to displaying
    progress in a prompt_toolkit TextArea. This is needed because the
    prompt_toolkit ProgressBar doesn't work within widget based applications.
    Additionally the tqdm would require redirecting stdout and stderr which
    would break the entire application.

    Attributes:
        total_steps (int):
            The total number of steps to complete.
        max_length (int):
            The maximum length of the progress bar.
        current_step (int):
            The current step in the progress bar.
        forest (h5forest.h5_forest.H5Forest):
            The H5Forest instance to use for the progress bar.
        text_area (h5forest.h5_forest.TextArea):
            The text area to display the progress bar in.
    """

    def __init__(self, total, description=""):
        """
        Initialize the progress bar.

        Args:
            total (int):
                The total number of steps to complete.
        """
        from h5forest.h5_forest import H5Forest

        self.total_steps = total
        self.max_length = get_window_size()[1] - 4
        self.current_step = 0
        self.description = description
        self.forest = H5Forest()
        self.text_area = self.forest.progress_bar_content

        self.forest.flag_progress_bar = True

    def update_progress(self, step):
        """
        Update the progress bar.

        Args:
            step (int):
                The number of steps to increment the progress bar by.
        """
        # Increment the step
        self.current_step += step

        # Define the text that'll appear at the end
        back = (
            f"{self.current_step / self.total_steps * 100:.2f}% "
            f"({self.current_step}/{self.total_steps})"
            f" [{self.description}]"
        )

        # How long can the bar be including the end text?
        bar_length = self.max_length - len(back) - 3

        # Work out how many characters should be filled
        filled_length = int(bar_length * self.current_step // self.total_steps)

        # Define the bar
        bar = "█" * filled_length + " " * (bar_length - filled_length)

        # Update the text area
        self.text_area.text = f"{bar} | {back}"
        self.forest.app.invalidate()

    def __enter__(self):
        """Begin the progress bar."""
        # Initialize the progress display
        self.update_progress(step=0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End the progress bar.

        Args:
            exc_type (type):
                The type of the exception.
            exc_val (Exception):
                The exception instance.
            exc_tb (Traceback):
                The traceback.
        """
        # Ensure the progress bar shows as complete
        self.update_progress(self.total_steps)

        # Reset the progress bar for potential reuse
        self.current_step = 0

        # Cleanup and final update if necessary
        self.forest.flag_progress_bar = False
        self.forest.app.invalidate()

    def advance(self, step=1):
        """Advance the progress bar."""
        self.update_progress(step=step)
