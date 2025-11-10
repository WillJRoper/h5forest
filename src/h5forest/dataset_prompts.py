"""Module for handling user prompts when interacting with datasets.

This module provides an abstraction for prompting users before performing
operations on chunked or large datasets. It ensures users are aware of
the implications of their actions and can make informed decisions.
"""


def prompt_for_chunked_dataset(app, node, operation_callback):
    """
    Prompt user about how to handle a chunked dataset.

    This function implements a two-stage prompt workflow:
    1. Ask if the user wants to process chunk by chunk
    2. If no, ask if they want to load all at once or abort

    Args:
        app (H5Forest):
            The main application instance.
        node (Node):
            The dataset node to operate on.
        operation_callback (callable):
            Function to call with signature: operation_callback(use_chunks, load_all)
            where use_chunks is True to use chunked processing,
            and load_all is True to load all data at once.
    """
    # First, check if dataset is chunked
    if not node.is_chunked:
        # Not chunked, proceed normally
        operation_callback(use_chunks=False, load_all=True)
        return

    def chunk_by_chunk_callback():
        """Handle the first prompt response."""
        response = app.user_input.strip().lower()

        # Return focus to the tree
        app.default_focus()

        if response in ["y", "yes"]:
            # User wants chunk-by-chunk processing
            operation_callback(use_chunks=True, load_all=False)
            app.return_to_normal_mode()
        elif response in ["n", "no"]:
            # User doesn't want chunk-by-chunk, ask about loading all
            app.input(
                "Should we load all at once? (If not, we will abort) [y/n]:",
                load_all_callback,
            )
        else:
            app.print(f"Invalid input: {app.user_input}. Operation aborted.")
            app.return_to_normal_mode()

    def load_all_callback():
        """Handle the second prompt response."""
        response = app.user_input.strip().lower()

        # Return focus to the tree
        app.default_focus()

        if response in ["y", "yes"]:
            # User wants to load all at once
            operation_callback(use_chunks=False, load_all=True)
        elif response in ["n", "no"]:
            # User wants to abort
            app.print("Operation aborted.")
        else:
            app.print(f"Invalid input: {app.user_input}. Operation aborted.")

        app.return_to_normal_mode()

    # Start the prompt workflow
    app.input(
        "Chunked Dataset found. Should we process chunk by chunk? [y/n]:",
        chunk_by_chunk_callback,
    )


def prompt_for_large_dataset(app, node, operation_callback):
    """
    Prompt user before loading a large dataset.

    This function checks if a dataset is larger than 1GB uncompressed,
    and if so, asks the user to confirm before proceeding.

    Args:
        app (H5Forest):
            The main application instance.
        node (Node):
            The dataset node to operate on.
        operation_callback (callable):
            Function to call if user confirms, with no arguments.
    """
    # Calculate uncompressed size in GB using node metadata
    # Node already has size and datatype information
    import h5py

    # Try to get dtype itemsize from the node's datatype string
    # The node.datatype is a string like "float64", "int32", etc.
    try:
        with h5py.File(node.filepath, "r") as hdf:
            dataset = hdf[node.path]
            uncompressed_bytes = dataset.size * dataset.dtype.itemsize
            uncompressed_gb = uncompressed_bytes / (10**9)
    except (OSError, FileNotFoundError, KeyError):
        # If file access fails (e.g., in tests), use node's nbytes as estimate
        # nbytes is the compressed size, so uncompressed will be >= this
        # We'll use a conservative estimate here
        uncompressed_gb = node.nbytes / (10**9)

    # If dataset is less than 1GB, proceed without prompting
    if uncompressed_gb < 1.0:
        operation_callback()
        return

    def size_confirmation_callback():
        """Handle the size confirmation response."""
        response = app.user_input.strip().lower()

        # Return focus to the tree
        app.default_focus()

        if response in ["y", "yes"]:
            # User confirms, proceed with operation
            operation_callback()
        elif response in ["n", "no"]:
            # User wants to abort
            app.print("Operation aborted.")
        else:
            app.print(f"Invalid input: {app.user_input}. Operation aborted.")

        app.return_to_normal_mode()

    # Prompt the user
    app.input(
        f"This dataset is {uncompressed_gb:.2f} GB uncompressed. "
        f"Proceed with load? [y/n]:",
        size_confirmation_callback,
    )


def prompt_for_dataset_operation(app, node, operation_callback):
    """
    Combined prompt workflow for dataset operations.

    This function combines both chunked and large dataset prompts
    in a single workflow. It first checks for chunked datasets,
    then checks for large datasets before proceeding.

    Args:
        app (H5Forest):
            The main application instance.
        node (Node):
            The dataset node to operate on.
        operation_callback (callable):
            Function to call with signature: operation_callback(use_chunks)
            where use_chunks is True to use chunked processing.
    """

    def after_chunk_prompt(use_chunks, load_all):
        """Called after chunked dataset prompt is resolved."""
        # If user chose chunk-by-chunk processing, proceed immediately
        if use_chunks:
            operation_callback(use_chunks=True)
            return

        # If user declined both chunk-by-chunk and load-all, abort
        if not load_all:
            app.print("Operation aborted.")
            app.return_to_normal_mode()
            return

        # User wants to load all at once, check for large dataset
        def after_size_prompt():
            """Called after large dataset prompt is resolved."""
            operation_callback(use_chunks=False)

        prompt_for_large_dataset(app, node, after_size_prompt)

    # Start with chunked dataset prompt
    prompt_for_chunked_dataset(app, node, after_chunk_prompt)
