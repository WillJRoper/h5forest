# Quick Start

This guide will get you up and running with h5forest in just a few minutes.

## Basic Usage

Launch h5forest with any HDF5 file:

```bash
h5forest /path/to/your/file.hdf5
```

You'll see the main interface with several panels:

- **Tree Panel** (left): Hierarchical view of your HDF5 file
- **Metadata Panel** (bottom left): Information about the selected item
- **Attributes Panel** (bottom right): Attributes of the selected item
- **Hotkeys Panel** (bottom): Available keyboard shortcuts

## Basic Navigation

### Moving Around

- Use **arrow keys** or **hjkl** (Vim-style) to navigate the tree
- **`{`** and **`}`** to jump up/down 10 lines at a time
- **Enter** to expand or collapse groups

### Viewing Data

When you select a dataset (not a group), you'll see its metadata including:

- Shape and data type
- Compression information
- Memory usage
- Number of attributes

## Your First Exploration

Let's walk through a typical workflow:

### 1. Navigate the Tree Structure

```
▼ my_simulation.h5
  ▼ PartType0
    ▶ Coordinates
    ▶ Masses
    ▶ Velocities
  ▼ PartType1
    ▶ Coordinates
    ▶ Masses
```

Use arrow keys to move between items. Groups (folders) have triangular arrows, datasets (files) don't.

### 2. Expand Groups

Press **Enter** on a group to expand it and see its contents.

### 3. Examine a Dataset

Navigate to a dataset like `Coordinates`. The metadata panel will show:

```
Dataset:            /PartType0/Coordinates
Shape:              (1000000, 3)
Datatype:           float32
Compressed Memory:  11.4 MB
Compression:        gzip
```

### 4. Enter Dataset Mode

Press **`d`** to enter Dataset Mode. Now you have additional options:

- **`v`** - View dataset values (truncated for large arrays)
- **`m`** - Get minimum and maximum values
- **`M`** - Calculate mean value
- **`s`** - Calculate standard deviation

### 5. View Values

Press **`v`** to see actual data values:

```
[[1.23 4.56 7.89]
 [2.34 5.67 8.90]
 [3.45 6.78 9.01]
 ...
 
Showing 1000/3000000 elements.
```

### 6. Generate Statistics

Press **`m`** to get min/max values. For large datasets, you'll see a progress bar as h5forest efficiently processes the data in chunks.

## Understanding Modes

h5forest uses a modal interface. The available modes are:

| Key | Mode | Purpose |
|-----|------|---------|
| **Default** | Normal Mode | Basic navigation |
| **`d`** | Dataset Mode | Data analysis |
| **`g`** | Goto Mode | Quick navigation |
| **`w`** | Window Mode | Panel management |
| **`p`** | Plotting Mode | Create scatter plots |
| **`H`** | Histogram Mode | Generate histograms |

Each mode shows different hotkeys at the bottom of the screen.

## Quick Reference

### Essential Keys

- **`q`** - Quit (works in any mode)
- **`Ctrl+Q`** - Force quit
- **Escape** - Return to Normal Mode
- **`A`** - Toggle expanded attributes panel

### Mode Switching

- **`d`** - Dataset analysis mode
- **`g`** - Goto navigation mode  
- **`w`** - Window management mode
- **`p`** - Plotting mode
- **`H`** - Histogram mode

### Dataset Mode

- **`v`** - View values
- **`V`** - View values in range (prompts for indices)
- **`m`** - Min/Max statistics
- **`M`** - Mean calculation
- **`s`** - Standard deviation

## Next Steps

Now that you've covered the basics:

- Read the [Mode Reference](modes/overview.md) for complete keyboard shortcuts
- Check out [Examples](examples/navigation.md) for more complex workflows
- See the [FAQ](faq.md) if you run into issues

## Tips for Success

!!! tip "Performance with Large Files"
    h5forest uses lazy loading and chunked processing. Large files load quickly, and statistics are computed efficiently even for massive datasets.

!!! tip "Vim Users"
    If you're familiar with Vim, you'll feel right at home with the modal interface and keyboard shortcuts.

!!! warning "Terminal Compatibility"
    For the best experience, use a modern terminal emulator with Unicode and 256-color support.