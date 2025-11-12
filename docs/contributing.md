# Contributing to `h5forest`

We welcome contributions to `h5forest`! This guide will help you get started with contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- HDF5 libraries (for `h5py`)
- pre-commit hook installation (see below)

### Installation

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/yourusername/h5forest.git
   cd h5forest
   ```

2. **Install in development mode:**

   ```bash
   pip install -e ".[dev,test]"
   ```

   This installs `h5forest` along with development dependencies:
   - `ruff` - Code linting and formatting
   - `pytest` - Testing framework
   - Additional testing utilities

3. **Install documentation tools (optional):**

   ```bash
   pip install -e ".[docs]"
   ```

   This enables local documentation building with:
   - `mkdocs` - Documentation site generator
   - `mkdocs-material` - Material theme for MkDocs
   - Related plugins and extensions

4. **Install pre-commit hooks:**

   ```bash
   pip install pre-commit
   pre-commit install
   ```

   Pre-commit hooks automatically enforce our code quality standards. Pull requests that don't pass these checks will be rejected by our CI workflows.

   The hooks perform the following checks:
   - **Ruff linting and formatting** - Ensures code style consistency (PEP 8, 79 char lines, etc.)
   - **Merge conflict detection** - Prevents accidental merge conflict markers
   - **Large file prevention** - Stops large files from being added
   - **Case conflict checks** - Avoids filename case issues across operating systems

   Once installed, these checks run automatically on staged files before every commit, catching issues early and saving time in the review process.

   You can also run them manually:

   ```bash
   # Run on all files
   pre-commit run --all-files

   # Run on specific files
   pre-commit run --files path/to/file.py
   ```

5. **Verify installation:**

   ```bash
   # Run tests
   pytest

   # Check linting
   ruff check .

   # Try the application
   h5forest tests/fixtures/simple.h5
   ```

## Development Workflow

### Before Making Changes

1. **Create a new branch:**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

### Making Changes

1. **Make your changes** following the coding standards below

2. **Add tests** for new functionality (see [Testing Guide](testing.md))

3. **Run tests and linting:**

   ```bash
   # Run all tests
   pytest

   # Check code formatting
   ruff check .
   ruff format .

   # Fix auto-fixable issues
   ruff check --fix .
   ```

4. **Test your changes manually:**
   ```bash
   h5forest path/to/test/file.h5
   ```

### Submitting Changes

1. **Commit your changes:**

   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

2. **Push to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub

## Coding Standards

### Code Style

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and linting. All code must pass ruff checks before being merged.

**Formatting Rules:**

- **Line length:** Maximum 79 characters (PEP 8 compliant)
- **Indentation:** 4 spaces (no tabs)
- **Quote style:** Double quotes for strings (single quotes for dictionary keys when appropriate)
- **Blank lines:** Two blank lines between top-level definitions, one between methods
- **Trailing whitespace:** Not allowed
- **Import sorting:** Organized alphabetically with isort rules

**Import Organization:**

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import h5py
import numpy as np
from prompt_toolkit import Application

# Local application imports
from h5forest.node import Node
from h5forest.tree import Tree
```

**Naming Conventions:**

