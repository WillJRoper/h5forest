# `H5forest`

**A Text-based User Interface (TUI) for exploring HDF5 files**

`h5forest` brings interactivity and new functionality to HDF5 file exploration. Unlike traditional command-line tools like `h5ls` or `h5glance`, `h5forest` provides a fully interactive terminal interface for navigating complex HDF5 file hierarchies.

![h5forest Screenshot](https://github.com/user-attachments/assets/38b92869-6768-41f4-833c-d8b4ad6c6ad5)

## Features

- **Interactive Interface**: Handle large files with deep hierarchies through an intuitive TUI
- **Real-time Displays**: Live metadata and attribute views that update as you navigate
- **Modal System**: Vim-like modal interface for different interaction modes
- **Lazy Loading**: Efficient handling of large datasets with chunked data support
- **Dataset Inspection**: Peek inside datasets with automatic truncation for large arrays
- **Statistical Analysis**: Compute statistics (min/max, mean, standard deviation) on the fly
- **Data Visualization**: Generate quick scatter plots and histograms
- **Asynchronous Operations**: Responsive interface that doesn't block during heavy computations

## Quick Start

Install `h5forest` via pip:

```bash
pip install h5forest
```

Then explore any HDF5 file:

```bash
h5forest /path/to/your/file.hdf5
```

## Navigation Overview

h5forest uses a modal interface with different modes for different tasks:

- **Normal Mode**: Default navigation and tree exploration
- **Search Mode**: Fuzzy search to quickly find datasets and groups
- **Jump Mode**: Quick navigation commands
- **Dataset Mode**: Data analysis and statistics
- **Window Mode**: Panel and focus management
- **Plotting Mode**: Create scatter plots from data
- **Histogram Mode**: Generate histograms and distributions

Use keyboard shortcuts to switch between modes and perform actions. Press `q` to exit any mode or the application.

## Documentation Sections

- **[Getting Started](installation.md)**: Installation and basic setup
- **[Quick Start](quickstart.md)**: Get up and running in minutes
- **[Mode Reference](modes/overview.md)**: Detailed guide to all interaction modes
- **[Contributing](contributing.md)**: Development setup and contribution guidelines
- **[FAQ](faq.md)**: Common questions and troubleshooting

## Why `h5forest`?

Traditional HDF5 tools work well for quick inspections, but `h5forest` excels when you need to:

- Explore complex, deeply nested file structures
- Interactively analyze datasets without writing scripts
- Generate quick visualizations during data exploration
- Navigate large files efficiently with lazy loading
- Perform statistical analysis on datasets of any size

## Community

`h5forest` is developed by [Will Roper](https://github.com/WillJRoper).

**Get Involved:**

- **Contribute:** See our [Contributing Guide](contributing.md) for development setup and guidelines
- **Report Issues:** Submit bug reports and feature requests on [GitHub Issues](https://github.com/WillJRoper/h5forest/issues)
- **Discussions:** Join conversations on [GitHub Discussions](https://github.com/WillJRoper/h5forest/discussions)
- **Source Code:** Fork and star the project on [GitHub](https://github.com/WillJRoper/h5forest)

## License

`h5forest` is released under the GPL v3 License. See the [LICENSE](https://github.com/WillJRoper/h5forest/blob/main/LICENSE) file for details.
