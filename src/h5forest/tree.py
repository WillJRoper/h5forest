"""Tree class for the HDF5 file viewer.

This module contains the Tree class which is used to represent the HDF5 file
as a tree structure. The Tree contains Nodes which are used to represent the
groups and datasets in the HDF5 file. Each Node is lazy loaded, meaning that
its children are only loaded when it is opened.

Example usage:
    tree = Tree("example.h5")
    print(tree.get_tree_text())
"""

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
        self.filename = (
            filepath.split("/")[-1].replace(".h5", "").replace(".hdf5", "")
        )

        # Initialise a container to store nodes by row in the tree output
        self.nodes_by_row = []

        # Intialise containers to hold the tree text and split version
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

        This will populate the chidlren dict on the node which will be parsed
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
