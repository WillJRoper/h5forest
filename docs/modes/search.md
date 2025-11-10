# Search Mode

Search Mode provides real-time fuzzy search functionality to quickly find datasets and groups in your HDF5 file. As you type, the tree filters in real-time to show only matching nodes and their parent hierarchy.

## Purpose

Search Mode is designed for:

- Quickly finding specific datasets or groups by name
- Filtering large hierarchies to focus on relevant items
- Exploring files with deep or complex structures

## Entering Search Mode

From Normal Mode:

- Press **`s`** to enter Search Mode

The search input box will appear at the bottom of the screen and receive focus.

## Keyboard Reference

| Key          | Action         | Description                                     |
| ------------ | -------------- | ----------------------------------------------- |
| **`Enter`**  | Accept Results | Keep filtered tree and return to Normal Mode    |
| **`Escape`** | Cancel Search  | Restore original tree and return to Normal Mode |

## How It Works

### Real-time Filtering

As you type in Search Mode:

1. The tree filters in real-time using fuzzy matching
2. Matching nodes are automatically expanded and highlighted
3. Parent nodes are shown to provide context
4. Up to 100 best matches are displayed

### Fuzzy Matching

The search uses intelligent fuzzy matching:

- **Case-insensitive**: "mass" matches "Mass", "MASS", "MaSs"
- **Subsequence matching**: All query characters must appear in order
- **Smart scoring**: Shorter paths with consecutive matches rank higher

### Using The Search Results

**Accept Results (Enter)**:

- Keeps the filtered tree visible and returns to Normal Mode
- All mode commands (d, g, w, p, H) work on filtered results
- Navigate the filtered tree normally

**Cancel Search (Escape)**:

- Restores the tree to its state before search
- Returns to Normal Mode
- Maintains any previously expanded nodes

**Restore to Initial (r in Normal Mode)**:

- Press `r` in Normal Mode to reset tree completely
- Collapses all nodes except root
- Clears any filtered results
- Returns tree to state when file was first opened
