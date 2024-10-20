# h5forest
HDF5 Forest (`h5forest`) is an interactive CLI application for exploring HDF5 files.

`h5ls` works, and `h5glance` is a great improvement on it. So "Why bother?" I hear you say. 

Well, `h5forest` brings interactivity and functionality not available in its long-standing brethren. `h5forest` includes:

- An interactive interface capable of handling files with deep hierarchies and large numbers of groups.
- Real-time metadata and attribute displays.
- The ability to display the contents of a Dataset.
- The ability to get basic statistics from a Dataset.
- The ability to quickly plot datasets against each other.

The following features will be coming soon:
- A search function.
- Renaming of Datasets and Groups.

![SCR-20240217-pnoi](https://github.com/WillJRoper/h5forest/assets/40025495/365a9a54-95ce-4642-8e60-b3c176b40201)

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



