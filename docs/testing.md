# Testing Guide

`h5forest` includes a comprehensive test suite to ensure code quality and prevent regressions. This guide covers how to run tests, understand the test structure, and contribute new tests.

## Quick Start

```bash
# Install test dependencies
pip install -e ".[dev,test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src/h5forest --cov-report=term-missing
```

## Test Structure

The test suite is organized into several categories:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data files
│   ├── create_fixtures.py   # Script to generate HDF5 test files
│   ├── simple.h5           # Basic HDF5 file structure
│   ├── complex.h5          # Multi-level groups and datasets
│   ├── attributes.h5       # File with extensive attributes
│   └── empty.h5            # Empty HDF5 file
└── unit/                   # Unit tests for individual components
    ├── test_node.py        # Node class functionality
    ├── test_tree.py        # Tree class and TreeProcessor
    ├── test_utils.py       # Utility functions
    └── test_basic_functionality.py  # Infrastructure tests
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_node.py

# Run specific test class
pytest tests/unit/test_node.py::TestNodeInitialization

# Run specific test method
pytest tests/unit/test_node.py::TestNodeInitialization::test_node_init_root_node

# Run tests matching pattern
pytest -k "test_tree"
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov=src/h5forest --cov-report=term-missing

# HTML coverage report
pytest --cov=src/h5forest --cov-report=html
# Open htmlcov/index.html in browser

# XML coverage report (for CI)
pytest --cov=src/h5forest --cov-report=xml
```

### Filtering Tests

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first
pytest --ff

# Stop after first failure
pytest -x

# Show local variables in tracebacks
pytest -l
```

## Contributing Tests

We aim to have 100% test coverage (though getting to exactly 100% is not always feasible). When contributing new features or bug fixes, please include appropriate tests and make sure the coverage is not decreased.

### Writing New Tests

When adding new functionality, include tests that cover:

1. **Happy path scenarios** - Normal usage patterns
2. **Edge cases** - Boundary conditions and unusual inputs
3. **Error handling** - Invalid inputs and error conditions
4. **Integration points** - How components work together

### Test Naming Convention

```python
class TestComponentName:
    """Test cases for ComponentName class."""

    def test_method_does_expected_behavior(self):
        """Test that method performs expected behavior under normal conditions."""

    def test_method_handles_edge_case(self):
        """Test that method handles edge case appropriately."""

    def test_method_raises_error_on_invalid_input(self):
        """Test that method raises appropriate error for invalid input."""
```

### Using Fixtures

```python
def test_node_with_fixture(self, temp_h5_file):
    """Test using the temp_h5_file fixture."""
    with h5py.File(temp_h5_file, 'r') as f:
        node = Node("test", f, temp_h5_file)
        assert node.name == "test"

def test_with_mock_io(self, mock_prompt_toolkit_io):
    """Test that requires mocked prompt_toolkit I/O."""
    # Test TUI components safely
    pass
```

### Adding Test Fixtures

To add new HDF5 test files:

1. Create the file in `tests/fixtures/`
2. Add creation logic to `create_fixtures.py`
3. Add fixture function to `conftest.py`
4. Document the fixture purpose

Example:

```python
# In conftest.py
@pytest.fixture
def my_test_file():
    """Fixture providing path to specialized test file."""
    return os.path.join(FIXTURES_DIR, "my_test.h5")
```

## Continuous Integration

Tests run automatically on:

- Pull requests to `main` or `develop` branches
- Direct pushes to `main` or `develop` branches

The CI workflow:

- Tests against Python 3.8, 3.9, 3.10, 3.11, 3.12
- Runs linting checks with ruff
- Executes full test suite
- Generates coverage reports
- Must pass for PR approval

## Best Practices

1. **Test behavior, not implementation** - Focus on what the code does, not how
2. **Use descriptive test names** - Make intent clear from the name
3. **Keep tests independent** - Each test should run in isolation
4. **Use appropriate assertions** - Choose the most specific assertion available
5. **Mock external dependencies** - Don't rely on external systems
6. **Test edge cases** - Cover boundary conditions and error paths
7. **Keep tests simple** - One concept per test
8. **Use fixtures for setup** - Avoid repetitive test setup code
