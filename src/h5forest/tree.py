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

from h5forest.node import Node


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

        # Store the root level of the tree
        self.roots = []

        # Initialise a container to store nodes by row in the tree output
        self.nodes_by_row = []

        # Parse the root level
        self.parse_roots()

    def parse_roots(self):
        """Parse the root level of the HDF5 file."""
        with h5py.File(self.filepath, "r") as hdf:
            # Loop over root keys
            for key in hdf.keys():
                item = hdf[key]
                node = Node(key, item, self.filepath)
                self.roots.append(node)

    def parse_level(self, parent):
        """
        Open the parent group.

        This will populate the chidlren dict on the node which will be parsed
        later when a text representation is requested updating the tree.
        """
        # Open this group
        parent.open_node()

    def _get_tree_text_recursive(self, current_node, text, nodes_by_row):
        """
        Parse the open nodes to produce the text tree representation.

        This will recurse through the open nodes constructing the output.

        Returns:
            str:
                The text representation of the tree.
            list:
                A list containing the nodes where the index is the row
                they are on in the text representation.
        """
        # Add this nodes representation
        text += f"{current_node.to_tree_string()}\n"

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
        for root in self.roots:
            text, nodes_by_row = self._get_tree_text_recursive(
                root,
                text,
                nodes_by_row,
            )

        # Store the nodes by row
        self.nodes_by_row = nodes_by_row

        return text

    def update_tree_text(self, parent, current_row, tree_text_area):
        """Update the tree text for the parent node."""
        # Open the parent
        self.parse_level(parent)

        # Get the tree text split into lines
        tree_text = tree_text_area.text.split("\n")

        # Update the parent node to reflect that it is now open
        tree_text[current_row] = parent.to_tree_string()

        # Loop over the now populated children and insert them into the tree
        # text
        for i, child in enumerate(parent.children):
            self.nodes_by_row.insert(current_row + i + 1, child)
            tree_text.insert(current_row + i + 1, child.to_tree_string())

        # Update the tree text area
        tree_text_area.text = "\n".join(tree_text)

    def close_node(self, node, current_row, tree_text_area):
        """Close the node."""
        # Close the node itself
        node.close_node()

        # Get the tree text split into lines
        tree_text = tree_text_area.text.split("\n")

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
            del tree_text[current_row + 1]

        # Update the parent node to reflect that it is now closed
        tree_text[current_row] = node.to_tree_string()

        # Update the tree text area
        tree_text_area.text = "\n".join(tree_text)

    def get_current_node(self, row):
        """
        Return the current node.

        Args:
            row (int):
                The row in the tree.

        Returns:
            Node:
                The node at row.
        """
        return self.nodes_by_row[row]
