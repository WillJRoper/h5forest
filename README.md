# h5forest
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

![SCR-20241020-rprx](https://github.com/user-attachments/assets/06801c77-4e7c-49e1-b46d-36a1fae8038b)

The following features are coming soon:
- A search function.
- Renaming of Datasets and Groups.

## Getting started

To install `h5forest` simply clone this repo and run

```
pip install .
```

at the root level of the repo (PyPi install coming soon). 

You will now have the `h5forest` command installed. Simply run

```
h5forest /path/to/hdf5/file.hdf5
```

on the command line to get started exploring a file.

## Testimonials

"This is the most compelling and useful procrastination I've ever seen" - Frustrated collaborator waiting for actual work to be done.

"Why has no one done this before? Let’s nominate him for a peerage." - Professor incapable of peerage nomination.

"Nice" - Previous supervisor.



