"""A module containing functions for graceful error handling."""

import traceback
from pathlib import Path


def error_handler(func):
    """
    Wrap a function in a try/except block to catch errors.

    Errors are printed to the mini buffer with detailed context including:
    - Class name (if method)
    - Module and file location
    - Line number where error occurred
    - Full exception message

    Args:
        func (function):
            The function to wrap.
    """

    def wrapper(*args, **kwargs):
        """Wrap the function."""
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # Re-raise the KeyboardInterrupt to ensure it's not caught here
            raise
        except Exception as e:
            # Nested import to avoid circular dependencies
            from h5forest.h5_forest import H5Forest

            # Get detailed error context
            tb = traceback.extract_tb(e.__traceback__)

            # Find the frame where the error actually occurred (last frame)
            if tb:
                last_frame = tb[-1]
                filename = Path(last_frame.filename).name
                lineno = last_frame.lineno
                location = f"{filename}:{lineno}"
            else:
                location = "unknown"

            # Try to get class name if this is a method
            qualname = func.__qualname__
            if "." in qualname:
                # It's a method, extract class name
                class_name = qualname.rsplit(".", 1)[0]
                method_name = qualname.rsplit(".", 1)[1]
                context = f"{class_name}.{method_name}"
            else:
                # It's a function
                context = func.__name__

            # Build error message with context
            error_msg = f"ERROR@{context} ({location}): {e}"

            H5Forest().print(error_msg)

    return wrapper
