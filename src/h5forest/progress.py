from h5forest.utils import get_window_size
from h5forest.h5_forest import H5Forest


class ProgressBar:
    def __init__(self, total):
        self._total_steps = total
        self.max_length = get_window_size()[1] - 10
        self._current_step = 0
        self.forest = H5Forest()
        self.text_area = self.forest.progress_bar_content.text

    def update_progress(self, step):
        self.current_step = step
        filled_length = int(
            self.bar_length * self.current_step // self.total_steps
        )
        bar = "█" * filled_length + " " * (self.bar_length - filled_length)
        self.text_area.text = f"[{bar}] {self.current_step}/{self.total_steps}"

    def __enter__(self):
        # Initialize the progress display
        self.update_progress()
        self.forest.flag_progress_bar = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure the progress bar shows as complete
        self.update_progress(self.total_steps)

        # Reset the progress bar for potential reuse
        self.current_step = 0

        # Cleanup or final update if necessary
        self.forest.flag_progress_bar = False

    def advance(self, step=1):
        self.current_step += step
        self.update_progress()
