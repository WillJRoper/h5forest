"""Tree class for the HDF5 file viewer.

This module contains the Tree class which is used to represent the HDF5 file
as a tree structure. The Tree contains Nodes which are used to represent the
groups and datasets in the HDF5 file. Each Node is lazy loaded, meaning that
its children are only loaded when it is opened.

Example usage:
    tree = Tree("example.h5")
    print(tree.get_tree_text())
"""

import threading
from pathlib import Path

import h5py
from prompt_toolkit.layout.processors import Processor, Transformation

from h5forest.node import Node


class TreeProcessor(Processor):
    def __init__(self, tree):
        self.tree = tree

    def apply_transformation(self, ti):
        lineno = ti.lineno
        fragments = ti.fragments

        # Access the node corresponding to the current line
        if lineno < len(self.tree.nodes_by_row):
            node = self.tree.nodes_by_row[lineno]
            style = ""

            if node.is_group:
                style += " class:group"
            if node.is_highlighted:
                style += " class:highlighted"
            if node.is_under_cursor:
                style += " class:under_cursor"

            # Apply the style to the entire line
            new_fragments = [(style, text) for _style, text in fragments]
            return Transformation(new_fragments)
        else:
            # Line number exceeds the number of nodes, return original
            # fragments
            return Transformation(fragments)


