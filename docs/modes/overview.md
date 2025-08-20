# Mode Overview

h5forest uses a modal interface system inspired by Vim (yes, we know, everyone either loves it or thinks it's an elaborate prank from the 1970s). Different keyboard shortcuts are active depending on the current mode, because apparently regular menus weren't cool enough.

## Available Modes

1. **Normal Mode** - Default navigation and basic operations
2. **Goto Mode** - Quick navigation commands
3. **Dataset Mode** - Data analysis and statistics
4. **Window Mode** - Panel and focus management
5. **Plotting Mode** - Scatter plot creation
6. **Histogram Mode** - Histogram generation
7. **Edit Mode** - Rename groups and datasets

## Mode Switching

### Entering Modes

From Normal Mode, press the following keys to enter other modes:

| Key     | Mode           | Purpose                    |
| ------- | -------------- | -------------------------- |
| **`g`** | Goto Mode      | Quick navigation           |
| **`d`** | Dataset Mode   | Data analysis              |
| **`w`** | Window Mode    | Window management          |
| **`p`** | Plotting Mode  | Create scatter plots       |
| **`H`** | Histogram Mode | Generate histograms        |
| **`e`** | Edit Mode      | Rename groups and datasets |

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

| Key            | Action                     |
| -------------- | -------------------------- |
| **`Ctrl+Q`**   | Force quit application     |
| **Arrow Keys** | Navigate (when applicable) |

## Mode Summary

| Mode          | Key       | Purpose       | Main Features                    |
| ------------- | --------- | ------------- | -------------------------------- |
| **Normal**    | (default) | Navigation    | Tree traversal, file exploration |
| **Goto**      | `g`       | Quick nav     | Fast tree navigation, search     |
| **Dataset**   | `d`       | Data analysis | Value inspection, statistics     |
| **Window**    | `w`       | UI control    | Panel focus, layout              |
| **Plotting**  | `p`       | Visualization | Scatter plots                    |
| **Histogram** | `H`       | Distribution  | Statistical plots                |

## Next Steps

Explore the detailed documentation for each mode:

- [Normal Mode](normal.md) - Basic navigation and control
- [Goto Mode](jump.md) - Quick navigation features
- [Dataset Mode](dataset.md) - Data analysis tools
- [Window Mode](window.md) - Interface management
- [Plotting Mode](plotting.md) - Scatter plot creation
- [Histogram Mode](histogram.md) - Distribution analysis
- [Edit Mode](edit.md) - Rename groups and datasets

Each mode page includes comprehensive keyboard reference tables and usage examples.
