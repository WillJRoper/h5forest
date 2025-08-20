"""Basic functionality tests to verify the test infrastructure works."""

import os
import tempfile
from unittest.mock import patch

import h5py
import numpy as np
import pytest


class TestBasicInfrastructure:
    """Test that the basic test infrastructure works."""

    def test_fixtures_directory_exists(self, fixtures_dir):
        """Test that fixtures directory exists."""
        assert os.path.exists(fixtures_dir)

    def test_simple_h5_file_exists(self, simple_h5_file):
        """Test that simple HDF5 file fixture exists."""
        assert os.path.exists(simple_h5_file)

        # Verify it's a valid HDF5 file
        with h5py.File(simple_h5_file, "r") as f:
            assert isinstance(f, h5py.File)

    def test_complex_h5_file_exists(self, complex_h5_file):
        """Test that complex HDF5 file fixture exists."""
        assert os.path.exists(complex_h5_file)

        with h5py.File(complex_h5_file, "r") as f:
            assert isinstance(f, h5py.File)
            # Should have nested structure
            assert len(list(f.keys())) > 0

    def test_prompt_toolkit_io_fixture(self, mock_prompt_toolkit_io):
        """Test that prompt_toolkit IO fixture works."""
        # Should be able to send text
        mock_prompt_toolkit_io.send_text("test")

        # The fixture should be available
        assert mock_prompt_toolkit_io is not None

    def test_temp_h5_file_fixture(self, temp_h5_file):
        """Test that temporary HDF5 file fixture works."""
        assert os.path.exists(temp_h5_file)

        with h5py.File(temp_h5_file, "r") as f:
            assert "test_data" in f
            assert "test_group" in f

    def test_numpy_arrays_fixture(self, sample_numpy_arrays):
        """Test that numpy arrays fixture works."""
        assert "integers" in sample_numpy_arrays
        assert "floats" in sample_numpy_arrays
        assert isinstance(sample_numpy_arrays["integers"], np.ndarray)


class TestModuleImports:
    """Test that all modules can be imported successfully."""

    def test_import_h5forest_modules(self):
        """Test that h5forest modules can be imported."""
        from h5forest import h5_forest, node, tree, utils

        assert h5_forest is not None
        assert node is not None
        assert tree is not None
        assert utils is not None

    def test_import_h5forest_classes(self):
        """Test that main classes can be imported."""
        from h5forest.h5_forest import H5Forest
        from h5forest.node import Node
        from h5forest.tree import Tree
        from h5forest.utils import DynamicTitle

        assert H5Forest is not None
        assert Node is not None
        assert Tree is not None
        assert DynamicTitle is not None


class TestBasicClassCreation:
    """Test basic class instantiation."""

    def test_dynamic_title_creation(self):
        """Test DynamicTitle can be created."""
        from h5forest.utils import DynamicTitle

        title = DynamicTitle("Test Title")
        assert title() == "Test Title"

        title.update_title("New Title")
        assert title() == "New Title"

    def test_tree_creation_with_file(self, simple_h5_file):
        """Test Tree can be created with a real HDF5 file."""
        from h5forest.tree import Tree

        tree = Tree(simple_h5_file)
        assert tree.filepath == simple_h5_file
        assert hasattr(tree, "root")
        assert hasattr(tree, "nodes_by_row")

    @patch("h5forest.h5_forest.get_window_size")
    def test_h5forest_singleton_creation(
        self, mock_get_window_size, simple_h5_file
    ):
        """Test H5Forest singleton can be created."""
        # Mock terminal size to avoid terminal dependency
        mock_get_window_size.return_value = (24, 80)

        # Import here to avoid issues with earlier imports
        from h5forest.h5_forest import H5Forest

        # Create instance (singleton) - requires file path
        forest1 = H5Forest(simple_h5_file)
        forest2 = H5Forest(simple_h5_file)

        # Should be same instance (singleton pattern)
        assert forest1 is forest2

        # Should have the tree with file path set
        assert forest1.tree.filepath == simple_h5_file

        # Reset the singleton for cleanup
        H5Forest._instance = None


class TestBasicFileOperations:
    """Test basic file operations work."""

    def test_read_simple_h5_file(self, simple_h5_file):
        """Test reading the simple HDF5 file."""
        with h5py.File(simple_h5_file, "r") as f:
            # Check basic structure exists
            assert len(list(f.keys())) > 0

            # Check attributes exist
            assert len(f.attrs.keys()) > 0

    def test_read_complex_h5_file(self, complex_h5_file):
        """Test reading the complex HDF5 file."""
        with h5py.File(complex_h5_file, "r") as f:
            # Should have nested groups
            keys = list(f.keys())
            assert len(keys) > 0

            # Check for nested structure
            found_group = False
            for key in keys:
                if isinstance(f[key], h5py.Group):
                    found_group = True
                    break
            assert found_group


class TestErrorHandling:
    """Test basic error handling."""

    def test_nonexistent_file_error(self):
        """Test error handling for nonexistent files."""
        from h5forest.tree import Tree

        with pytest.raises((FileNotFoundError, OSError)):
            Tree("nonexistent_file.h5")

    def test_invalid_h5_file_error(self):
        """Test error handling for invalid HDF5 files."""
        from h5forest.tree import Tree

        # Create a non-HDF5 file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".h5", delete=False
        ) as tmp:
            tmp.write("This is not an HDF5 file")
            tmp_path = tmp.name

        try:
            with pytest.raises((ValueError, OSError, Exception)):
                Tree(tmp_path)
        finally:
            os.unlink(tmp_path)


class TestMockingInfrastructure:
    """Test that mocking infrastructure works properly."""

    def test_mock_h5py_file_fixture(self, mock_h5py_file):
        """Test the mock h5py file fixture."""
        assert mock_h5py_file is not None
        assert hasattr(mock_h5py_file, "attrs")
        assert hasattr(mock_h5py_file, "keys")

    def test_reset_singleton_fixture(self):
        """Test that singleton reset fixture works."""
        from h5forest.h5_forest import H5Forest

        # Should start with no instance
        assert not hasattr(H5Forest, "_instance") or H5Forest._instance is None
