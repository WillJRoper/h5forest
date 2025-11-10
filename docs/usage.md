# Basic Usage

This page covers the fundamental concepts and usage patterns of `h5forest`.

## Interface Overview

h5forest's interface consists of several key panels:

```
┌─────────────────┬─────────────────┐
│                 │                 │
│   Tree Panel    │  Values/Plot    │
│                 │   (optional)    │
│                 │                 │
├─────────────────┼─────────────────┤
│  Metadata       │   Attributes    │
├─────────────────┴─────────────────┤
│          Hotkeys Display          │
├───────────────────────────────────┤
│         Mini Buffer               │
└───────────────────────────────────┘
```

### Panel Descriptions

**Tree Panel**: Shows the hierarchical structure of your HDF5 file. Groups are shown with triangular arrows (▶/▼) based on whether they are open or closed, and datasets are shown without arrows.

**Metadata Panel**: Displays information about the currently selected item (group or dataset).

**Attributes Panel**: Shows HDF5 attributes associated with the selected item. Can be expanded with **`A`** to show larger lists of attributes in a broader view.

**Values/Plot Panel**: Conditionally appear when viewing dataset values or creating plots in the Dataset or Plotting modes.

**Hotkeys Display**: Shows available keyboard shortcuts for the current mode.

**Mini Buffer**: Used for messages, prompts, and user input.

## File Structure Navigation

### Understanding HDF5 Structure

HDF5 files are organized hierarchically:

- **Groups**: Like folders, can contain other groups or datasets
- **Datasets**: Actual data arrays with associated metadata
- **Attributes**: Key-value metadata attached to groups or datasets

### Tree Navigation

**Basic Movement**:

```
↑/k    Move up one line
↓/j    Move down one line
←/h    Move left
→/l    Move right
```

**Fast Movement**:

```
{      Jump up 10 lines
}      Jump down 10 lines
```

**Expansion**:

```
Enter  Expand/collapse the selected group
```

## Working with Different Data Types

### Groups

When you select a group, you'll see a variety of metadata telling you about its contents:

```
Group:              /simulation/particles
N_children:         5
N_attrs:            2
Depth:              2
```

Groups primarily serve as organizational containers.

### Datasets

Dataset metadata includes comprehensive information about the data stored at that location:

```
Dataset:            /simulation/particles/positions
Shape:              (1000000, 3)
Datatype:           float64
Compressed Memory:  22.9 MB
Compression:        gzip
Compression_opts:   9
Chunks:             (32768, 3)
```

Key information:

- **Shape**: Dimensions of the array
- **Datatype**: Data type (float64, int32, etc.)
- **Memory**: Actual storage size
- **Compression**: Compression algorithm used
- **Chunks**: How data is stored internally

## Attributes Inspection

HDF5 attributes are metadata key-value pairs. They appear in the attributes panel:

```
units: kpc
description: Particle positions in comoving coordinates
created_by: simulation_code_v2.1
```

### Expanding Attributes

Press **`A`** to toggle between normal and expanded attribute view:

- **Normal**: Attributes panel shares space with metadata
- **Expanded**: Attributes panel takes half the screen width

## Data Value Inspection

### Viewing Dataset Values

In Dataset Mode (**`d`**):

- **`v`**: View truncated dataset values
- **`V`**: View specific range (prompts for start:end indices)

For small datasets, all values are shown. For large datasets, h5forest shows a sensible subset:

```
[[1.234 5.678 9.012]
 [2.345 6.789 0.123]
 [3.456 7.890 1.234]
 ...

Showing 1000/3000000 elements.
```

### Range Viewing

Use **`V`** to view specific slices. You'll be prompted:

```
Enter range (start:end): 100:200
```

This shows elements 100 through 199.

## Statistical Analysis

h5forest can compute statistics efficiently even for very large datasets:

### Available Statistics

- **`m`**: Minimum and maximum values
- **`M`**: Mean (average) value
- **`s`**: Standard deviation

### Chunked Processing

For large datasets, statistics are computed in chunks with a progress bar:

```
Min/Max ████████████████████████████████ 100%
```

This approach:

- Prevents memory overflow
- Provides progress feedback
- Maintains accuracy

## Performance Considerations

### Lazy Loading

h5forest only loads data when needed:

- File structure loads immediately
- Dataset values load on request
- Statistics compute on demand

### Memory Management

- Tree structure uses minimal memory
- Dataset values are not cached
- Statistics use chunk-based algorithms where possible

### Responsive Interface

- All heavy operations run in background threads
- Interface remains responsive during calculations
- Progress bars show operation status
