# Installation

## Requirements

`h5forest` requires Python 3.8 or higher and works on Linux, macOS, and Windows.

## Install from PyPI

The easiest way to install `h5forest` is via pip:

```bash
pip install h5forest
```

This will install `h5forest` and all required dependencies:

- `h5py` - HDF5 file reading
- `numpy` - Numerical operations
- `prompt_toolkit` - Terminal user interface framework
- `matplotlib` - Plotting functionality
- `rapidfuzz` - Fuzzy searching

## Install from Source

To install the latest development version:

```bash
git clone https://github.com/WillJRoper/h5forest.git
cd h5forest
pip install -e .
```

For development installation with testing tools and documentation building, see the [Contributing Guide](contributing.md).

## Verify Installation

After installation, verify everything works:

```bash
h5forest --help
```

You should see the help message. If you have an HDF5 file available, test the interface:

```bash
h5forest /path/to/your/file.hdf5
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'h5py'**

```bash
pip install h5py
```

**Permission errors on Linux/macOS**

```bash
pip install --user h5forest
```

**Terminal display issues**

- Ensure your terminal supports Unicode characters
- For best experience, use a terminal with 256 color support
- Some features may not work properly in very old terminal emulators

### Getting Help

If you encounter issues:

1. Check the [FAQ](faq.md) for common solutions
2. Search existing [GitHub issues](https://github.com/WillJRoper/h5forest/issues)
3. Create a new issue with your system details and error message

## Next Steps

Once installed, continue to the [Quick Start Guide](quickstart.md) to learn the basics of using h5forest.