class Tree:
    """A class to represent the HDF5 file as a tree structure.

    This class is used to represent the HDF5 file as a tree structure. The
    tree is constructed from Node objects representing Groups and Datasets
    which are lazy loaded, meaning that the children of a node are only
    loaded when needed.

    Attributes:
        filepath (str):
            The path to the HDF5 file.
        roots (list):
            A list of the root level nodes in the tree.
        nodes_by_row (list):
            A list of all nodes in the tree by row in the tree output.
    """

    def __init__(self, filepath):
        """
        Initialise the tree.

        This will set up the attributes we'll need and parses the root level of
        the HDF5 file ready to be displayed.

        Args:
            filepath (str):
                The path to the HDF5 file.
        """
        # Store the file path we're working with
        self.filepath = filepath
        self.filename = Path(filepath).stem

        # Initialise a container to store nodes by row in the tree output
        self.nodes_by_row = []

        # Initialise containers to hold the tree text and split version
        # to avoid wasted computation
        self.tree_text = ""
        self.tree_text_split = []

        # Get the root of the level
        with h5py.File(self.filepath, "r") as hdf:
            self.root = Node(self.filename, hdf, self.filepath)
            self.root.is_under_cursor = True

        # Store the previous node under the cursor (we need some memory for
        # correct highlighting)
        self.prev_node = self.root

        # We'll collect a list of all the nodes in the background to
        # facilitate searches (lazy initialization - only when search is used)
        self.unpack_thread = None  # we'll do the unpacking on this thread
        self.all_node_paths = []
        self.all_node_paths_lock = (
            threading.Lock()
        )  # Protect concurrent access
        self.paths_initialized = (
            False  # Track if we've started collecting paths
        )
        self.index_building = (
            False  # Track if we're currently building the index
        )

        # Store the original tree state for search restoration
        self.original_tree_text = None
        self.original_tree_text_split = None
        self.original_nodes_by_row = None

        # Store filtered node rows for search navigation
        self.filtered_node_rows = []

    @property
    def length(self):
        """Return the length of the tree text."""
        return len(self.tree_text)

    @property
    def height(self):
        """Return the height of the tree text."""
        return len(self.nodes_by_row)

    @property
    def width(self):
        """
        Return the width of the tree text.

        Note that this works because every line is padded with spaces to
        the same length.
        """
        return len(self.tree_text_split[0])

    def parse_level(self, parent):
        """
        Open the parent group.

        This will populate the children dict on the node which will be parsed
        later when a text representation is requested updating the tree.

        Args:
            parent (Node):
                The parent node to open.
        """
        # Open this group
        parent.open_node()

    def _get_tree_text_recursive(self, current_node, text, nodes_by_row):
        """
        Parse the open nodes to produce the text tree representation.

        This will recurse through the open nodes constructing the output.

        Args:
            current_node (Node):
                The current node to parse.
            text (str):
                The current text representation of the tree.
            nodes_by_row (list):
                A list containing the nodes where the index is the row
                they are on in the text representation.

        Returns:
            str:
                The text representation of the tree.
            list:
                A list containing the nodes where the index is the row
                they are on in the text representation.
        """
        # Add this nodes representation
        text += f"{current_node.to_tree_text()}\n"

        # Append this node to the by row list
        nodes_by_row.append(current_node)

        # And include any children
        for child in current_node.children:
            text, nodes_by_row = self._get_tree_text_recursive(
                child,
                text,
                nodes_by_row,
            )

        return text, nodes_by_row

    def get_tree_text(self):
        """
        Return the text representation of the tree.

        Note that this is only called at initialisation and thus only parses
        the roots of the tree. Any future updates will be done via
        update_tree_text. This is to avoid recalculating the full tree for
        every change.

        Returns:
            str:
                The text representation of the tree.
        """
        text = ""
        nodes_by_row = []
        text, nodes_by_row = self._get_tree_text_recursive(
            self.root,
            text,
            nodes_by_row,
        )

        # Store the nodes by row
        self.nodes_by_row = nodes_by_row

        # Store the tree text
        self.tree_text = text
        self.tree_text_split = text.split("\n")

        return text

    def update_tree_text(self, parent, current_row):
        """
        Update the tree text for the parent node.

        Args:
            parent (Node):
                The parent node to update.
            current_row (int):
                The row in the tree text where the parent is.
        """
        # Open the parent
        self.parse_level(parent)

        # Update the parent node to reflect that it is now open
        self.tree_text_split[current_row] = parent.to_tree_text()

        # Create the text and node list for the children ready to insert
        child_test = [child.to_tree_text() for child in parent.children]
        child_nodes_by_row = [child for child in parent.children]

        # Insert the children into the tree text and nodes by row list
        self.tree_text_split[current_row + 1 : current_row + 1] = child_test
        self.nodes_by_row[current_row + 1 : current_row + 1] = (
            child_nodes_by_row
        )

        # Update the tree text area
        self.tree_text = "\n".join(self.tree_text_split)

        return self.tree_text

    def close_node(self, node, current_row):
        """
        Close the node.

        Args:
            node (Node):
                The node to close.
            current_row (int):
                The row in the tree text where the node is.
        """
        # Close the node itself
        node.close_node()

        # Now we need to remove all the children from the tree, these have
        # already been closed recursively by the call to `close_node` above
        # so we just need to remove them from the tree text and the nodes by
        # row list

        # We can do this by removing everything between the node and the next
        # node at the same depth
        for i, n in enumerate(self.nodes_by_row[current_row + 1 :]):
            if n.depth <= node.depth:
                break
            del self.nodes_by_row[current_row + 1]
            del self.tree_text_split[current_row + 1]

        # Update the parent node to reflect that it is now closed
        self.tree_text_split[current_row] = node.to_tree_text()

        # Update the tree text area
        self.tree_text = "\n".join(self.tree_text_split)

        return self.tree_text

    def get_current_node(self, row):
        """
        Return the current node.

        This will also unhighlight the previous node, and highlight the new
        node.

        Args:
            row (int):
                The row in the tree.

        Returns:
            Node:
                The node at row.
        """
        # Unhighlight the previous node
        self.prev_node.is_under_cursor = False

        # Get the new node and highlight it
        new_node = self.nodes_by_row[row]
        new_node.is_under_cursor = True

        # New node will now be the previous node
        self.prev_node = new_node

        return new_node

    def get_all_paths(self):
        """Collect all the paths in the HDF5 file (lazy initialization)."""
        # Only start the collection once
        if self.paths_initialized:
            return

        self.paths_initialized = True
        self.index_building = True

        def run_in_thread():
            try:
                with h5py.File(self.filepath, "r") as hdf:

                    def visitor(name, obj):
                        with self.all_node_paths_lock:
                            self.all_node_paths.append(name)

                    hdf.visititems(visitor)
            finally:
                # Mark index building as complete
                self.index_building = False

        self.unpack_thread = threading.Thread(
            target=run_in_thread, daemon=True
        )
        self.unpack_thread.start()

        # We'll join this thread in the filter function (filter_tree)
        # to ensure we have all the paths before we start searching without
        # holding things up here

    def filter_tree(self, query):
        """
        Filter the tree based on a fuzzy search query.

        This method searches all paths in the HDF5 file and reconstructs
        the tree to show only matching nodes and their parents. The original
        tree state is preserved for restoration.

        Args:
            query (str):
                The search query string.

        Returns:
            str:
                The filtered tree text, or empty string if no query.
        """
        from h5forest.fuzzy import search_paths

        # If query is empty, restore original tree
        if not query:
            if self.original_tree_text is not None:
                self.restore_tree()
            return self.tree_text

        # Initialize path collection if this is the first search
        self.get_all_paths()

        # Wait briefly for the background thread (non-blocking for UI)
        # Use a short timeout so tests can complete but UI stays responsive
        if self.unpack_thread is not None and self.unpack_thread.is_alive():
            # Wait up to 100ms for the thread to finish
            # This allows fast completion in tests while keeping UI responsive
            self.unpack_thread.join(timeout=0.1)

            # If still not done after timeout, return unfiltered tree
            if self.unpack_thread.is_alive():
                return self.tree_text

        # If we haven't saved the original tree yet, do it now
        if self.original_tree_text is None:
            self._save_tree_state()

        # Search for matching paths (limit to top 100 to avoid UI freeze)
        # Use lock to safely read all_node_paths
        with self.all_node_paths_lock:
            matches = search_paths(query, self.all_node_paths, limit=100)

        # If no matches, show empty tree
        if not matches:
            self.tree_text = ""
            self.tree_text_split = []
            self.nodes_by_row = []
            self.filtered_node_rows = []
            return self.tree_text

        # Extract just the paths from matches
        matching_paths = [path for path, score in matches]

        # Build filtered tree with matches and their parents
        self._build_filtered_tree(matching_paths)

        return self.tree_text

    def _save_tree_state(self):
        """Save the current tree state for later restoration."""
        self.original_tree_text = self.tree_text
        self.original_tree_text_split = self.tree_text_split.copy()
        self.original_nodes_by_row = self.nodes_by_row.copy()

    def _get_node_search_path(self, node):
        """
        Build the search path for a node as it appears in all_node_paths.

        The path format matches how paths are stored in all_node_paths:
        - Root node: ""
        - Direct children of root: "node_name"
        - Deeper nodes: "parent/child/node_name"

        Args:
            node: The node to build the search path for.

        Returns:
            str: The search path for the node.
        """
        if node.depth == 0:
            return ""
        elif node.parent and node.parent.depth == 0:
            return node.name
        else:
            # Build full path from root
            path_parts = []
            current = node
            while current.parent is not None:
                path_parts.insert(0, current.name)
                current = current.parent
            return "/".join(path_parts)

    def _build_filtered_tree(self, matching_paths):
        """
        Build a filtered tree showing only matching nodes and their parents.

        Args:
            matching_paths (list):
                List of paths that match the search query.
        """
        # Collect all paths to include (matches + parents)
        paths_to_include = set()

        for path in matching_paths:
            # Add the matching path
            paths_to_include.add(path)

            # Add all parent paths
            parts = path.split("/")
            for i in range(1, len(parts)):
                parent_path = "/".join(parts[:i])
                if parent_path:
                    paths_to_include.add(parent_path)

        # First pass: Open all parent nodes that need to be shown
        # This ensures we can traverse their children
        self._open_nodes_in_paths(paths_to_include)

        # Rebuild the tree by traversing from root
        # and only including nodes whose paths are in paths_to_include
        filtered_text = ""
        filtered_nodes = []
        filtered_rows = []

        def _traverse_and_filter(node, row_counter):
            """Recursively traverse and filter nodes."""
            nonlocal filtered_text, filtered_nodes, filtered_rows

            # Get the search path for this node
            node_search_path = self._get_node_search_path(node)

            # Root is always included if any children match
            if node.depth == 0 or node_search_path in paths_to_include:
                # Add this node to filtered tree
                filtered_text_line = node.to_tree_text() + "\n"
                filtered_text += filtered_text_line
                filtered_nodes.append(node)

                # Track if this was a matching node (not just a parent)
                if node_search_path in matching_paths:
                    filtered_rows.append(row_counter[0])

                row_counter[0] += 1

                # Recursively include children
                for child in node.children:
                    _traverse_and_filter(child, row_counter)

        # Start traversal from root
        row_counter = [0]  # Use list to make it mutable in nested function
        _traverse_and_filter(self.root, row_counter)

        # Update tree state with filtered results
        self.tree_text = filtered_text.rstrip("\n")
        self.tree_text_split = (
            self.tree_text.split("\n") if self.tree_text else []
        )
        self.nodes_by_row = filtered_nodes
        self.filtered_node_rows = filtered_rows

    def _open_nodes_in_paths(self, paths_to_include):
        """
        Open all nodes that are in the paths_to_include set.

        This ensures that when we filter the tree, parent nodes are opened
        so their children are visible.

        Args:
            paths_to_include (set):
                Set of paths that should be included in the filtered tree.
        """

        def _recursive_open(node):
            """Recursively open nodes that need to be shown."""
            # Get the search path for this node
            node_search_path = self._get_node_search_path(node)

            # If this node is in paths to include and is a group, open it
            if node.depth == 0 or node_search_path in paths_to_include:
                if node.is_group and not node.is_expanded:
                    node.open_node()

                # Recursively process children
                for child in node.children:
                    _recursive_open(child)

        _recursive_open(self.root)

    def restore_tree(self):
        """Restore the original tree state before filtering."""
        if self.original_tree_text is not None:
            self.tree_text = self.original_tree_text
            self.tree_text_split = self.original_tree_text_split.copy()
            self.nodes_by_row = self.original_nodes_by_row.copy()

            # Clear all highlighting
            for node in self.nodes_by_row:
                node.is_highlighted = False

            # Clear saved state
            self.original_tree_text = None
            self.original_tree_text_split = None
            self.original_nodes_by_row = None
            self.filtered_node_rows = []
