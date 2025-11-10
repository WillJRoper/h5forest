# Normal Mode

Normal Mode is the default mode in h5forest and serves as the foundation for all file exploration. You'll return to this mode after completing tasks in specialized modes, making it the central hub for navigation and mode switching.

## Purpose

Normal Mode is designed for:

- Navigating the HDF5 file tree structure
- Expanding and collapsing groups
- Viewing metadata and attributes
- Switching to other modes for specialized tasks

## Keyboard Reference

### Tree Navigation

| Key               | Action          | Description                        |
| ----------------- | --------------- | ---------------------------------- |
| **`↑`** / **`k`** | Move up         | Move cursor up one line            |
| **`↓`** / **`j`** | Move down       | Move cursor down one line          |
| **`{`**           | Jump up         | Move cursor up 10 lines            |
| **`}`**           | Jump down       | Move cursor down 10 lines          |
| **`Enter`**       | Expand/Collapse | Toggle expansion of selected group |

### Mode Switching

| Key     | Mode           | Description                  |
| ------- | -------------- | ---------------------------- |
| **`g`** | Goto Mode      | Quick navigation commands    |
| **`d`** | Dataset Mode   | Data analysis and statistics |
| **`w`** | Window Mode    | Panel and focus management   |
| **`p`** | Plotting Mode  | Create scatter plots         |
| **`H`** | Histogram Mode | Generate histograms          |
| **`s`** | Search Mode    | Fuzzy search through tree    |

### Interface Control

| Key          | Action            | Description                                                        |
| ------------ | ----------------- | ------------------------------------------------------------------ |
| **`A`**      | Toggle Attributes | Expand/shrink attributes panel                                     |
| **`r`**      | Restore Tree      | Reset tree to initial state (collapses all, clears search results) |
| **`q`**      | Quit              | Exit application                                                   |
| **`Ctrl+Q`** | Force Quit        | Force exit application                                             |

## Basic Usage

- **Movement**: Use arrow keys or `j`/`k` to navigate
- **Fast movement**: Use `{`/`}` to jump 10 lines
- **Expand/collapse**: Press `Enter` on groups
- **View attributes**: Press `A` to toggle expanded attributes panel

## Visual Indicators

- **`▶`**: Collapsed group
- **`▼`**: Expanded group
- **No symbol**: Dataset or empty group

## Panel Information

- **Metadata panel**: Shows item details (shape, type, children count)
- **Attributes panel**: Displays HDF5 attributes as key-value pairs
- Both panels update automatically as you navigate
