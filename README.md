# HDF5orest
HDF5 Forest (`h5forest`) is an interactive CLI application for exploring HDF5 files interactively.

`h5ls` works, and `h5glance` is a great improvement on it. So "why bother?" I hear you say. 

Well, `h5forest` brings interactivity and functionality not available in its long standing brethren. `h5forest` includes:

- An interactive interface capable of handling files with deep hierarchies and large numbers of groups.
- Real time metadata and attribute displays.
- The ability to display the contents of Datasets. (For Large datasets only a small sample of the values are read in to avoid flooding memory.)
- The ability to quick plot datasets against each other [WIP].
- Renaming of Datasets and Groups [WIP].
- An emacs plugin to probe HDF5 natively in emacs [WIP].

![SCR-20240214-sfaa](https://github.com/WillJRoper/HDF5orest/assets/40025495/711ccd02-a3c0-479f-831a-9f26018ad708)

## Getting started

To install `h5forest` simply clone this repo and run

```
pip install .
```

at the root level.

You will now have the `h5forest` command. Simply run

```
h5forest /path/to/hdf5/file.hdf5
```

to get started exploring a file.

