# Goto Mode

Goto Mode enables rapid navigation through complex HDF5 file hierarchies with keyboard-driven jump commands.

## Purpose

Goto Mode is designed for:

- Quick navigation to specific locations in the tree
- Rapid movement between related datasets
- Efficient exploration of large, complex file structures
- Finding datasets by name or path patterns

## Keyboard Reference

| Key               | Action               | Description                                  |
| ----------------- | -------------------- | -------------------------------------------- |
| **`t`** / **`g`** | Jump to Top          | Move cursor to the root of the tree          |
| **`b`** / **`G`** | Jump to Bottom       | Move cursor to the last item in the tree     |
| **`p`**           | Jump to Parent       | Move cursor to parent of current item        |
| **`n`**           | Jump to Next Sibling | Move to next item at same hierarchical level |
| **`K`**           | Jump to Key          | Jump to next item containing specified text  |
| **`q`**           | Exit Goto Mode       | Return to Normal Mode                        |

## Entering Goto Mode

From Normal Mode, press **`g`** to enter Goto Mode. The hotkey display will update to show Goto Mode commands.

## Navigation Commands

### Tree Boundaries

**Jump to Top** (**`t/g`**)

- Moves cursor to the root item of the HDF5 file
- Useful for returning to the beginning after deep exploration
- Equivalent to pressing Home in many applications

**Jump to Bottom** (**`b/G`**)

- Moves cursor to the last visible item in the tree
- Accounts for currently expanded/collapsed state
- Useful for reaching the end of large expanded sections

### Hierarchical Navigation

**Jump to Parent** (**`p`**)

- Moves cursor to the parent group of the current item
- For items at the root level, stays at current position
- Maintains tree expansion state
- Useful for moving up the hierarchy quickly

Example:

```
▼ simulation/
  ▼ particles/
    ▶ coordinates     ← Current position
    ▶ velocities
```

Pressing **`p`** moves to `particles/`, pressing **`p`** again moves to `simulation/`.

**Jump to Next Sibling** (**`n`**)

- Moves to the next item at the same hierarchical level
- Skips over children of intervening groups
- Wraps to first sibling if at the last sibling

Example:

```
▼ simulation/
  ▶ particles/        ← Current position
  ▶ metadata/         ← Next sibling
  ▶ analysis/
```

Pressing **`n`** moves from `particles/` to `metadata/`.

### Search Navigation

**Jump to Key** (**`K`**)

- Prompts for text input
- Moves to the next item whose name contains the specified text
- Case-insensitive search
- Continues from current position

Usage:

1. Press **`K`**
2. Enter search text (e.g., "coord")
3. Press Enter
4. Cursor moves to next item containing "coord" in its name

!!! note "Search Scope"
Search only covers currently loaded tree items. If groups are collapsed, their children won't be searched. If you want to search within collapsed groups, use the Search Mode (**`s`**) instead (see [Search Mode](search.md)).
