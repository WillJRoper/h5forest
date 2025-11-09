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


class TestNodeMemorySizeFormatting:
    """Test memory size formatting in get_meta_text."""

    def test_meta_text_bytes_format(self, tmp_path):
        """Test memory size in bytes (< 1000 B)."""
        filepath = tmp_path / "test_bytes.h5"
        with h5py.File(filepath, "w") as f:
            # Create tiny dataset (< 1000 bytes)
            f.create_dataset("tiny", data=np.arange(10, dtype=np.uint8))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["tiny"]
            node = Node("tiny", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert " B\n" in meta_text

    def test_meta_text_kilobytes_format(self, tmp_path):
        """Test memory size in KB (1000 <= size < 10^6)."""
        filepath = tmp_path / "test_kb.h5"
        with h5py.File(filepath, "w") as f:
            # Create dataset around 5 KB
            f.create_dataset("medium", data=np.arange(1500, dtype=np.float32))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["medium"]
            node = Node("medium", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert " KB\n" in meta_text

    def test_meta_text_megabytes_format(self, tmp_path):
        """Test memory size in MB (10^6 <= size < 10^9)."""
        filepath = tmp_path / "test_mb.h5"
        with h5py.File(filepath, "w") as f:
            # Create dataset around 2 MB
            f.create_dataset("large", data=np.arange(500000, dtype=np.float32))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["large"]
            node = Node("large", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert " MB\n" in meta_text

    def test_meta_text_gigabytes_format(self, tmp_path):
        """Test memory size in GB (>= 10^9)."""
        filepath = tmp_path / "test_gb.h5"
        with h5py.File(filepath, "w") as f:
            # Create dataset > 1 GB
            f.create_dataset(
                "huge",
                shape=(300000000,),
                dtype=np.float32,
                compression="gzip",
            )

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["huge"]
            node = Node("huge", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert " GB\n" in meta_text


class TestNodeChunksAndFillvalue:
    """Test chunks and fillvalue display in metadata."""

    def test_meta_text_chunks_displayed(self, tmp_path):
        """Test that chunks are shown when chunks != shape."""
        filepath = tmp_path / "test_chunks.h5"
        with h5py.File(filepath, "w") as f:
            # Create chunked dataset where chunks != shape
            f.create_dataset(
                "chunked",
                shape=(1000,),
                chunks=(100,),
                dtype=np.float32,
            )

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["chunked"]
            node = Node("chunked", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert "Chunks:" in meta_text

    def test_meta_text_fillvalue_displayed(self, tmp_path):
        """Test that fillvalue is shown when present."""
        filepath = tmp_path / "test_fillvalue.h5"
        with h5py.File(filepath, "w") as f:
            # Create dataset with fillvalue
            f.create_dataset(
                "with_fill",
                shape=(100,),
                dtype=np.float32,
                fillvalue=-999.0,
            )

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["with_fill"]
            node = Node("with_fill", dataset, str(filepath), parent=root)

            meta_text = node.get_meta_text()
            assert "Fillvalue:" in meta_text


class TestNodeGroupOperations:
    """Test operations on group nodes."""

    def test_get_value_text_on_group(self, temp_h5_file):
        """Test that get_value_text returns empty string for groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            value_text = node.get_value_text()
            assert value_text == ""

    def test_get_min_max_on_group(self, temp_h5_file):
        """Test that get_min_max returns (None, None) for groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            result = node.get_min_max()
            assert result == (None, None)

    def test_get_mean_on_group(self, temp_h5_file):
        """Test that get_mean returns (None, None) for groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            result = node.get_mean()
            assert result == (None, None)

    def test_get_std_on_group(self, temp_h5_file):
        """Test that get_std returns (None, None) for groups."""
        with h5py.File(temp_h5_file, "r") as f:
            root = Node("test_file", f, temp_h5_file)
            group = f["test_group"]

            node = Node("test_group", group, temp_h5_file, parent=root)

            result = node.get_std()
            assert result == (None, None)


class TestNodeNonChunkedStatistics:
    """Test statistics on non-chunked datasets."""

    @patch("h5forest.node.ProgressBar")
    def test_min_max_non_chunked(self, mock_progress_bar, tmp_path):
        """Test get_min_max on non-chunked dataset."""
        filepath = tmp_path / "test_nonchunked.h5"
        with h5py.File(filepath, "w") as f:
            # Create non-chunked dataset (chunks == shape)
            data = np.array([1, 5, 3, 9, 2, 7])
            f.create_dataset("nonchunked", data=data, chunks=(6,))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["nonchunked"]
            node = Node("nonchunked", dataset, str(filepath), parent=root)

            vmin, vmax = node.get_min_max()
            assert vmin == 1
            assert vmax == 9

    @patch("h5forest.node.ProgressBar")
    def test_mean_non_chunked(self, mock_progress_bar, tmp_path):
        """Test get_mean on non-chunked dataset."""
        filepath = tmp_path / "test_nonchunked.h5"
        with h5py.File(filepath, "w") as f:
            # Create non-chunked dataset (chunks == shape)
            data = np.array([2.0, 4.0, 6.0, 8.0])
            f.create_dataset("nonchunked", data=data, chunks=(4,))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["nonchunked"]
            node = Node("nonchunked", dataset, str(filepath), parent=root)

            mean = node.get_mean()
            assert mean == 5.0

    @patch("h5forest.node.ProgressBar")
    def test_std_non_chunked(self, mock_progress_bar, tmp_path):
        """Test get_std on non-chunked dataset."""
        filepath = tmp_path / "test_nonchunked.h5"
        with h5py.File(filepath, "w") as f:
            # Create non-chunked dataset (chunks == shape)
            data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            f.create_dataset("nonchunked", data=data, chunks=(5,))

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["nonchunked"]
            node = Node("nonchunked", dataset, str(filepath), parent=root)

            std = node.get_std()
            assert std > 0  # Should have some standard deviation
            # Verify it's close to numpy's std
            expected_std = np.array([1.0, 2.0, 3.0, 4.0, 5.0]).std()
            assert abs(std - expected_std) < 0.01


class TestNodeLargeDatasetTruncation:
    """Test value display truncation for large datasets."""

    def test_large_dataset_truncated_display(self, tmp_path):
        """Test that large datasets are truncated in value display."""
        filepath = tmp_path / "test_large.h5"
        with h5py.File(filepath, "w") as f:
            # Create dataset larger than 1000 elements
            f.create_dataset(
                "large_data", data=np.arange(5000, dtype=np.float32)
            )

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["large_data"]
            node = Node("large_data", dataset, str(filepath), parent=root)

            value_text = node.get_value_text()

            # Should contain truncation message
            assert "Showing" in value_text
            assert "/5000 elements" in value_text

    def test_large_multidim_dataset_truncated(self, tmp_path):
        """Test truncation for multi-dimensional large datasets."""
        filepath = tmp_path / "test_large_multidim.h5"
        with h5py.File(filepath, "w") as f:
            # Create large multi-dimensional dataset
            f.create_dataset(
                "large_multidim",
                data=np.arange(10000).reshape(100, 100),
                dtype=np.float32,
            )

        with h5py.File(filepath, "r") as f:
            root = Node("test", f, str(filepath))
            dataset = f["large_multidim"]
            node = Node("large_multidim", dataset, str(filepath), parent=root)

            value_text = node.get_value_text()

            # Should contain truncation message
            assert "Showing" in value_text
            assert "elements" in value_text
