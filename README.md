# h5forest
[![PyPI version](https://badge.fury.io/py/h5forest.svg)](https://badge.fury.io/py/h5forest)
[![PyPI downloads](https://img.shields.io/pypi/dm/h5forest.svg)](https://pypi.org/project/h5forest/)
[![Python versions](https://img.shields.io/pypi/pyversions/h5forest.svg)](https://pypi.org/project/h5forest/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Test Suite](https://github.com/WillJRoper/h5forest/actions/workflows/test.yml/badge.svg)](https://github.com/WillJRoper/h5forest/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/WillJRoper/h5forest/branch/main/graph/badge.svg)](https://codecov.io/gh/WillJRoper/h5forest)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

HDF5 Forest (`h5forest`) is a Text-based User Interface (TUI) for exploring HDF5 files.

`h5ls` works, and `h5glance` is a great improvement, so "Why bother?" I hear you ask. 

Well, `h5forest` brings interactivity and new functionality not available in its long-standing brethren. `h5forest` includes:

- An interactive interface capable of handling large files with deep hierarchies.
- Real-time metadata and attribute displays.
- A modal system for interacting with the file (I use Neovim by the way).
- Lazy loading, making the most of chunked data.
- Peeking inside Datasets.
- Computing statistics on the fly.
- Generation of quick diagnostics.
- Fully asynchronous operation for a blazingly fast (🔥) and responsive feel.
- A fully terminal-based interface with vim motions (did I mention?...).
- Fuzzy search with real-time filtering to quickly find datasets and groups.

![SCR-20241021-belp](https://github.com/user-attachments/assets/38b92869-6768-41f4-833c-d8b4ad6c6ad5)

The following features are coming soon:
- Renaming of Datasets and Groups.

## Getting started

`h5forest` can be installed through `pip`:

```bash
pip install h5forest
```

You will now have the `h5forest` command installed. Simply run

```
h5forest /path/to/hdf5/file.hdf5
```

on the command line to get started exploring a file.

## Testimonials

"This is the most compelling and useful procrastination I've ever seen" - Frustrated collaborator waiting for actual work to be done.

"Why has no one done this before? Let’s nominate him for a peerage." - Professor incapable of peerage nomination.

"Nice" - Previous supervisor.



