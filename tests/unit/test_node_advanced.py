"""Advanced tests for h5forest.node module covering missing functionality."""

from unittest.mock import patch

import h5py
import numpy as np

from h5forest.node import Node


class TestNodeValueOperations:
    """Test Node value and statistical operations."""

    def test_get_value_text_simple(self, temp_h5_file):
        """Test getting value text from a dataset."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            value_text = node.get_value_text()

            assert isinstance(value_text, str)
            assert len(value_text) > 0

    def test_get_value_text_with_range(self, temp_h5_file):
        """Test getting value text with start and end indices."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            value_text = node.get_value_text(start_index=0, end_index=5)

            assert isinstance(value_text, str)
            assert len(value_text) > 0

    @patch("h5forest.node.ProgressBar")
    def test_get_min_max(self, mock_progress_bar, temp_h5_file):
        """Test getting min/max values from numeric dataset."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            result = node.get_min_max()

            # For datasets, should return (min, max)
            if node.is_dataset:
                vmin, vmax = result
                assert isinstance(vmin, (int, float, np.number))
                assert isinstance(vmax, (int, float, np.number))
                assert vmin <= vmax
            else:
                # For groups, returns (None, None)
                assert result == (None, None)

    @patch("h5forest.node.ProgressBar")
    def test_get_mean(self, mock_progress_bar, temp_h5_file):
        """Test getting mean value from numeric dataset."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            result = node.get_mean()

            # For datasets, should return mean value
            if node.is_dataset:
                assert isinstance(result, (int, float, np.number))
            else:
                # For groups, returns (None, None)
                assert result == (None, None)

    @patch("h5forest.node.ProgressBar")
    def test_get_std(self, mock_progress_bar, temp_h5_file):
        """Test getting standard deviation from numeric dataset."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            result = node.get_std()

            # For datasets, should return std value
            if node.is_dataset:
                assert isinstance(result, (int, float, np.number))
                assert result >= 0  # Standard deviation is always non-negative
            else:
                # For groups, returns (None, None)
                assert result == (None, None)


class TestNodeTextOperations:
    """Test Node text generation operations."""

    def test_get_attr_text_with_attributes(self, attributes_h5_file):
        """Test getting attribute text from node with attributes."""
        with h5py.File(attributes_h5_file, "r") as f:
            node = Node("attrs_test", f, attributes_h5_file)

            attr_text = node.get_attr_text()

            assert isinstance(attr_text, str)
            if node.has_attrs:
                assert len(attr_text) > 0

    def test_get_attr_text_no_attributes(self, temp_h5_file):
        """Test getting attribute text from node without attributes."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            attr_text = node.get_attr_text()

            assert isinstance(attr_text, str)
            # May be empty if no attributes

    def test_get_meta_text_public(self, temp_h5_file):
        """Test the public get_meta_text method."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)

            meta_text = root.get_meta_text()

            assert isinstance(meta_text, str)
            assert len(meta_text) > 0
            assert "Group:" in meta_text


class TestNodeErrorHandling:
    """Test Node error handling and edge cases."""

    def test_node_with_empty_group(self, empty_h5_file):
        """Test Node with empty HDF5 file."""
        with h5py.File(empty_h5_file, "r") as f:
            node = Node("empty_file", f, empty_h5_file)

            assert node.is_group
            assert node.nr_child == 0
            assert not node.has_children

    def test_node_path_construction_deep(self, temp_h5_file):
        """Test path construction for deeply nested nodes."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            level1 = Node("test_group", group, temp_h5_file, parent=root)
            level1.open_node()

            # Find nested child
            for child in level1.children:
                if child.name == "nested_data":
                    assert child.depth == 2
                    assert "nested_data" in child.path
                    break


class TestNodeProperties:
    """Test various Node properties and attributes."""

    def test_node_size_properties(self, temp_h5_file):
        """Test Node size-related properties."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            assert hasattr(node, "size")
            assert hasattr(node, "nbytes")
            assert hasattr(node, "ndim")
            assert node.size > 0
            assert node.nbytes > 0
            assert node.ndim >= 0

    def test_node_compression_info(self, temp_h5_file):
        """Test Node compression information."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            dataset = f["test_data"]

            node = Node("test_data", dataset, temp_h5_file, parent=root)

            # Check that compression properties can be accessed
            meta_text = node.get_meta_text()
            assert "Compressed Memory:" in meta_text


class TestNodeStateMutations:
    """Test Node state changes and mutations."""

    def test_node_highlighting_states(self, temp_h5_file):
        """Test various highlighting state combinations."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)

            # Test all combinations
            root.is_highlighted = False
            root.is_under_cursor = False
            assert not root.is_highlighted and not root.is_under_cursor

            root.is_highlighted = True
            root.is_under_cursor = False
            assert root.is_highlighted and not root.is_under_cursor

            root.is_highlighted = False
            root.is_under_cursor = True
            assert not root.is_highlighted and root.is_under_cursor

            root.is_highlighted = True
            root.is_under_cursor = True
            assert root.is_highlighted and root.is_under_cursor

    def test_node_expansion_cycle(self, temp_h5_file):
        """Test multiple open/close cycles."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            # Multiple cycles
            for _ in range(3):
                assert not node.is_expanded
                node.open_node()
                assert node.is_expanded
                assert len(node.children) > 0

                node.close_node()
                assert not node.is_expanded
                assert len(node.children) == 0
