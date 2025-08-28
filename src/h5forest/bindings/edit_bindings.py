"""This module contains the keybindings for direct editing functionality.

Direct editing allows users to immediately edit whatever is under the cursor:
- Tree items (groups/datasets): rename them
- Attributes in the attributes panel: edit attribute values

This provides a streamlined workflow where pressing 'e' immediately starts
editing the current item without entering a separate mode.
"""

import h5py
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import VSplit

from h5forest.errors import error_handler


def collect_expansion_state(node, states=None):
    """
    Collect expansion state as a hierarchical structure.

    Returns a dict mapping node names to their expansion info,
    which is more robust to renames than absolute paths.
    """
    if states is None:
        states = {}

    if node.is_expanded:
        # Store this node's expansion state and its children's states
        states[node.name] = {"expanded": True, "children": {}}
        for child in node.children:
            collect_expansion_state(child, states[node.name]["children"])
    else:
        states[node.name] = {"expanded": False, "children": {}}

    return states


def restore_expansion_state(node, states, tree=None):
    """Restore expansion state from hierarchical structure."""
    if tree is None:
        tree = node  # For root node case

    node_state = states.get(node.name, {})

    if node_state.get("expanded", False) and node.has_children:
        if not node.is_expanded:
            # For tree root, use parse_level, for others open_node
            if hasattr(tree, "parse_level"):
                tree.parse_level(node)
            else:
                node.open_node()

        # Recursively restore children states
        child_states = node_state.get("children", {})
        for child in node.children:
            restore_expansion_state(child, child_states, tree)


def find_node_position_in_text(tree_text, node_path):
    """Find the cursor position for a node with given path in tree text."""
    if not node_path:
        return None

    lines = tree_text.split("\n")
    position = 0

    # For root node (path="/"), look for first line
    if node_path == "/":
        return 0

    # Extract the actual node name from the path
    if "/" in node_path:
        target_name = node_path.split("/")[-1]
    else:
        target_name = node_path

    for line in lines:
        # Extract node name from tree text line
        # Lines look like: "    ▼ node_name" or "      node_name"
        stripped = line.strip()
        if stripped:
            # Remove tree indicators and get node name
            node_name = stripped.lstrip("▼▶ ")
            # Check if this is our target node
            if node_name == target_name:
                return position
        position += len(line) + 1  # +1 for newline

    return None


