# Mode Overview

h5forest uses a modal interface system inspired by Vim, where different keyboard shortcuts are active depending on the current mode. This design allows for efficient, context-specific interactions with your HDF5 files.

## Modal Interface Concept

The interface has six primary modes:

1. **Normal Mode** - Default navigation and basic operations
2. **Goto Mode** - Quick navigation commands
3. **Dataset Mode** - Data analysis and statistics
4. **Window Mode** - Panel and focus management
5. **Plotting Mode** - Scatter plot creation
6. **Histogram Mode** - Histogram generation

## Mode Switching

### Entering Modes

From Normal Mode, press the following keys to enter other modes:

| Key | Mode | Purpose |
|-----|------|---------|
| **`g`** | Goto Mode | Quick navigation |
| **`d`** | Dataset Mode | Data analysis |
| **`w`** | Window Mode | Window management |
| **`p`** | Plotting Mode | Create scatter plots |
| **`H`** | Histogram Mode | Generate histograms |

### Exiting Modes

- **`q`** - Exit current mode and return to Normal Mode
- **`Escape`** - Return to Normal Mode (context-dependent)
- **`Ctrl+Q`** - Force exit the entire application

## Mode Indicators

The current mode is indicated by:

1. **Hotkey Display**: The bottom panel shows mode-specific keyboard shortcuts
2. **Context**: Available actions change based on the mode
3. **Focus**: Some modes change which panel has input focus

## Universal Commands

These commands work in all modes:

| Key | Action |
|-----|--------|
| **`Ctrl+Q`** | Force quit application |
| **Arrow Keys** | Navigate (when applicable) |

## Mode-Specific Features

### Normal Mode
- Tree navigation and expansion
- Basic file exploration
- Mode switching hub

### Goto Mode
- Fast tree navigation
- Go to specific locations
- Search functionality

### Dataset Mode  
- Value inspection
- Statistical analysis
- Data validation

### Window Mode
- Panel focus management
- Interface customization

### Plotting Mode
- Axis selection for scatter plots
- Plot configuration
- Data visualization

### Histogram Mode
- Distribution analysis
- Statistical visualization
- Configuration options

## Workflow Integration

The modal system supports natural workflows:

### Exploration Workflow
```
Normal Mode → Navigate tree
     ↓
Dataset Mode → Analyze data
     ↓  
Plotting Mode → Visualize relationships
```

### Analysis Workflow
```
Normal Mode → Find datasets
     ↓
Dataset Mode → Check statistics
     ↓
Jump Mode → Navigate to related data
     ↓
Dataset Mode → Compare values
```

## Context-Sensitive Help

Each mode displays relevant keyboard shortcuts in the hotkey panel at the bottom of the screen. This provides just-in-time help without cluttering the interface.

## Best Practices

### Efficient Mode Usage

1. **Stay in Normal Mode** for general navigation
2. **Enter Dataset Mode** when you need to analyze data
3. **Use Jump Mode** for quick navigation in large files
4. **Switch to Window Mode** to adjust panel focus
5. **Use Plotting/Histogram Modes** for visualization

### Keyboard Efficiency

- Learn the mode-switching keys (**`j`**, **`d`**, **`w`**, **`p`**, **`h`**)
- Use **`q`** to quickly exit modes
- Watch the hotkey display for available actions
- Practice common workflows to build muscle memory

## Advanced Features

### Mode State Persistence

Some modes remember your settings:
- Plotting mode retains axis selections
- Histogram mode keeps configuration options
- Window mode remembers panel preferences

### Contextual Availability

Some mode features are only available when relevant:
- Dataset-specific actions require a dataset to be selected
- Plotting requires numeric datasets
- Statistics calculations adapt to data types

## Next Steps

Explore the detailed documentation for each mode:

- [Normal Mode](normal.md) - Basic navigation and control
- [Jump Mode](jump.md) - Quick navigation features  
- [Dataset Mode](dataset.md) - Data analysis tools
- [Window Mode](window.md) - Interface management
- [Plotting Mode](plotting.md) - Scatter plot creation
- [Histogram Mode](histogram.md) - Distribution analysis

Each mode page includes comprehensive keyboard reference tables and usage examples.