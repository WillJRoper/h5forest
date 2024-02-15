"""This module contains the Node class for the HDF5 file viewer.

The Node class is used to represent a Group/Dataset in the HDF5 file. Nodes
can be linked via parent/child relationships to form a tree structure
representing the HDF5 file. A Node is lazy loaded, i.e. it only opens the
HDF5 file when it is expanded. This allows for fast loading of the tree
structure and only opening the HDF5 file when necessary.

Example usage:
    node = Node("group", group, "file.h5")
    print(node)
    print(node.open_node())
    print(node.get_attr_text())
    print(node.get_value_text())
    print(node.is_expanded)

"""
import h5py
import numpy as np

from h5forest.utils import get_window_size


class Node:
    """
    A class to represent a node in the HDF5 file.

    This class is used to represent a Group/Dataset in the HDF5 file. Nodes
    can be linked via parent/child relationships to form a tree structure
    representing the HDF5 file. A Node is lazy loaded, i.e. it only opens the
    HDF5 file when it is expanded. This allows for fast loading of the tree
    structure and only opening the HDF5 file when necessary.

    Attributes:
        name (str):
            The name of the node.
        filepath (str):
            The filepath of the HDF5 file.
        path (str):
            The full path of the node.
        children (list):
            A list of the child nodes.
        parent (Node):
            The parent node.
        depth (int):
            The depth of the node in the tree.
        obj_type (type):
            The type of the object.
        is_group (bool):
            Whether the node is a group.
        is_dataset (bool):
            Whether the node is a dataset.
        nr_child (int):
            The number of children the node has.
        has_children (bool):
            Whether the node has children.
        nr_attrs (int):
            The number of attributes the node has.
        has_attrs (bool):
            Whether the node has attributes.
        attrs (dict):
            A dictionary of the attributes.
        shape (tuple):
            The shape of a dataset, None for a Group.
        datatype (str):
            The datatype of a dataset, None for a Group.
        compression (str):
            The compression type of a dataset, None for a Group.
        compression_opts (int):
            The compression options of a dataset, None for a Group.
        chunks (tuple):
            The chunk shape of a dataset, None for a Group.
        fillvalue (int):
            The fillvalue of a dataset, None for a Group.
        nbytes (int):
            The number of bytes the dataset uses, None for a Group.
        _attr_text (str):
            The attribute text for the node.
        _meta_text (str):
            The metadata text for the node.
    """

    def __init__(self, name, obj, filepath, parent=None):
        """
        Initialise the Node.

        Args:
            name (str):
                The name (key) of the node.
            obj (h5py.Group/h5py.Dataset):
                The object the node represents.
            filepath (str):
                The filepath of the HDF5 file.
            parent (Node, optional):
                The parent node. Defaults to None.
        """
        # Store the name of the node
        self.name = name

        # Store the filepath
        self.filepath = filepath

        # Store the full path of the node
        if parent is not None:
            self.path = f"{parent.path}/{name}"

        else:
            self.path = name

        # Set up a container to hold the child nodes
        self.children = []

        # Store the parent node
        self.parent = parent

        # Compute the depth of the tree here
        self.depth = len(self.path.split("/")) - 1

        # Store the type of the obj
        self.obj_type = type(obj)

        # Store whether the node is a group or dataset
        if isinstance(obj, h5py.Group):
            self.is_group = True
            self.is_dataset = False
        else:
            self.is_group = False
            self.is_dataset = True

        # Does this node have children?
        if self.is_group:
            self.nr_child = len(obj.keys())
            self.has_children = bool(self.nr_child > 0)
        else:
            self.nr_child = 0
            self.has_children = False

        # Does this node have attributes?
        self.nr_attrs = len(obj.attrs.keys())
        self.has_attrs = bool(self.nr_attrs > 0)
        self.attrs = {key: obj.attrs[key] for key in obj.attrs.keys()}

        # For a dataset we can get a bunch of metadata to display
        if self.is_dataset:
            self.shape = obj.shape
            self.datatype = str(obj.dtype)
            self.compression = obj.compression
            self.compression_opts = obj.compression_opts
            self.chunks = obj.chunks
            self.fillvalue = obj.fillvalue
            self.nbytes = obj.nbytes
        else:
            self.shape = None
            self.datatype = None
            self.compression = None
            self.compression_opts = None
            self.chunks = None
            self.fillvalue = None
            self.nbytes = None

        # Construct tree_text, attribute and metadata text to avoid computation
        self._attr_text = None
        self._meta_text = None

    @property
    def is_expanded(self):
        """
        Return whether the node expanded.

        This is a property that returns whether the node is expanded. A node
        is expanded if it has children and all of its children are expanded.

        Returns:
            bool:
                True if the children have been loaded (i.e. noded is
                expanded).
        """
        return len(self.children) > 0

    def __repr__(self):
        """
        Return a string representation of the node.

        Returns:
            str:
                A string representation of the node.
        """
        return f"Node({self.path})"

    def to_tree_text(self):
        """
        Return a string representing the node for inclusion in the tree.

        This will return a one line string with the correct indentation and
        arrow representing the node in the tree.

        Returns:
            str:
                A string representing the node for inclusion in the tree text.
        """
        # Create the tree text
        if self.has_children:
            out = (
                f"{'    ' * self.depth}"
                f"{'▼' if self.is_expanded else '▶'} {self.name}"
            )
        else:
            out = f"{'    ' * self.depth} {self.name}"

        return out

    def open_node(self):
        """Open the node of the HDF5 file."""
        if self.is_dataset:
            raise ValueError("Cannot open a dataset as a group.")

        with h5py.File(self.filepath, "r") as hdf:
            if self.nr_child > 0:
                for key in hdf[self.path].keys():
                    child = hdf[f"{self.path}/{key}"]
                    self.children.append(
                        Node(key, child, self.filepath, parent=self)
                    )

    def close_node(self):
        """Close the node of the HDF5 file."""
        # Close all children
        for child in self.children:
            child.close_node()
        self.children = []

    def _get_meta_text(self):
        """
        Return the metadata text for the node.

        Returns:
            str:
                The metadata text for the node.
        """
        if self.is_group:
            text = f"Group:              {self.path}\n"
        else:
            text = f"Dataset:            {self.path}\n"

        # For a group there isn't much to display
        if self.is_group:
            text += f"N_children:         {self.nr_child}\n"
            text += f"N_attrs:            {self.nr_attrs}\n"
            text += f"Depth:              {self.depth}\n"
        else:
            # For a dataset we can get a bunch of metadata to display
            text += f"Shape:              {self.shape}\n"
            text += f"Datatype:           {self.datatype}\n"
            if self.nbytes < 1000:
                text += f"Compressed Memory:  {self.nbytes} B\n"
            elif self.nbytes < 10**6:
                text += f"Compressed Memory:  {self.nbytes / 1000} KB\n"
            elif self.nbytes < 10**9:
                text += f"Compressed Memory:  {self.nbytes / 10**6} MB\n"
            else:
                text += f"Compressed Memory:  {self.nbytes / 10**9} GB\n"
            text += f"Compression:        {self.compression}\n"
            text += f"Compression_opts:   {self.compression_opts}\n"
            if self.chunks is not None:
                text += f"Chunks:             {self.chunks}\n"
            if self.fillvalue is not None:
                text += f"Fillvalue:          {self.fillvalue}\n"
        return text

    def get_meta_text(self):
        """
        Return the text containing the metadata.

        The first time this is called the private variable will be populated.

        Returns:
            str:
                The metadata text for the node (stored in a private attribute).
        """
        # Construct the metadata text if it hasn't been done already
        if self._meta_text is None:
            self._meta_text = self._get_meta_text()
        return self._meta_text

    def _get_attr_text(self):
        """
        Return the attribute text for the node.

        Returns:
            str:
                The attribute text for the node.
        """
        text = ""
        for key, value in self.attrs.items():
            text += f"{key}: {value}\n"
        return text

    def get_attr_text(self):
        """
        Return the text containing the attributes.

        The first time this is called the private variable will be populated.

        Returns:
            str:
                The attribute text for the node (stored in a private
                attribute).
        """
        # Construct the attribute text if it hasn't already been done
        if self._attr_text is None:
            self._attr_text = self._get_attr_text()
        return self._attr_text

    def get_value_text(self):
        """
        Return the value text for the node.

        If this node is a Group then an empty string is returned and showing
        the value frame won't be triggered.

        If the Dataset is small enough we can just read everything and display
        it. If the dataset is too large we will only show a truncated view
        (first 100 elements or what will fit in the TextArea).

        Returns:
            str:
                The value text for the node.
        """
        if self.is_group:
            return ""
        else:
            with h5py.File(self.filepath, "r") as hdf:
                dataset = hdf[self.path]
                rows, columns = get_window_size()

                # Account for the other 2 frames we will have open
                columns //= 3

                # Subtract rows for the header and footer
                rows //= 5

                # How many values roughly can we show maximally?
                max_count = min(100, columns * rows)

                # If the dataset is small enough we can just read everything
                if dataset.size < max_count:
                    data_subset = dataset[...]
                    truncated = ""

                else:
                    # Divide the max count by the number of dimensions
                    dim_count = max_count // dataset.ndim

                    # Work out how many elements we can read and display
                    slices = []
                    for dim in dataset.shape:
                        slices.append(slice(0, dim_count))

                    data_subset = dataset[tuple(slices)]

                    # Flag in the header we are only showing a truncated view
                    truncated = (
                        f"\n\nShowing {max_count}/{dataset.size} elements."
                    )

                # Format data for display
                formatted_data = np.array2string(
                    data_subset,
                    threshold=np.inf,
                    edgeitems=3,
                    max_line_width=columns - 4,
                    precision=3,
                    suppress_small=True,
                    separator=", ",
                )

                # Combine path and data for output
                return formatted_data + truncated
