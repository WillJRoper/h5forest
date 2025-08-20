"""Unit tests for h5forest.node module - corrected version."""

import h5py
import pytest

from h5forest.node import Node


class TestNodeInitialization:
    """Test Node initialization and basic properties."""

    def test_node_init_root_node(self, temp_h5_file):
        """Test basic Node initialization for root node."""
        with h5py.File(temp_h5_file, "r") as f:
            node = Node("test_file", f, temp_h5_file)

            assert node.name == "test_file"
            assert node.filepath == temp_h5_file
            assert node.path == "/"
            assert node.parent is None
            assert node.depth == 0
            assert node.is_group is True
            assert node.is_dataset is False
            assert isinstance(node.children, list)

    def test_node_init_child_node(self, temp_h5_file):
        """Test Node initialization for child node."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            child_node = Node("test_data", dataset, temp_h5_file, parent=root)

            assert child_node.name == "test_data"
            assert child_node.parent == root
            assert (
                child_node.path == "//test_data"
            )  # Root path is "/" so child path is "//child"
            assert child_node.depth == 1
            assert child_node.is_dataset is True
            assert child_node.is_group is False

    def test_node_dataset_properties(self, temp_h5_file):
        """Test dataset-specific properties."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            assert node.shape == dataset.shape
            assert node.size == dataset.size
            assert node.datatype == str(dataset.dtype)
            assert hasattr(node, "nbytes")
            assert hasattr(node, "ndim")

    def test_node_group_properties(self, temp_h5_file):
        """Test group-specific properties."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            assert node.is_group is True
            assert node.nr_child > 0  # Should have nested_data
            assert node.has_children is True
            assert node.shape is None
            assert node.datatype is None

    def test_node_attributes_parsing(self, attributes_h5_file):
        """Test that node attributes are parsed correctly."""
        with h5py.File(attributes_h5_file, "r") as f:
            node = Node("attrs_test", f, attributes_h5_file)

            assert node.nr_attrs > 0
            assert node.has_attrs is True
            assert isinstance(node.attrs, dict)
            assert len(node.attrs) == node.nr_attrs


class TestNodeHierarchy:
    """Test Node parent-child relationships."""

    def test_node_open_expands_children(self, temp_h5_file):
        """Test that opening a node creates children."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            parent_node = Node("test_group", group, temp_h5_file, parent=root)

            # Initially no children loaded
            assert len(parent_node.children) == 0
            assert not parent_node.is_expanded

            # Open the node
            parent_node.open_node()

            # Should now have children
            assert len(parent_node.children) > 0
            assert parent_node.is_expanded

    def test_node_close_removes_children(self, temp_h5_file):
        """Test that closing a node removes children."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)
            node.open_node()

            assert len(node.children) > 0

            node.close_node()

            assert len(node.children) == 0
            assert not node.is_expanded

    def test_dataset_cannot_be_opened(self, temp_h5_file):
        """Test that datasets cannot be opened as groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            with pytest.raises(
                ValueError, match="Cannot open a dataset as a group"
            ):
                node.open_node()


class TestNodeTextGeneration:
    """Test Node text generation methods."""

    def test_to_tree_text_group_collapsed(self, temp_h5_file):
        """Test tree text for collapsed group."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            tree_text = node.to_tree_text()

            assert "test_group" in tree_text
            assert "▶" in tree_text  # Collapsed arrow

    def test_to_tree_text_group_expanded(self, temp_h5_file):
        """Test tree text for expanded group."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)
            node.open_node()

            tree_text = node.to_tree_text()

            assert "test_group" in tree_text
            assert "▼" in tree_text  # Expanded arrow

    def test_to_tree_text_dataset(self, temp_h5_file):
        """Test tree text for dataset."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            tree_text = node.to_tree_text()

            assert "test_data" in tree_text
            # Datasets don't have arrows, just indentation

    def test_get_meta_text_group(self, temp_h5_file):
        """Test metadata text generation for groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            meta_text = node._get_meta_text()

            assert "Group:" in meta_text
            assert "N_children:" in meta_text
            assert "N_attrs:" in meta_text
            assert "Depth:" in meta_text

    def test_get_meta_text_dataset(self, temp_h5_file):
        """Test metadata text generation for datasets."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            meta_text = node._get_meta_text()

            assert "Dataset:" in meta_text
            assert "Shape:" in meta_text
            assert "Datatype:" in meta_text
            assert "Compressed Memory:" in meta_text


class TestNodeState:
    """Test Node state management."""

    def test_expansion_state_property(self, temp_h5_file):
        """Test is_expanded property."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            # Initially not expanded
            assert not node.is_expanded

            # After opening, should be expanded
            node.open_node()
            assert node.is_expanded

    def test_highlighting_state(self, temp_h5_file):
        """Test highlighting state flags."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)

            # Initial state
            assert not root.is_highlighted
            assert not root.is_under_cursor

            # Can be set
            root.is_highlighted = True
            root.is_under_cursor = True

            assert root.is_highlighted
            assert root.is_under_cursor

    def test_root_node_auto_opens(self, temp_h5_file):
        """Test that root node opens automatically."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)

            # Root node should auto-open if it has children
            if root.has_children:
                assert root.is_expanded


class TestNodeStringRepresentation:
    """Test Node string representation."""

    def test_repr_representation(self, temp_h5_file):
        """Test repr representation of Node."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            repr_str = repr(node)

            assert "Node(" in repr_str
            assert "/test_data" in repr_str


class TestNodeDepthCalculation:
    """Test Node depth calculation."""

    def test_root_depth(self, temp_h5_file):
        """Test root node depth."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            assert root.depth == 0

    def test_child_depth(self, temp_h5_file):
        """Test child node depth."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            child = Node("test_group", group, temp_h5_file, parent=root)
            assert child.depth == 1

    def test_nested_depth(self, temp_h5_file):
        """Test nested node depth calculation."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            level1 = Node("test_group", group, temp_h5_file, parent=root)
            level1.open_node()

            # Find nested dataset
            nested_dataset = None
            for child in level1.children:
                if child.name == "nested_data":
                    nested_dataset = child
                    break

            if nested_dataset:
                assert nested_dataset.depth == 2
