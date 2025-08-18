# Normal Mode

Normal Mode is the default mode in h5forest. It provides basic navigation, tree manipulation, and serves as the hub for switching to other specialized modes.

## Purpose

Normal Mode is designed for:
- Navigating the HDF5 file tree structure
- Expanding and collapsing groups
- Viewing metadata and attributes
- Switching to other modes for specialized tasks

## Keyboard Reference

### Tree Navigation

| Key | Action | Description |
|-----|--------|-------------|
| **`↑`** / **`k`** | Move up | Move cursor up one line |
| **`↓`** / **`j`** | Move down | Move cursor down one line |
| **`{`** | Jump up | Move cursor up 10 lines |
| **`}`** | Jump down | Move cursor down 10 lines |
| **`Enter`** | Expand/Collapse | Toggle expansion of selected group |

### Mode Switching

| Key | Mode | Description |
|-----|------|-------------|
| **`j`** | Jump Mode | Quick navigation commands |
| **`d`** | Dataset Mode | Data analysis and statistics |
| **`w`** | Window Mode | Panel and focus management |
| **`p`** | Plotting Mode | Create scatter plots |
| **`h`** | Histogram Mode | Generate histograms |

### Interface Control

| Key | Action | Description |
|-----|--------|-------------|
| **`A`** | Toggle Attributes | Expand/shrink attributes panel |
| **`q`** | Quit | Exit application |
| **`Ctrl+Q`** | Force Quit | Force exit application |

## Tree Navigation Details

### Basic Movement

Use arrow keys or Vim-style movement:
- **`k`** / **`↑`**: Move up in the tree
- **`j`** / **`↓`**: Move down in the tree

The cursor highlights the current item, and the metadata/attributes panels update automatically.

### Fast Movement

For large files with many items:
- **`{`**: Jump up 10 lines at once
- **`}`**: Jump down 10 lines at once

This is especially useful when navigating files with hundreds or thousands of datasets.

### Group Expansion

Press **`Enter`** on any group to:
- **Expand** if currently collapsed (▶ becomes ▼)
- **Collapse** if currently expanded (▼ becomes ▶)

!!! tip "Lazy Loading"
    Groups are loaded on-demand when first expanded, making large files load quickly.

## Interface Customization

### Attributes Panel

Press **`A`** to toggle between two attribute panel layouts:

**Normal Layout**: Attributes panel shares bottom space with metadata
```
┌─────────────┬─────────────┐
│    Tree     │   Values    │
├─────────────┼─────────────┤
│  Metadata   │ Attributes  │
└─────────────┴─────────────┘
```

**Expanded Layout**: Attributes panel takes half the screen width
```
┌─────────────┬─────────────┐
│    Tree     │ Attributes  │
├─────────────┤             │
│  Metadata   │             │
└─────────────┴─────────────┘
```

Use expanded layout when examining files with many or complex attributes.

## Real-time Updates

As you navigate in Normal Mode, several panels update automatically:

### Metadata Panel
Shows information about the selected item:
- **Groups**: Number of children, attributes, and depth
- **Datasets**: Shape, data type, compression, memory usage

### Attributes Panel  
Displays HDF5 attributes as key-value pairs:
```
units: meters
description: Particle positions
created: 2024-01-15
```

## Efficient Workflows

### Quick Exploration
1. Use **`{`** and **`}`** to quickly scan through large sections
2. Expand interesting groups with **`Enter`**
3. Check metadata for datasets of interest
4. Switch to Dataset Mode (**`d`**) for detailed analysis

### Structure Mapping
1. Start at the root level
2. Systematically expand major groups
3. Note the overall organization
4. Use **`A`** to examine important attributes

### Focused Navigation
1. Use standard movement (**`j`**/**`k`**) for precise control
2. Expand only relevant groups
3. Switch to Jump Mode (**`j`**) for quick repositioning

## Common Patterns

### Dataset Discovery
```
1. Navigate to promising group
2. Press Enter to expand
3. Look for datasets with interesting metadata
4. Press 'd' to enter Dataset Mode
5. Analyze the data
```

### File Structure Documentation
```
1. Start at root
2. Expand all major groups
3. Note hierarchical organization
4. Check group attributes for documentation
5. Map out key datasets and their purposes
```

## Visual Indicators

### Tree Symbols
- **`▶`**: Collapsed group (has children)
- **`▼`**: Expanded group (showing children)
- **No symbol**: Dataset or empty group

### Highlighting
- **Current item**: Highlighted with cursor
- **Tree structure**: Indentation shows hierarchy
- **Item types**: Groups and datasets visually distinguished

## Tips for Efficiency

!!! tip "Keyboard Focus"
    Normal Mode keeps focus on the tree panel. All navigation commands work immediately without clicking.

!!! tip "Memory Efficient"
    Only expanded groups load their children. This keeps memory usage low even for massive files.

!!! warning "Large Files"
    In very large files, avoid expanding everything at once. Navigate selectively to maintain performance.

## Next Steps

From Normal Mode, you can efficiently switch to specialized modes:

- Press **`d`** for [Dataset Mode](dataset.md) to analyze data
- Press **`j`** for [Jump Mode](jump.md) for quick navigation
- Press **`w`** for [Window Mode](window.md) to manage panels
- Press **`p`** for [Plotting Mode](plotting.md) to create visualizations
- Press **`h`** for [Histogram Mode](histogram.md) for statistical plots

Each specialized mode provides focused tools while preserving your current position in the tree.