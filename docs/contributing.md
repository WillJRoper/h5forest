# Contributing to h5forest

We welcome contributions to h5forest! This guide will help you get started with contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- HDF5 libraries (for h5py)

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

3. **Verify installation:**
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

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and linting:

- **Line length:** 79 characters
- **Import sorting:** Alphabetical with isort rules
- **Quote style:** Double quotes for strings
- **Indentation:** 4 spaces (no tabs)

### Code Quality

- **Type hints:** Encouraged but not required
- **Docstrings:** Required for public functions and classes
- **Comments:** Use sparingly, prefer self-documenting code
- **Error handling:** Handle errors gracefully with informative messages

### Example Code Style

```python
class ExampleClass:
    """A well-documented example class.
    
    This class demonstrates the coding standards used in h5forest.
    
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

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- **Description:** What you expected vs. what happened
- **Reproduction steps:** How to reproduce the issue
- **Environment:** Python version, OS, h5forest version
- **Sample file:** If possible, a minimal HDF5 file that triggers the bug

### Feature Requests

When suggesting features, please include:

- **Use case:** Why is this feature needed?
- **Description:** What should the feature do?
- **Examples:** How would users interact with it?
- **Implementation ideas:** Any thoughts on how to implement it

### Code Contributions

We welcome contributions in these areas:

#### Core Functionality
- **Navigation improvements:** Better tree traversal, search functionality
- **Performance optimizations:** Faster loading, memory efficiency
- **HDF5 support:** Better support for different HDF5 features

#### User Interface
- **Keybinding enhancements:** More intuitive key mappings
- **Display improvements:** Better formatting, colors, layout
- **Accessibility features:** Screen reader support, keyboard navigation

#### Data Analysis
- **Visualization features:** More plot types, interactive plots
- **Statistical functions:** Data summaries, analysis tools
- **Export capabilities:** Save data, export visualizations

#### Developer Experience
- **Testing infrastructure:** More test coverage, test utilities
- **Documentation:** Tutorials, examples, API docs
- **Development tools:** Better debugging, profiling tools

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

- Tests against Python 3.8, 3.9, 3.10, 3.11, 3.12
- Code linting and formatting
- Test coverage reporting
- Documentation building (if applicable)

## Getting Help

### Communication Channels

- **GitHub Issues:** For bugs, feature requests, and questions
- **GitHub Discussions:** For general questions and community chat
- **Documentation:** Check the docs first for answers

### Development Questions

If you have questions about:

- **Architecture:** Check `CLAUDE.md` in the repository root
- **Testing:** See the [Testing Guide](testing.md)
- **Specific implementations:** Look at existing code for patterns

## Recognition

Contributors are recognized through:

- **GitHub contributors graph:** Automatic recognition for commits
- **Release notes:** Major contributions mentioned in releases
- **Documentation:** Contributors listed in project documentation

Thank you for contributing to h5forest! Your efforts help make HDF5 data exploration better for everyone.