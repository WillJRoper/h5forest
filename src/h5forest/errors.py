"""A module containing functions for graceful error handling."""


def error_handler(func):
    """
    Wrap a function in a try/except block to catch errors.

    Errors are printed to the mini buffer.

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

            H5Forest().print(f"ERROR@{func.__name__}: {e}")

    return wrapper