def _init_edit_bindings(app):
    """Set up the keybindings for direct editing."""

    @error_handler
    def direct_edit(event):
        """Edit whatever is currently under the cursor."""
        # Check what has focus to determine edit context
        current_focus = app.app.layout.current_window

        if current_focus == app.tree_content:
            # Editing tree item (rename)
            edit_tree_item()
        elif current_focus == app.attributes_content:
            # Editing attribute
            edit_attribute()
        else:
            # Default to tree editing if focus is unclear
            edit_tree_item()

    def edit_tree_item():
        """Edit/rename the current tree item."""
        # Get the current node
        try:
            node = app.tree.get_current_node(app.current_row)
        except IndexError:
            app.print("No item selected for editing")
            return

        def rename_callback():
            """Handle the rename operation."""
            new_name = app.user_input.strip()

            # Validate the new name
            if not new_name:
                app.print("Name cannot be empty")
                app.default_focus()
                return

            if new_name == node.name:
                app.print("Name unchanged")
                app.default_focus()
                return

            # Check for invalid characters
            if "/" in new_name:
                app.print("Name cannot contain '/' character")
                app.default_focus()
                return

            # Perform the rename directly
            perform_rename(node, new_name)
            app.default_focus()

        # Start editing with current name pre-filled
        app.input(
            f"Rename {node.name}:",
            rename_callback,
            mini_buffer_text=node.name,
        )

    def edit_attribute():
        """Edit an attribute key and value."""
        # Get the current node to access its attributes
        try:
            node = app.tree.get_current_node(app.current_row)
        except IndexError:
            app.print("No item selected")
            return

        # Get the cursor position in the attributes panel
        attr_doc = app.attributes_content.buffer.document
        attr_cursor_row = attr_doc.cursor_position_row

        # Use the proper attribute cursor tracking
        original_key, original_value = node.get_current_attribute(
            attr_cursor_row
        )

        # Check if cursor is on a valid attribute
        if original_key is None:
            app.print("No attribute under cursor")
            app.default_focus()
            return

        # Step 1: Edit the key
        def edit_key_callback():
            """Handle key editing (first step)."""
            new_key = app.user_input.strip()

            if not new_key:
                app.print("Key cannot be empty")
                app.default_focus()
                return

            # Step 2: Edit the value
            def edit_value_callback():
                """Handle value editing (second step)."""
                new_value_str = app.user_input.strip()

                try:
                    # Try to convert value to appropriate type
                    try:
                        parsed_value = int(new_value_str)
                    except ValueError:
                        try:
                            parsed_value = float(new_value_str)
                        except ValueError:
                            # Handle string values, including 'None'
                            if new_value_str.lower() == "none":
                                parsed_value = None
                            else:
                                parsed_value = new_value_str

                    # Remove old attribute if key changed
                    if (
                        new_key != original_key
                        and original_key in node.obj.attrs
                    ):
                        del node.obj.attrs[original_key]
                        # Also remove from cached attrs dict
                        if original_key in node.attrs:
                            del node.attrs[original_key]

                    # Set the new/updated attribute
                    node.obj.attrs[new_key] = parsed_value
                    # Also update cached attrs dict
                    node.attrs[new_key] = parsed_value
                    app.print(
                        f"Set {node.path}.attrs['{new_key}'] = {parsed_value}"
                    )

                    # Clear cached attribute text to force refresh of mapping
                    node._attr_text = None

                    # Refresh the attributes display
                    app.attributes_content.text = node.get_attr_text()
                    app.app.invalidate()

                except Exception as e:
                    app.print(f"Error setting attribute: {e}")

                # Always return focus to attributes panel to continue editing
                app.shift_focus(app.attributes_content)

            # Start value editing
            app.input(
                f"Edit value for '{new_key}':",
                edit_value_callback,
                mini_buffer_text=str(original_value),
            )

        # Start key editing
        app.input(
            "Edit attribute key:",
            edit_key_callback,
            mini_buffer_text=original_key,
        )

    def perform_rename(node, new_name):
        """Perform the actual rename operation."""
        # Check if target already exists
        if node.parent is None:
            # Root level item
            new_path = f"/{new_name}"
        else:
            parent_path = node.parent.path
            if parent_path == "/":
                new_path = f"/{new_name}"
            else:
                new_path = f"{parent_path}/{new_name}"

        try:
            with h5py.File(app.tree.filepath, "r") as hdf:
                if new_path in hdf:
                    app.print(f"Name '{new_name}' already exists")
                    app.default_focus()
                    return
        except (OSError, IOError) as e:
            app.print(f"Error accessing file: {str(e)}")
            app.default_focus()
            return
        except Exception as e:
            app.print(f"Unexpected error checking target: {str(e)}")
            app.default_focus()
            return

        # Show progress and start operation
        app.flag_progress_bar = True
        app.progress_bar_content.text = (
            f"Renaming {node.name} to {new_name}..."
        )
        app.app.invalidate()

        # Perform the rename operation directly
        try:
            if node.is_group:
                rename_group(node, new_name)
            else:
                rename_dataset(node, new_name)
        except Exception as e:
            app.print(f"Rename operation failed: {str(e)}")
            app.flag_progress_bar = False
            app.app.invalidate()
            app.default_focus()

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
            # Return focus to tree
            app.default_focus()

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
            app.default_focus()

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
            # Return focus to tree
            app.default_focus()

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
            app.default_focus()

    def refresh_tree_display():
        """Refresh the tree display after a rename operation."""
        try:
            # Store current cursor position and row
            current_pos = app.current_position
            current_row = app.current_row

            # Store the expansion state hierarchically
            expansion_states = collect_expansion_state(app.tree.root)

            # Store the currently selected node path for cursor restoration
            try:
                current_node = app.tree.get_current_node(current_row)
                current_node_path = current_node.path
            except (IndexError, AttributeError):
                current_node_path = None

            # Recreate the tree from the file (since HDF5 structure changed)
            from h5forest.tree import Tree, TreeProcessor

            app.tree = Tree(app.tree.filepath)
            app.tree_processor = TreeProcessor(app.tree)

            # Re-expand nodes that were previously expanded
            restore_expansion_state(app.tree.root, expansion_states, app.tree)

            # Update the tree content
            new_tree_text = app.tree.get_tree_text()

            # Try to restore cursor to the same node (accounting for renames)
            target_pos = find_node_position_in_text(
                new_tree_text, current_node_path
            )
            if target_pos is None:
                # Fallback to safe position if node not found
                target_pos = (
                    min(current_pos, len(new_tree_text) - 1)
                    if new_tree_text
                    else 0
                )

            app.tree_buffer.set_document(
                Document(text=new_tree_text, cursor_position=target_pos),
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

    # Bind the direct edit function to work from normal mode
    app.kb.add("e", filter=Condition(lambda: app.flag_normal_mode))(
        direct_edit
    )

    # Return empty hot keys since this is no longer a mode
    # The 'e' key will be shown in the normal mode hotkeys
    return VSplit([])