- **Classes:** `PascalCase` (e.g., `TreeProcessor`, `DatasetNode`)
- **Functions/Methods:** `snake_case` (e.g., `process_data`, `get_metadata`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_DISPLAY_ITEMS`, `DEFAULT_CHUNK_SIZE`)
- **Private members:** Prefix with single underscore (e.g., `_internal_method`)
- **Variables:** `snake_case` (e.g., `file_path`, `node_count`)

### Code Quality

- **Type hints:** Strongly encouraged for function signatures and class attributes
- **Docstrings:** Required for all public functions, classes, and modules
- **Comments:** Use sparingly; prefer self-documenting code. When needed, explain _why_, not _what_
- **Error handling:** Handle errors gracefully with informative messages
- **DRY principle:** Don't Repeat Yourself - extract common logic into reusable functions
- **SOLID principles:** Follow object-oriented design principles where applicable

### Example Code Style

```python
class ExampleClass:
    """A well-documented example class.

    This class demonstrates the coding standards used in `h5forest`.

    Attributes:
        name (str): The name of the example.
        value (int): An example integer value.
    """

    def __init__(self, name: str, value: int = 0):
        """Initialize the example class.

        Args:
            name: The name for this example.
            value: Initial value (defaults to 0).
        """
        self.name = name
        self.value = value

    def process_data(self, data: list) -> list:
        """Process the input data.

        Args:
            data: List of items to process.

        Returns:
            Processed list with modifications applied.

        Raises:
            ValueError: If data is empty or invalid.
        """
        if not data:
            raise ValueError("Data cannot be empty")

        return [item * 2 for item in data if isinstance(item, (int, float))]
```

## Testing Requirements

All contributions must include appropriate tests. See the [Testing Guide](testing.md) for details.

### Test Coverage

- **New features:** Must include comprehensive tests
- **Bug fixes:** Must include regression tests
- **Refactoring:** Existing tests must pass

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/h5forest --cov-report=term-missing

# Run specific tests
pytest tests/unit/test_node.py
```

## Documentation

### Docstring Style

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Brief description of the function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        Description of the return value.

    Raises:
        ValueError: Description of when this error is raised.

    Example:
        >>> example_function("test", 5)
        True
    """
```

### Documentation Updates

- Update relevant documentation when changing functionality
- Add new documentation for new features
- Keep examples up to date

### Building Documentation Locally

To build and preview the documentation:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve documentation locally with live reload
mkdocs serve
```

Then visit `http://localhost:8000` in your browser to view the documentation.

The documentation will automatically rebuild as you make changes to the markdown files.

## Review Process

### Pull Request Requirements

Before submitting a PR, ensure:

- [ ] All tests pass (`pytest`)
- [ ] Code passes linting (`ruff check .`)
- [ ] Code is properly formatted (`ruff format .`)
- [ ] New functionality includes tests
- [ ] Documentation is updated if needed
- [ ] Commit messages are descriptive

### Review Criteria

PRs are reviewed for:

- **Functionality:** Does it work as intended?
- **Code quality:** Is it well-written and maintainable?
- **Testing:** Are there adequate tests?
- **Documentation:** Is it properly documented?
- **Performance:** Does it introduce performance regressions?
- **Compatibility:** Does it maintain backward compatibility?

### Continuous Integration

All PRs automatically run through CI which checks:

- Tests against Python 3.9, 3.10, 3.11, 3.12, 3.13
- Cross-platform testing on Ubuntu, Windows, and macOS
- Code linting and formatting
- Test coverage reporting
- Documentation building (if applicable)

## Adding New Key Bindings

The key binding system in `h5forest` is centralized in the `H5KeyBindings` class located in `src/h5forest/bindings/bindings.py`. This section explains how to add new key bindings to the application.

### Architecture Overview

The binding system consists of:

- **`H5KeyBindings` class** (`src/h5forest/bindings/bindings.py`): Central class that manages all key bindings
- **Function modules** (`src/h5forest/bindings/*_funcs.py`): Contain the actual handler functions for each mode
  - `normal_funcs.py` - Mode switching and core operations
  - `tree_funcs.py` - Tree navigation operations
  - `dataset_funcs.py` - Dataset inspection operations
  - `hist_funcs.py` - Histogram mode operations
  - `plot_funcs.py` - Scatter plot mode operations
  - `jump_funcs.py` - Jump/goto operations
  - `search_funcs.py` - Search operations
  - `window_funcs.py` - Window focus management
  - `utils.py` - Utility functions

### Steps to Add a New Binding

#### 1. Create the Handler Function

Add your handler function to the appropriate `*_funcs.py` file. All handlers should:

- Accept an `event` parameter
- Use the `@error_handler` decorator
- Get the app instance via the singleton: `app = H5Forest()`

**Example:**

```python
@error_handler
def my_new_function(event):
    """Brief description of what this function does."""
    # Avoid circular imports
    from h5forest.h5_forest import H5Forest

    # Access the application instance
    app = H5Forest()

    # Your logic here
    app.print("My new function executed!")
```

#### 2. Import the Handler in `bindings.py`

Add your function to the imports at the top of `src/h5forest/bindings/bindings.py`:

```python
from h5forest.bindings.your_funcs import (
    my_new_function,
    # ... other functions
)
```

#### 3. Add the Key Configuration

In the `H5KeyBindings.__init__()` method, add a key configuration attribute:

```python
self.my_new_key = self.config.get_keymap(
    "your_mode",  # e.g., "hist_mode", "plot_mode", "normal_mode"
    "your_action",  # e.g., "my_action"
)
```

#### 4. Create a Filter (if needed)

If your binding should only work in certain conditions, add a filter lambda in `__init__()`:

```python
self.filter_my_condition = lambda: app.some_condition
```

Common filters:
- `self.filter_normal_mode` - Only in normal mode
- `self.filter_hist_mode` - Only in histogram mode
- `self.filter_tree_focus` - Only when tree has focus
- `self.filter_not_normal_mode` - In any leader mode

#### 5. Create a Label

Add a label for the hotkey display:

```python
self.my_action_label = Label(
    translate_key_label(self.my_new_key) + ": Description"
)
```

#### 6. Bind the Function

In the appropriate `_init_*_bindings()` method, bind your function:

```python
def _init_your_mode_bindings(self):
    """Initialize your mode keybindings."""
    self.bind_function(
        self.my_new_key,
        my_new_function,
        self.filter_your_mode,  # Or lambda: True for always active
    )
```

#### 7. Update Hotkey Display

In the `get_current_hotkeys()` method, add your label to the appropriate mode section:

```python
if self.filter_your_mode():
    hotkeys.append(self.my_action_label)
```

#### 8. Add Configuration Defaults

Update `src/h5forest/data/default_config.yaml` to include the default key mapping:

```yaml
keymaps:
  your_mode:
    your_action: "k"  # Or whatever key you want
```

#### 9. Write Tests

Add tests in `tests/unit/test_your_mode_bindings.py`:

```python
@patch('h5forest.h5_forest.H5Forest')
def test_my_new_function(self, mock_h5forest_class, mock_app, mock_event):
    """Test my new function."""
    mock_h5forest_class.return_value = mock_app

    _init_your_mode_bindings(mock_app)

    # Find the binding
    bindings = [b for b in mock_app.kb.bindings if b.keys == ("k",)]
    handler = bindings[0].handler

    # Call the handler
    handler(mock_event)

    # Assert expected behavior
    mock_app.print.assert_called_once_with("My new function executed!")
```

### Example: Adding a "Copy Value" Binding to Histogram Mode

**1. Create handler in `hist_funcs.py`:**

```python
@error_handler
def copy_hist_value(event):
    """Copy the current histogram bin value to clipboard."""
    from h5forest.h5_forest import H5Forest
    app = H5Forest()

    # Get current bin value logic here
    value = app.histogram_plotter.get_current_bin_value()
    # Copy to clipboard logic
    subprocess.run(["xclip", "-selection", "clipboard"],
                   input=str(value).encode())
    app.print(f"Copied value: {value}")
```

**2. Import in `bindings.py`:**

```python
from h5forest.bindings.hist_funcs import (
    ...,
    copy_hist_value,
)
```

**3-7. Add configuration, filter, label, binding, and hotkey display** (as shown above)

**8. Update `default_config.yaml`:**

```yaml
keymaps:
  hist_mode:
    copy_value: "c"
```

**9. Write tests** (as shown above)

### Testing Your Binding

1. Run unit tests: `pytest tests/unit/test_your_mode_bindings.py`
2. Test manually: Start `h5forest` and try your new key binding
3. Check pre-commit hooks: `pre-commit run --all-files`

## Getting Help

### Communication Channels

- **GitHub Issues:** For bugs, feature requests, and questions
- **GitHub Discussions:** For general questions and community chat
- **Documentation:** Check the docs first for answers

Thank you for contributing to `h5forest`! Your efforts help make HDF5 data exploration better for everyone.
