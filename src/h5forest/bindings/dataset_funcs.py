"""A submodule containing the dataset mode keybindings for H5Forest.

This module contains the keybindings for the dataset mode. The dataset
mode allows the user to interact with the dataset, such as viewing the
values, getting the minimum and maximum, mean, and standard deviation.
The functions in this module should not be called directly, but are
intended to be used by the main application.
"""

import threading

from h5forest.dataset_prompts import prompt_for_dataset_operation
from h5forest.errors import error_handler


@error_handler
def show_values(event):
    """
    Show the values of a dataset.

    This will truncate the value list if the array is large so as not
    to flood memory.
    """
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the node under the cursor
    node = app.tree.get_current_node(app.current_row)

    # Exit if the node is not a Dataset
    if node.is_group:
        app.print(f"{node.path} is not a Dataset")
        return

    # Get the value string
    text = node.get_value_text()

    # Ensure there's something to draw
    if len(text) == 0:
        return

    app.value_title.update_title(f"Values: {node.path}")

    # Update the text
    app.values_content.text = text

    # Flag that there are values to show
    app.flag_values_visible = True

    # Exit values mode
    app.return_to_normal_mode()


@error_handler
def show_values_in_range(event):
    """Show the values of a dataset in an index range."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the node under the cursor
    node = app.tree.get_current_node(app.current_row)

    # Exit if the node is not a Dataset
    if node.is_group:
        app.print(f"{node.path} is not a Dataset")
        return

    def values_in_range_callback():
        """Get the start and end indices from the user input."""
        # Parse the range
        string_values = tuple([s.strip() for s in app.user_input.split("-")])

        # Attempt to convert to an int
        try:
            start_index = int(string_values[0])
            end_index = int(string_values[1])
        except ValueError:
            app.print(
                "Invalid input! Input must be a integers "
                f"separated by -, not ({app.user_input})"
            )

            # Exit this attempt gracefully
            app.default_focus()
            app.return_to_normal_mode()
            return

        # Return focus to the tree
        app.default_focus()

        # Get the value string
        text = node.get_value_text(
            start_index=start_index, end_index=end_index
        )

        # Ensure there's something to draw
        if len(text) == 0:
            return

        app.value_title.update_title(f"Values: {node.path}")

        # Update the text
        app.values_content.text = text

        # Flag that there are values to show
        app.flag_values_visible = True

        # Exit values mode
        app.return_to_normal_mode()

    # Get the indices from the user
    app.input(
        "Enter the index range (separated by -):",
        values_in_range_callback,
    )


@error_handler
def close_values(event):
    """Close the value pane."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    app.flag_values_visible = False
    app.values_content.text = ""

    # Exit values mode
    app.return_to_normal_mode()


@error_handler
def minimum_maximum(event):
    """Show the minimum and maximum values of a dataset."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the node under the cursor
    node = app.tree.get_current_node(app.current_row)

    # Exit if the node is not a Dataset
    if node.is_group:
        app.print(f"{node.path} is not a Dataset")
        return

    def run_operation(use_chunks):
        """Run the min/max operation after user confirmation."""

        @error_handler
        def run_in_thread():
            # Get the value string
            vmin, vmax = node.get_min_max()

            # Print the result on the main thread
            app.app.loop.call_soon_threadsafe(
                app.print,
                f"{node.path}: Minimum = {vmin},  Maximum = {vmax}",
            )

            # Exit values mode
            app.return_to_normal_mode()

        # Start the operation in a new thread
        threading.Thread(target=run_in_thread, daemon=True).start()

    # Prompt user if needed, then run operation
    prompt_for_dataset_operation(app, node, run_operation)


@error_handler
def mean(event):
    """Show the mean of a dataset."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the node under the cursor
    node = app.tree.get_current_node(app.current_row)

    # Exit if the node is not a Dataset
    if node.is_group:
        app.print(f"{node.path} is not a Dataset")
        return

    def run_operation(use_chunks):
        """Run the mean operation after user confirmation."""

        @error_handler
        def run_in_thread():
            # Get the value string
            vmean = node.get_mean()

            # Print the result on the main thread
            app.app.loop.call_soon_threadsafe(
                app.print,
                f"{node.path}: Mean = {vmean}",
            )

            # Exit values mode
            app.return_to_normal_mode()

        # Start the operation in a new thread
        threading.Thread(target=run_in_thread, daemon=True).start()

    # Prompt user if needed, then run operation
    prompt_for_dataset_operation(app, node, run_operation)


@error_handler
def std(event):
    """Show the standard deviation of a dataset."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Get the node under the cursor
    node = app.tree.get_current_node(app.current_row)

    # Exit if the node is not a Dataset
    if node.is_group:
        app.print(f"{node.path} is not a Dataset")
        return

    def run_operation(use_chunks):
        """Run the std operation after user confirmation."""

        @error_handler
        def run_in_thread():
            # Get the value string
            vstd = node.get_std()

            # Print the result on the main thread
            app.app.loop.call_soon_threadsafe(
                app.print,
                f"{node.path}: Standard Deviation = {vstd}",
            )

            # Exit values mode
            app.return_to_normal_mode()

        # Start the operation in a new thread
        threading.Thread(target=run_in_thread, daemon=True).start()

    # Prompt user if needed, then run operation
    prompt_for_dataset_operation(app, node, run_operation)
