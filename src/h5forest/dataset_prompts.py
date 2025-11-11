"""Module for handling user prompts when interacting with datasets.
This module provides an abstraction for prompting users before performing
operations on chunked or large datasets. It ensures users are aware of
the implications of their actions and can make informed decisions.
"""


def prompt_for_chunking_preference(app, nodes, operation_callback):
    """
    Prompt user about chunking preference for plotting/histogram operations.

    This function checks if any of the provided nodes are chunked, and
    prompts the user to decide whether to use chunked processing.

    Args:
        app (H5Forest):
            The main application instance.
        nodes (list):
            List of Node objects to check for chunking.
        operation_callback (callable):
            Function to call with signature: operation_callback(use_chunks)
            where use_chunks is True to use chunked processing.
    """
    # Check if config has always_chunk enabled
    if app.config.always_chunk_datasets():
        operation_callback(use_chunks=True)
        return

    # Check if any node is chunked
    has_chunked = any(node.is_chunked for node in nodes)

    # If no chunked data, proceed without chunking
    if not has_chunked:
        operation_callback(use_chunks=False)
        return

    # At this point, we have chunked data and need to prompt
    # Calculate memory footprint for all nodes
    import h5py
    import numpy as np

    total_size_gb = 0.0
    total_chunks = 0

    try:
        for node in nodes:
            if node.is_chunked:
                with h5py.File(node.filepath, "r") as hdf:
                    dataset = hdf[node.path]
                    uncompressed_bytes = dataset.size * dataset.dtype.itemsize
                    total_size_gb += uncompressed_bytes / (10**9)

                    if dataset.chunks:
                        num_chunks = int(
                            np.prod(
                                [
                                    np.ceil(s / c)
                                    for s, c in zip(
                                        dataset.shape, dataset.chunks
                                    )
                                ]
                            )
                        )
                        total_chunks += num_chunks
    except (OSError, FileNotFoundError, KeyError):
        # If file access fails, use node's nbytes as estimate
        for node in nodes:
            if node.is_chunked:
                total_size_gb += node.nbytes / (10**9)
        total_chunks = "unknown"

    def on_yes_chunk():
        """User wants chunk-by-chunk processing."""
        app.default_focus()
        operation_callback(use_chunks=True)

    def on_no_chunk():
        """User wants to load all at once."""
        app.default_focus()

        def on_yes_load_all():
            """User confirms loading all at once."""
            app.default_focus()
            operation_callback(use_chunks=False)

        def on_no_load_all():
            """User wants to abort."""
            app.default_focus()
            app.print("Operation aborted.")

        # Ask second question
        app.prompt_yn(
            "Should we load all at once? (If not, we will abort) [y/n]:",
            on_yes_load_all,
            on_no_load_all,
        )

    # Build the prompt message
    if isinstance(total_chunks, int) and total_chunks > 0:
        prompt_msg = (
            f"Chunked Dataset found ({total_size_gb:.2f} GB, "
            f"{total_chunks} chunks). "
            f"Should we process chunk by chunk? [y/n]:"
        )
    else:
        prompt_msg = (
            f"Chunked Dataset found ({total_size_gb:.2f} GB). "
            f"Should we process chunk by chunk? [y/n]:"
        )

    app.prompt_yn(
        prompt_msg,
        on_yes_chunk,
        on_no_chunk,
    )


