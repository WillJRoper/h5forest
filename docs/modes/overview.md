# Mode Overview

h5forest uses a modal interface system inspired by Vim (I use Neovim by the way), where different keyboard shortcuts become active depending on the current mode. This design enables efficient keyboard-driven navigation and powerful context-specific commands without cluttering the interface.

## Available Modes

1. **Normal Mode** - Default navigation and basic operations
2. **Search Mode** - Fuzzy search for datasets and groups
3. **Goto Mode** - Quick navigation commands
4. **Dataset Mode** - Data analysis and statistics
5. **Window Mode** - Panel and focus management
6. **Plotting Mode** - Scatter plot creation
7. **Histogram Mode** - Histogram generation

## Mode Switching

### Entering Modes

From Normal Mode, press the following keys to enter other modes:

| Key     | Mode           | Purpose                        |
| ------- | -------------- | ------------------------------ |
| **`s`** | Search Mode    | Fuzzy search (tree focus only) |
| **`g`** | Goto Mode      | Quick navigation               |
| **`d`** | Dataset Mode   | Data analysis                  |
| **`w`** | Window Mode    | Window management              |
| **`p`** | Plotting Mode  | Create scatter plots           |
| **`H`** | Histogram Mode | Generate histograms            |

### Exiting Modes

- **`q`** - Exit current mode and return to Normal Mode
- **`Escape`** - Return to Normal Mode (context-dependent)
- **`Ctrl+Q`** - Force exit the entire application

## Mode Indicators

The current mode is indicated by the **Hotkey Display**: The bottom panel shows mode-specific keyboard shortcuts and has the current mode in its title

## Universal Commands

These commands work in all modes:

| Key            | Action                           |
| -------------- | -------------------------------- |
| **`q`**        | Quit to previous content or exit |
| **`Ctrl+Q`**   | Force quit application           |
| **Arrow Keys** | Navigate (when applicable)       |

## Mode Summary

| Mode          | Key       | Purpose       | Main Features                     |
| ------------- | --------- | ------------- | --------------------------------- |
| **Normal**    | (default) | Navigation    | Tree traversal, file exploration  |
| **Search**    | `s`       | Find items    | Real-time fuzzy search, filtering |
| **Goto**      | `g`       | Quick nav     | Fast tree navigation              |
| **Dataset**   | `d`       | Data analysis | Value inspection, statistics      |
| **Window**    | `w`       | UI control    | Panel focus, layout               |
| **Plotting**  | `p`       | Visualization | Scatter plots                     |
| **Histogram** | `H`       | Distribution  | Statistical plots                 |

## Detailed Mode Documentation

Explore the detailed documentation for each mode:

- [Normal Mode](normal.md) - Basic navigation and control
- [Search Mode](search.md) - Fuzzy search functionality
- [Goto Mode](jump.md) - Quick navigation features
- [Dataset Mode](dataset.md) - Data analysis tools
- [Window Mode](window.md) - Interface management
- [Plotting Mode](plotting.md) - Scatter plot creation
- [Histogram Mode](histogram.md) - Distribution analysis

Each mode page includes comprehensive keyboard reference tables and usage examples.
