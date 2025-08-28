"""Tests for Node attribute cursor tracking functionality."""

import tempfile

import h5py
import pytest

from h5forest.node import Node


class TestNodeAttributeCursorTracking:
    """Test attribute cursor tracking functionality in Node class."""

    @pytest.fixture
    def sample_hdf5_file(self):
        """Create a sample HDF5 file with attributes."""
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
            filename = f.name

        # Create test file with attributes
        with h5py.File(filename, "w") as hdf:
            group = hdf.create_group("test_group")
            group.attrs["attr1"] = "value1"
            group.attrs["attr2"] = 42
            group.attrs["attr3"] = 3.14

            dataset = hdf.create_dataset("test_dataset", data=[1, 2, 3])
            dataset.attrs["ds_attr1"] = "dataset_value"
            dataset.attrs["ds_attr2"] = 100

        yield filename

    def test_attributes_by_row_mapping_created(self, sample_hdf5_file):
        """Test that attributes_by_row mapping is created."""
        with h5py.File(sample_hdf5_file, "r") as hdf:
            group = hdf["test_group"]
            node = Node("test_group", group, sample_hdf5_file)

            # Get attribute text to trigger mapping creation
            node.get_attr_text()

            # Check that mapping was created
            assert hasattr(node, "attributes_by_row")
            assert isinstance(node.attributes_by_row, list)
            assert len(node.attributes_by_row) == 3  # 3 attributes

            # Check mapping contents
            expected_keys = ["attr1", "attr2", "attr3"]
            assert all(key in expected_keys for key in node.attributes_by_row)

    def test_get_current_attribute_valid_row(self, sample_hdf5_file):
        """Test get_current_attribute with valid row numbers."""
        with h5py.File(sample_hdf5_file, "r") as hdf:
            group = hdf["test_group"]
            node = Node("test_group", group, sample_hdf5_file)

            # Test each row
            key0, value0 = node.get_current_attribute(0)
            assert key0 == "attr1"
            assert value0 == "value1"

            key1, value1 = node.get_current_attribute(1)
            assert key1 == "attr2"
            assert value1 == 42

            key2, value2 = node.get_current_attribute(2)
            assert key2 == "attr3"
            assert value2 == 3.14

    def test_get_current_attribute_invalid_row(self, sample_hdf5_file):
        """Test get_current_attribute with invalid row numbers."""
        with h5py.File(sample_hdf5_file, "r") as hdf:
            group = hdf["test_group"]
            node = Node("test_group", group, sample_hdf5_file)

            # Test negative row
            key, value = node.get_current_attribute(-1)
            assert key is None
            assert value is None

            # Test row beyond range
            key, value = node.get_current_attribute(10)
            assert key is None
            assert value is None

    def test_get_current_attribute_dataset(self, sample_hdf5_file):
        """Test get_current_attribute works with dataset attributes."""
        with h5py.File(sample_hdf5_file, "r") as hdf:
            # Create root node first to avoid depth 0 issue
            root = Node("root", hdf, sample_hdf5_file)

            # Now create dataset node with proper parent
            dataset = hdf["test_dataset"]
            node = Node("test_dataset", dataset, sample_hdf5_file, parent=root)

            # Test dataset attributes
            key0, value0 = node.get_current_attribute(0)
            assert key0 == "ds_attr1"
            assert value0 == "dataset_value"

            key1, value1 = node.get_current_attribute(1)
            assert key1 == "ds_attr2"
            assert value1 == 100

    def test_attributes_by_row_refreshes_with_cache_clear(
        self, sample_hdf5_file
    ):
        """Test that clearing cache causes attributes_by_row to refresh."""
        with h5py.File(sample_hdf5_file, "r") as hdf:
            group = hdf["test_group"]
            node = Node("test_group", group, sample_hdf5_file)

            # Get initial attribute text
            node.get_attr_text()
            initial_mapping = node.attributes_by_row.copy()

            # Clear cache
            node._attr_text = None

            # Get attribute text again
            node.get_attr_text()
            refreshed_mapping = node.attributes_by_row

            # Mappings should be the same (since attributes didn't change)
            assert initial_mapping == refreshed_mapping

    def test_no_attributes_handling(self, sample_hdf5_file):
        """Test handling of nodes with no attributes."""
        with h5py.File(sample_hdf5_file, "a") as hdf:
            # Create group with no attributes
            empty_group = hdf.create_group("empty_group")

        with h5py.File(sample_hdf5_file, "r") as hdf:
            empty_group = hdf["empty_group"]
            node = Node("empty_group", empty_group, sample_hdf5_file)

            # Should have empty mapping
            assert node.attributes_by_row == []

            # get_current_attribute should return None for any row
            key, value = node.get_current_attribute(0)
            assert key is None
            assert value is None