def prompt_for_chunked_dataset(
    app, node, operation_callback, return_to_normal=True
):
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
            Function to call with signature: operation_callback(use_chunks,
            load_all) where use_chunks is True to use chunked processing,
            and load_all is True to load all data at once.
        return_to_normal (bool):
            If True, return to normal mode after operation completes.
            If False, stay in current mode. Default: True.
    """
    # First, check if dataset is chunked
    if not node.is_chunked:
        # Not chunked, proceed normally
        operation_callback(use_chunks=False, load_all=True)
        return

    # Calculate memory footprint and chunk information
    import h5py
    import numpy as np

    try:
        with h5py.File(node.filepath, "r") as hdf:
            dataset = hdf[node.path]
            uncompressed_bytes = dataset.size * dataset.dtype.itemsize
            uncompressed_gb = uncompressed_bytes / (10**9)

            # Calculate number of chunks
            if dataset.chunks:
                # Total number of chunks = product of (shape[i] / chunks[i])
                # for each dimension
                num_chunks = int(
                    np.prod(
                        [
                            np.ceil(s / c)
                            for s, c in zip(dataset.shape, dataset.chunks)
                        ]
                    )
                )
            else:
                num_chunks = 1
    except (OSError, FileNotFoundError, KeyError):
        # If file access fails, use node's nbytes as estimate
        uncompressed_gb = node.nbytes / (10**9)
        num_chunks = "unknown"

    def on_yes_chunk_by_chunk():
        """User wants chunk-by-chunk processing."""
        app.default_focus()
        operation_callback(use_chunks=True, load_all=False)
        if return_to_normal:
            app.return_to_normal_mode()

    def on_no_chunk_by_chunk():
        """User doesn't want chunk-by-chunk, ask about loading all."""
        app.default_focus()

        def on_yes_load_all():
            """User wants to load all at once."""
            app.default_focus()
            operation_callback(use_chunks=False, load_all=True)
            if return_to_normal:
                app.return_to_normal_mode()

        def on_no_load_all():
            """User wants to abort."""
            app.default_focus()
            app.print("Operation aborted.")
            if return_to_normal:
                app.return_to_normal_mode()

        # Ask second question
        app.prompt_yn(
            "Should we load all at once? (If not, we will abort) [y/n]:",
            on_yes_load_all,
            on_no_load_all,
        )

    # Start the prompt workflow with enhanced message
    if isinstance(num_chunks, int):
        prompt_msg = (
            f"Chunked Dataset found ({uncompressed_gb:.2f} GB, "
            f"{num_chunks} chunks). "
            f"Should we process chunk by chunk? [y/n]:"
        )
    else:
        prompt_msg = (
            f"Chunked Dataset found ({uncompressed_gb:.2f} GB). "
            f"Should we process chunk by chunk? [y/n]:"
        )

    app.prompt_yn(
        prompt_msg,
        on_yes_chunk_by_chunk,
        on_no_chunk_by_chunk,
    )


def prompt_for_large_dataset(
    app, node, operation_callback, return_to_normal=True
):
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
        return_to_normal (bool):
            If True, return to normal mode after operation completes.
            If False, stay in current mode. Default: True.
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

    def on_yes():
        """User confirms, proceed with operation."""
        app.default_focus()
        operation_callback()
        if return_to_normal:
            app.return_to_normal_mode()

    def on_no():
        """User wants to abort."""
        app.default_focus()
        app.print("Operation aborted.")
        if return_to_normal:
            app.return_to_normal_mode()

    # Prompt the user
    app.prompt_yn(
        f"This dataset is {uncompressed_gb:.2f} GB uncompressed. "
        f"Proceed with load? [y/n]:",
        on_yes,
        on_no,
    )


def prompt_for_dataset_operation(
    app, node, operation_callback, return_to_normal=True
):
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
        return_to_normal (bool):
            If True, return to normal mode after operation completes.
            If False, stay in current mode. Default: True.
    """
    # The config has the option to turn off these prompts entirely
    if app.config.always_chunk_datasets():
        operation_callback(use_chunks=True)
        return

    def after_chunk_prompt(use_chunks, load_all):
        """Called after chunked dataset prompt is resolved."""
        # If user chose chunk-by-chunk processing, proceed immediately
        if use_chunks:
            operation_callback(use_chunks=True)
            return

        # If user declined both chunk-by-chunk and load-all, abort
        if not load_all:
            app.print("Operation aborted.")
            if return_to_normal:
                app.return_to_normal_mode()
            return

        # User wants to load all at once, check for large dataset
        def after_size_prompt():
            """Called after large dataset prompt is resolved."""
            operation_callback(use_chunks=False)

        prompt_for_large_dataset(
            app, node, after_size_prompt, return_to_normal
        )

    # Start with chunked dataset prompt
    prompt_for_chunked_dataset(app, node, after_chunk_prompt, return_to_normal)
