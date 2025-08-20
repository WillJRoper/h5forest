"""Create sample HDF5 files for testing."""

import os

import h5py
import numpy as np


def create_simple_hdf5(filepath):
    """Create a simple HDF5 file with basic structure."""
    with h5py.File(filepath, "w") as f:
        # Root attributes
        f.attrs["title"] = "Simple Test File"
        f.attrs["version"] = "1.0"

        # Simple datasets
        f.create_dataset("integers", data=np.arange(10))
        f.create_dataset("floats", data=np.random.random(5))
        f.create_dataset("strings", data=np.array([b"hello", b"world"]))

        # Group with datasets
        group1 = f.create_group("group1")
        group1.attrs["description"] = "First test group"
        group1.create_dataset("data", data=np.random.random((10, 5)))
        group1.create_dataset("labels", data=np.array([b"a", b"b", b"c"]))


def create_complex_hdf5(filepath):
    """Create a complex HDF5 file with nested structure."""
    with h5py.File(filepath, "w") as f:
        # Root attributes
        f.attrs["title"] = "Complex Test File"
        f.attrs["created_by"] = "h5forest test suite"

        # Nested groups
        level1 = f.create_group("level1")
        level1.attrs["level"] = 1

        level2a = level1.create_group("level2a")
        level2a.create_dataset("small_data", data=np.arange(100))
        level2a.create_dataset("matrix", data=np.random.random((20, 30)))

        level2b = level1.create_group("level2b")
        level2b.attrs["empty_group"] = True

        level3 = level2a.create_group("level3")
        level3.create_dataset("deep_data", data=np.ones(50))

        # Different data types
        types_group = f.create_group("types")
        types_group.create_dataset(
            "int8", data=np.array([1, 2, 3], dtype=np.int8)
        )
        types_group.create_dataset(
            "float32", data=np.array([1.1, 2.2, 3.3], dtype=np.float32)
        )
        types_group.create_dataset("bool", data=np.array([True, False, True]))

        # Large dataset
        f.create_dataset("large_data", data=np.random.random((1000, 100)))


def create_attributes_hdf5(filepath):
    """Create HDF5 file focused on testing attributes."""
    with h5py.File(filepath, "w") as f:
        # Many root attributes
        f.attrs["string_attr"] = "test string"
        f.attrs["int_attr"] = 42
        f.attrs["float_attr"] = 3.14159
        f.attrs["array_attr"] = np.array([1, 2, 3, 4, 5])

        # Dataset with attributes
        dset = f.create_dataset("data_with_attrs", data=np.arange(20))
        dset.attrs["units"] = "meters"
        dset.attrs["scale"] = 1.5
        dset.attrs["description"] = "Sample measurement data"

        # Group with many attributes
        group = f.create_group("attrs_group")
        for i in range(10):
            group.attrs[f"attr_{i}"] = f"value_{i}"


def create_empty_hdf5(filepath):
    """Create an empty HDF5 file."""
    with h5py.File(filepath, "w") as f:
        f.attrs["empty"] = True


def create_all_fixtures():
    """Create all test fixture files."""
    fixtures_dir = os.path.dirname(__file__)

    create_simple_hdf5(os.path.join(fixtures_dir, "simple.h5"))
    create_complex_hdf5(os.path.join(fixtures_dir, "complex.h5"))
    create_attributes_hdf5(os.path.join(fixtures_dir, "attributes.h5"))
    create_empty_hdf5(os.path.join(fixtures_dir, "empty.h5"))

    print("Created all test fixtures")


if __name__ == "__main__":
    create_all_fixtures()
