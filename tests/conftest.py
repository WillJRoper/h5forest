"""Shared pytest fixtures for h5forest tests."""

import os
import tempfile
from unittest.mock import Mock, patch

import h5py
import numpy as np
import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput


@pytest.fixture(scope="session", autouse=True)
def ensure_test_fixtures():
    """Ensure test fixture files exist before running tests."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    simple_path = os.path.join(fixtures_dir, "simple.h5")

    # Only create fixtures if they don't exist
    if not os.path.exists(simple_path):
        # Import the creation script
        import sys

        sys.path.insert(0, fixtures_dir)
        from create_fixtures import create_all_fixtures

        create_all_fixtures()
        sys.path.pop(0)

    yield


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def simple_h5_file(fixtures_dir):
    """Path to simple test HDF5 file."""
    return os.path.join(fixtures_dir, "simple.h5")


@pytest.fixture
def complex_h5_file(fixtures_dir):
    """Path to complex test HDF5 file."""
    return os.path.join(fixtures_dir, "complex.h5")


@pytest.fixture
def attributes_h5_file(fixtures_dir):
    """Path to attributes test HDF5 file."""
    return os.path.join(fixtures_dir, "attributes.h5")


@pytest.fixture
def empty_h5_file(fixtures_dir):
    """Path to empty test HDF5 file."""
    return os.path.join(fixtures_dir, "empty.h5")


@pytest.fixture
def temp_h5_file():
    """Create a temporary HDF5 file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
        filepath = tmp.name

    # Create a basic test file
    with h5py.File(filepath, "w") as f:
        f.attrs["test"] = True
        f.create_dataset("test_data", data=np.arange(10))
        group = f.create_group("test_group")
        group.create_dataset("nested_data", data=np.ones(5))

    yield filepath

    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


@pytest.fixture(autouse=True, scope="function")
def mock_prompt_toolkit_io():
    """
    Fixture to mock prompt_toolkit I/O for all tests.

    This creates a pipe input and dummy output that can be used
    to simulate user input and capture output in tests without
    requiring a real terminal.
    """
    with create_pipe_input() as pipe_input:
        with create_app_session(input=pipe_input, output=DummyOutput()):
            yield pipe_input


@pytest.fixture
def mock_h5py_file():
    """Create a mock h5py File object for unit testing."""
    mock_file = Mock()
    mock_file.attrs = {"title": "Test File"}
    mock_file.keys.return_value = ["group1", "dataset1"]

    # Mock group
    mock_group = Mock()
    mock_group.name = "/group1"
    mock_group.attrs = {"description": "Test Group"}
    mock_group.keys.return_value = ["sub_dataset"]

    # Mock dataset
    mock_dataset = Mock()
    mock_dataset.name = "/dataset1"
    mock_dataset.shape = (100, 50)
    mock_dataset.dtype = np.float64
    mock_dataset.attrs = {"units": "meters"}
    mock_dataset.value = np.random.random((100, 50))

    def mock_getitem(key):
        items = {"group1": mock_group, "dataset1": mock_dataset}
        return items.get(key)

    mock_file.__getitem__ = mock_getitem

    return mock_file


@pytest.fixture
def mock_node_parent():
    """Create a mock parent Node for testing."""
    from h5forest.node import Node

    parent = Mock(spec=Node)
    parent.name = "parent"
    parent.depth = 0
    parent.path = "/parent"
    parent.children = []
    return parent


@pytest.fixture
def sample_numpy_arrays():
    """Provide various numpy arrays for testing."""
    return {
        "integers": np.arange(10),
        "floats": np.random.random(20),
        "matrix": np.random.random((5, 10)),
        "3d_array": np.random.random((3, 4, 5)),
        "strings": np.array(["hello", "world", "test"]),
        "booleans": np.array([True, False, True, False]),
    }


@pytest.fixture(autouse=True)
def reset_h5forest_singleton():
    """Reset the H5Forest singleton instance between tests."""
    from h5forest.h5_forest import H5Forest

    # Clear any existing instance
    if hasattr(H5Forest, "_instance"):
        H5Forest._instance = None

    yield

    # Clear instance after test
    if hasattr(H5Forest, "_instance"):
        H5Forest._instance = None


@pytest.fixture
def mock_terminal_size():
    """Mock terminal size for consistent testing."""
    with patch("h5forest.utils.get_window_size", return_value=(24, 80)):
        yield


@pytest.fixture
def suppress_matplotlib():
    """Suppress matplotlib GUI during tests."""
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    yield
