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

from h5forest.progress import ProgressBar


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
        is_chunked (bool):
            Whether a dataset is chunked, None for a Group.
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
            self.path = f"{parent.path}/{self.name}"

        else:
            self.path = "/"

        # For the print path we don't want to treat the root as a /
        if parent is not None:
            self.print_path = f"{parent.print_path}/{self.name}"
        else:
            self.print_path = f"/{self.name}"

        # Set up a container to hold the child nodes
        self.children = []

        # Store the parent node
        self.parent = parent

        # Compute the depth of the tree here
        self.depth = len(self.print_path.split("/")) - 2

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
            self.size = obj.size
            self.datatype = str(obj.dtype)
            self.compression = obj.compression
            self.compression_opts = obj.compression_opts
            self.chunks = obj.chunks if obj.chunks is not None else obj.shape
            self.is_chunked = obj.chunks != obj.shape
            self.n_chunks = (
                1
                if not self.is_chunked
                else (
                    int(np.ceil(s / c))
                    for s, c in zip(self.shape, self.chunks)
                )
            )
            self.fillvalue = obj.fillvalue
            self.nbytes = obj.nbytes
            self.ndim = obj.ndim
        else:
            self.shape = None
            self.size = None
            self.datatype = None
            self.compression = None
            self.compression_opts = None
            self.chunks = None
            self.is_chunked = None
            self.fillvalue = None
            self.nbytes = None
            self.ndim = None

        # Construct tree_text, attribute and metadata text to avoid computation
        self._attr_text = None
        self._meta_text = None

        # Define a flags for syntax highlighting
        self.is_under_cursor = False
        self.is_highlighted = False

        # Start with the root node open
        if self.depth == 0:
            self.open_node()

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
            out = f"{'    ' * self.depth}  {self.name}"

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
            text = f"Group:              {self.print_path}\n"
        else:
            text = f"Dataset:            {self.print_path}\n"

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
            if self.chunks != self.shape:
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

    def get_value_text(self, start_index=None, end_index=None):
        """
        Return the value text for the node (optionally in a range).

        If this node is a Group then an empty string is returned and showing
        the value frame won't be triggered. Note that this should be handled
        outside but is included for safety.

        When no range is specified this method will try to limit to a sensible
        output size if necessary. If the Dataset is small enough we can
        just read everything and display it. If the dataset is too large
        we will only show a truncated view (first 100 elements or what will
        fit in the TextArea).

        When a range is stated that range of values will be read in and
        displayed.

        Returns:
            str:
                The value text for the node.
        """
        if self.is_group:
            return ""
        else:
            with h5py.File(self.filepath, "r") as hdf:
                dataset = hdf[self.path]

                # How many values roughly can we show maximally?
                max_count = 1000

                # If a range has been given follow that
                if start_index is not None:
                    data_subset = dataset[start_index:end_index]
                    truncated = (
                        f"\n\nShowing {len(data_subset)}/"
                        f"{dataset.size} elements ({start_index}-{end_index})."
                    )

                # If the dataset is small enough we can just read everything
                elif dataset.size < max_count:
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

                # Combine path and data for output
                return str(data_subset) + truncated

    def get_min_max(self):
        """
        Return the minimum and maximum values of the dataset.

        This will return the global minimum and maximum values of the dataset.

        If the dataset is chunked we will use them to limit the memory load
        and read in the data in manageable chunks and compute the
        minimum and maximum values on the fly.

        Returns:
            tuple:
                The minimum and maximum values of the dataset.
        """
        if self.is_group:
            return None, None
        else:
            with h5py.File(self.filepath, "r") as hdf:
                dataset = hdf[self.path]

                # If chunks and shape are equal just get the min and max
                if not self.is_chunked:
                    arr = dataset[:]
                    return arr.min(), arr.max()

                # OK, we have chunks, lets use them to avoid loading too
                # much. behaviours
                # based on dimensions

                # For 1D arrays we can just loop getting the min and max.
                # Define the initial min and max
                min_val = np.inf
                max_val = -np.inf

                # Loop over all possible chunks
                with ProgressBar(total=self.size, description="Min/Max") as pb:
                    for chunk_index in np.ndindex(*self.n_chunks):
                        # Get the current slice for each dimension
                        slices = tuple(
                            slice(
                                c_idx * c_size,
                                min((c_idx + 1) * c_size, s),
                            )
                            for c_idx, c_size, s in zip(
                                chunk_index, self.chunks, self.shape
                            )
                        )

                        # Read the chunk data
                        chunk_data = dataset[slices]

                        # Get the minimum and maximum
                        min_val = np.min((min_val, np.min(chunk_data)))
                        max_val = np.max((max_val, np.max(chunk_data)))

                        pb.advance(step=chunk_data.size)

                return min_val, max_val

    def get_mean(self):
        """
        Return the mean of the dataset values.

        This will calculate the global mean of the dataset, ignoring any axes.

        If the dataset is chunked we will use them to limit the memory load
        and read in the data in manageable chunks and compute the mean value
        on the fly.

        Returns:
            float:
                The mean of the dataset values.
        """
        if self.is_group:
            return None, None
        else:
            with h5py.File(self.filepath, "r") as hdf:
                dataset = hdf[self.path]

                # If chunks and shape are equal just get the min and max
                if not self.is_chunked:
                    arr = dataset[:]
                    return arr.mean()

                # OK, we have chunks, lets use them to make sure we don't load
                # too much into memory. Now we need to have slightly
                # different behaviours based on dimensions

                # Define initial sum
                val_sum = 0

                # Loop over all possible chunks
                with ProgressBar(total=self.size, description="Mean") as pb:
                    for chunk_index in np.ndindex(*self.n_chunks):
                        # Get the current slice for each dimension
                        slices = tuple(
                            slice(
                                c_idx * c_size,
                                min((c_idx + 1) * c_size, s),
                            )
                            for c_idx, c_size, s in zip(
                                chunk_index, self.chunks, self.shape
                            )
                        )

                        # Read the chunk data
                        chunk_data = dataset[slices]

                        # Get the sum
                        val_sum += np.sum(
                            chunk_data,
                        )

                        pb.advance(step=chunk_data.size)

                # Return the mean
                return val_sum / (self.size)

    def get_std(self):
        """
        Return the standard deviation of the dataset values.

        This will calculate the global standard deviation of the dataset,
        ignoring any axes.

        If the dataset is chunked we will use them to limit the memory load
        and read in the data in manageable chunks and compute the standard
        deviation on the fly.

        Returns:
            float:
                The standard deviation of the dataset values.
        """
        if self.is_group:
            return None, None
        else:
            with h5py.File(self.filepath, "r") as hdf:
                dataset = hdf[self.path]

                # If chunks and shape are equal just get the min and max
                if not self.is_chunked:
                    arr = dataset[:]
                    return arr.std()

                # OK, we have chunks, lets use them to make sure we don't load
                # too much into memory.

                # Define initial sum
                val_sum = 0
                spu_val_sum = 0

                # Loop over all possible chunks
                with ProgressBar(total=self.size, description="StDev") as pb:
                    for chunk_index in np.ndindex(*self.n_chunks):
                        # Get the current slice for each dimension
                        slices = tuple(
                            slice(
                                c_idx * c_size,
                                min((c_idx + 1) * c_size, s),
                            )
                            for c_idx, c_size, s in zip(
                                chunk_index, self.chunks, self.shape
                            )
                        )

                        # Read the chunk data
                        chunk_data = dataset[slices]

                        # Get the sum and sum of squares
                        val_sum += np.sum(chunk_data)
                        spu_val_sum += np.sum(chunk_data**2)

                        pb.advance(step=chunk_data.size)

                # Return the standard deviation
                return np.sqrt(
                    (spu_val_sum / self.size) - (val_sum / self.size) ** 2
                )
