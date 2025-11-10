# Contributing to h5forest

Thank you for your interest in contributing to h5forest! We welcome contributions of all kinds, from bug reports and feature requests to code improvements and documentation updates.

## Quick Start

1. **Fork and clone** the repository
2. **Install in development mode:**
   ```bash
   pip install -e ".[dev,test]"
   ```
3. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```
   Pre-commit hooks automatically enforce our code style. Pull requests that don't pass our style checks will be rejected by the CI workflows.
4. **Make your changes** following our coding standards
5. **Run tests** to ensure everything works:
   ```bash
   pytest
   ruff check .
   ```
6. **Submit a pull request**

## Coding Standards

- **Code style:** We use [ruff](https://docs.astral.sh/ruff/) for formatting and linting
- **Line length:** Maximum 79 characters (PEP 8)
- **Type hints:** Strongly encouraged for function signatures
- **Docstrings:** Required for all public functions and classes (Google style)
- **Tests:** All new features must include tests

## Development Workflow

Before submitting a pull request:

- [ ] All tests pass (`pytest`)
- [ ] Code passes linting (`ruff check .`)
- [ ] Code is properly formatted (`ruff format .`)
- [ ] New functionality includes tests
- [ ] Documentation is updated if needed

## Full Documentation

For comprehensive contributing guidelines, including:
- Detailed development setup
- Code style examples
- Testing requirements
- Documentation building
- Pull request process

**Read the full [Contributing Guide](https://willjroper.github.io/h5forest/contributing/)** in our documentation.

## Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/WillJRoper/h5forest/discussions)
- **Bug reports?** Create an [Issue](https://github.com/WillJRoper/h5forest/issues)
- **Feature requests?** Also create an [Issue](https://github.com/WillJRoper/h5forest/issues)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster a welcoming and inclusive community.

---

We appreciate your contributions to making h5forest better!
