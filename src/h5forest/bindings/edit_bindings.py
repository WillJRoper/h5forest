"""This module contains the keybindings for the edit mode.

The edit mode allows users to rename groups and datasets in the HDF5 file.
This involves a two-step process: editing the name and confirming the
operation. The backend handles copying data to the new location and removing
the old data.

This module defines the functions for binding edit mode events to functions.
This should not be used directly, but instead provides the functions for the
application.
"""

import h5py
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import VSplit
from prompt_toolkit.widgets import Label

from h5forest.errors import error_handler


def _init_edit_bindings(app):
    """Set up the keybindings for the edit mode."""

    @error_handler
    def edit_name(event):
        """Edit the name of the current node."""
        # Get the current node
        try:
            node = app.tree.get_current_node(app.current_row)
        except IndexError:
            app.print("No item selected for editing")
            app.return_to_normal_mode()
            return

        # Store the node being edited
        app.edit_node = node
        app.original_name = node.name

        def edit_name_callback():
            """Handle the edited name input."""
            new_name = app.user_input.strip()

            # Validate the new name
            if not new_name:
                app.print("Name cannot be empty")
                app.return_to_normal_mode()
                return

            if new_name == app.original_name:
                app.print("Name unchanged")
                app.return_to_normal_mode()
                return

            # Check for invalid characters
            if "/" in new_name:
                app.print("Name cannot contain '/' character")
                app.return_to_normal_mode()
                return

            # Store the new name and ask for confirmation
            app.new_name = new_name
            confirm_rename()

        # Get the new name from user
        app.input(
            f"Edit name for {node.name}:",
            edit_name_callback,
            mini_buffer_text=node.name,
        )

    def confirm_rename():
        """Ask user to confirm the rename operation."""
        node = app.edit_node
        node_type = "Group" if node.is_group else "Dataset"

        def confirm_callback():
            """Handle the confirmation response."""
            response = app.user_input.strip().lower()

            if response in ["y", "yes"]:
                # Start the rename operation
                perform_rename()
            else:
                app.print("Rename cancelled")
                app.return_to_normal_mode()

        app.input(
            f"Rename {node_type} '{app.original_name}' to"
            f" '{app.new_name}'? (y/n):",
            confirm_callback,
        )

    def perform_rename():
        """Perform the actual rename operation."""
        node = app.edit_node

        # Check if target already exists
        if node.parent is None:
            # Root level item
            new_path = f"/{app.new_name}"
        else:
            parent_path = node.parent.path
            if parent_path == "/":
                new_path = f"/{app.new_name}"
            else:
                new_path = f"{parent_path}/{app.new_name}"

        try:
            with h5py.File(app.tree.filepath, "r") as hdf:
                if new_path in hdf:
                    app.print(f"Name '{app.new_name}' already exists")
                    app.return_to_normal_mode()
                    return
        except (OSError, IOError) as e:
            app.print(f"Error accessing file: {str(e)}")
            app.return_to_normal_mode()
            return
        except Exception as e:
            app.print(f"Unexpected error checking target: {str(e)}")
            app.return_to_normal_mode()
            return

        # Show progress and start operation
        app.flag_progress_bar = True
        app.progress_bar_content.text = (
            f"Renaming {node.name} to {app.new_name}..."
        )
        app.app.invalidate()

        # Perform the rename operation directly (not in thread for safety)
        try:
            if node.is_group:
                rename_group(node, app.new_name)
            else:
                rename_dataset(node, app.new_name)
        except Exception as e:
            app.print(f"Rename operation failed: {str(e)}")
            app.flag_progress_bar = False
            app.app.invalidate()

        app.return_to_normal_mode()

    def rename_group(node, new_name):
        """Rename a group by copying all contents."""
        try:
            with h5py.File(app.tree.filepath, "a") as hdf:
                old_group = hdf[node.path]

                # Construct new path properly
                if node.parent is None:
                    new_path = f"/{new_name}"
                else:
                    parent_path = node.parent.path
                    if parent_path == "/":
                        new_path = f"/{new_name}"
                    else:
                        new_path = f"{parent_path}/{new_name}"

                # Create new group
                new_group = hdf.create_group(new_path)

                # Copy attributes
                for attr_name, attr_value in old_group.attrs.items():
                    new_group.attrs[attr_name] = attr_value

                # Recursively copy all contents
                def copy_contents(src_group, dst_group):
                    for key in src_group.keys():
                        src_item = src_group[key]
                        if isinstance(src_item, h5py.Group):
                            # Copy subgroup
                            dst_subgroup = dst_group.create_group(key)
                            for (
                                attr_name,
                                attr_value,
                            ) in src_item.attrs.items():
                                dst_subgroup.attrs[attr_name] = attr_value
                            copy_contents(src_item, dst_subgroup)
                        else:
                            # Copy dataset with all properties
                            try:
                                dst_dataset = dst_group.create_dataset(
                                    key,
                                    shape=src_item.shape,
                                    dtype=src_item.dtype,
                                    chunks=src_item.chunks,
                                    compression=src_item.compression,
                                    compression_opts=src_item.compression_opts,
                                    fillvalue=src_item.fillvalue,
                                )
                                # Copy attributes
                                for (
                                    attr_name,
                                    attr_value,
                                ) in src_item.attrs.items():
                                    dst_dataset.attrs[attr_name] = attr_value
                                # Copy data
                                if src_item.size >= 1000000:
                                    copy_dataset_chunked(src_item, dst_dataset)
                                else:
                                    dst_dataset[...] = src_item[...]
                            except Exception as e:
                                app.print(
                                    f"Error copying dataset {key}: {str(e)}"
                                )

                copy_contents(old_group, new_group)

                # Delete old group
                del hdf[node.path]

            app.print(f"Successfully renamed group to {new_name}")
            # Refresh the tree display
            refresh_tree_display()

        except (OSError, IOError) as e:
            app.print(f"File I/O error during group rename: {str(e)}")
        except h5py.Error as e:
            app.print(f"HDF5 error during group rename: {str(e)}")
        except MemoryError:
            app.print("Memory error: Group too large for rename operation")
        except Exception as e:
            app.print(f"Unexpected error during group rename: {str(e)}")
        finally:
            app.flag_progress_bar = False
            app.app.invalidate()

    def rename_dataset(node, new_name):
        """Rename a dataset by copying data in chunks."""
        try:
            with h5py.File(app.tree.filepath, "a") as hdf:
                old_dataset = hdf[node.path]

                # Construct new path properly
                if node.parent is None:
                    new_path = f"/{new_name}"
                else:
                    parent_path = node.parent.path
                    if parent_path == "/":
                        new_path = f"/{new_name}"
                    else:
                        new_path = f"{parent_path}/{new_name}"

                # Create new dataset with same properties
                new_dataset = hdf.create_dataset(
                    new_path,
                    shape=old_dataset.shape,
                    dtype=old_dataset.dtype,
                    chunks=old_dataset.chunks,
                    compression=old_dataset.compression,
                    compression_opts=old_dataset.compression_opts,
                    fillvalue=old_dataset.fillvalue,
                )

                # Copy attributes
                for attr_name, attr_value in old_dataset.attrs.items():
                    new_dataset.attrs[attr_name] = attr_value

                # Copy data in chunks
                if (
                    old_dataset.size >= 1000000
                ):  # Use chunked copy for large datasets
                    copy_dataset_chunked(old_dataset, new_dataset)
                else:
                    # For small datasets, simple copy
                    new_dataset[...] = old_dataset[...]

                # Delete old dataset
                del hdf[node.path]

            app.print(f"Successfully renamed dataset to {new_name}")
            # Refresh the tree display
            refresh_tree_display()

        except (OSError, IOError) as e:
            app.print(f"File I/O error during dataset rename: {str(e)}")
        except h5py.Error as e:
            app.print(f"HDF5 error during dataset rename: {str(e)}")
        except MemoryError:
            app.print("Memory error: Dataset too large for rename operation")
        except Exception as e:
            app.print(f"Unexpected error during dataset rename: {str(e)}")
        finally:
            app.flag_progress_bar = False
            app.app.invalidate()

    def refresh_tree_display():
        """Refresh the tree display after a rename operation."""
        try:
            # Store current cursor position
            current_pos = app.current_position

            # Recreate the tree from the file (since HDF5 structure changed)
            from h5forest.tree import Tree, TreeProcessor

            app.tree = Tree(app.tree.filepath)
            app.tree_processor = TreeProcessor(app.tree)

            # Update the tree content
            new_tree_text = app.tree.get_tree_text()
            safe_pos = (
                min(current_pos, len(new_tree_text) - 1)
                if new_tree_text
                else 0
            )
            app.tree_buffer.set_document(
                Document(text=new_tree_text, cursor_position=safe_pos),
                bypass_readonly=True,
            )

            # Update the tree content control to use new processor
            app.tree_content.content.input_processors = [app.tree_processor]

            # Force refresh of the interface
            app.app.invalidate()

        except Exception as e:
            app.print(f"Warning: Could not refresh tree display: {str(e)}")

    def copy_dataset_chunked(src_dataset, dst_dataset):
        """Copy a dataset in chunks to avoid memory issues."""
        try:
            # Determine chunk size based on data type and available memory
            chunk_size = min(
                100000, src_dataset.size // 100
            )  # At least 100 chunks

            total_elements = src_dataset.size
            copied_elements = 0

            # Flatten view for easier chunking
            src_flat = src_dataset.reshape(-1)
            dst_flat = dst_dataset.reshape(-1)

            while copied_elements < total_elements:
                end_idx = min(copied_elements + chunk_size, total_elements)
                chunk_data = src_flat[copied_elements:end_idx]
                dst_flat[copied_elements:end_idx] = chunk_data
                copied_elements = end_idx

                # Update progress periodically
                if (
                    copied_elements % chunk_size == 0
                ):  # Update after each chunk
                    progress = int((copied_elements / total_elements) * 100)
                    app.progress_bar_content.text = (
                        f"Copying {src_dataset.name}: {progress}%"
                    )
                    app.app.invalidate()

        except MemoryError:
            app.print(
                f"Memory error during chunked copy of {src_dataset.name}"
            )
            raise
        except (OSError, IOError) as e:
            app.print(f"I/O error during chunked copy: {str(e)}")
            raise
        except Exception as e:
            app.print(f"Error during chunked copy: {str(e)}")
            raise

    # Bind the edit name function
    app.kb.add("e", filter=Condition(lambda: app.flag_edit_mode))(edit_name)

    # Add the hot keys
    hot_keys = VSplit(
        [
            Label("e → Edit Name"),
            Label("q → Exit Edit Mode"),
        ]
    )

    return hot_keys
