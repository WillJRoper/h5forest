# Jump Mode

Jump Mode provides quick navigation commands for efficiently moving around large HDF5 file hierarchies. It's designed for rapid repositioning within the tree structure.

## Purpose

Jump Mode is designed for:
- Quick navigation to specific locations in the tree
- Rapid movement between related datasets
- Efficient exploration of large, complex file structures
- Finding datasets by name or path patterns

## Keyboard Reference

| Key | Action | Description |
|-----|--------|-------------|
| **`t`** | Jump to Top | Move cursor to the root of the tree |
| **`b`** | Jump to Bottom | Move cursor to the last item in the tree |
| **`p`** | Jump to Parent | Move cursor to parent of current item |
| **`n`** | Jump to Next Sibling | Move to next item at same hierarchical level |
| **`k`** | Jump to Key | Jump to next item containing specified text |
| **`q`** | Exit Jump Mode | Return to Normal Mode |

## Entering Jump Mode

From Normal Mode, press **`j`** to enter Jump Mode. The hotkey display will update to show Jump Mode commands.

## Navigation Commands

### Tree Boundaries

**Jump to Top** (**`t`**)
- Moves cursor to the root item of the HDF5 file
- Useful for returning to the beginning after deep exploration
- Equivalent to pressing Home in many applications

**Jump to Bottom** (**`b`**)
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

**Jump to Key** (**`k`**)
- Prompts for text input
- Moves to the next item whose name contains the specified text
- Case-insensitive search
- Continues from current position

Usage:
1. Press **`k`**
2. Enter search text (e.g., "coord")
3. Press Enter
4. Cursor moves to next item containing "coord" in its name

!!! note "Search Scope"
    Search only covers currently loaded tree items. If groups are collapsed, their children won't be searched.

## Practical Usage Examples

### Quick Return to Root
When deep in a hierarchy:
```bash
# Current position: /simulation/particles/type1/coordinates
# Press 'j' to enter Jump Mode
# Press 't' to jump to root
# Now at: / (root)
```

### Exploring Parallel Structures
When examining similar datasets across different groups:
```bash
# At: /simulation/particles/positions
# Press 'j' then 'p' to go to /simulation/particles/
# Press 'n' to go to /simulation/forces/
# Navigate down to /simulation/forces/positions
```

### Finding Related Datasets
When looking for datasets with similar names:
```bash
# Looking for all "coordinates" datasets
# Press 'j' then 'k'
# Type "coord" and press Enter
# Jumps to next dataset containing "coord"
# Repeat as needed
```

## Workflow Integration

### Large File Exploration
Jump Mode is particularly useful for large files:

1. **Orient yourself**: Use **`t`** to return to root
2. **Survey structure**: Navigate between major groups with **`n`**  
3. **Deep dive**: Use **`p`** to move back up when needed
4. **Find datasets**: Use **`k`** to locate specific items

### Comparative Analysis
When comparing related datasets:

1. Navigate to first dataset in Normal Mode
2. Enter Dataset Mode (**`d`**) to analyze
3. Return to Normal Mode (**`q`**)
4. Enter Jump Mode (**`j`**)
5. Use **`k`** or **`n`** to find related dataset
6. Repeat analysis

### File Structure Documentation
For understanding file organization:

1. Start at root with **`t`**
2. Use **`n`** to move between top-level groups
3. Explore each major section
4. Use **`p`** to return to higher levels
5. Map out the overall structure

## Search Tips

### Effective Search Terms
- Use partial names: "coord" finds "coordinates", "coordinate_x", etc.
- Use distinctive parts: "vel" for velocity datasets
- Use numbers: "0" to find PartType0, timestep_0, etc.

### Search Strategy
1. **Start broad**: Search for general terms first
2. **Refine**: Use more specific terms if too many matches
3. **Multiple searches**: Repeat search to find all instances
4. **Combine with navigation**: Use other Jump Mode commands between searches

## Performance Considerations

### Memory Efficiency
Jump Mode commands work with the currently loaded tree structure:
- No additional memory overhead
- Fast execution even in large files
- Commands respect collapsed groups

### Search Limitations
- Search only covers visible (loaded) items
- Collapsed groups' children are not searched
- Consider expanding major groups before searching

## Integration with Other Modes

### From Jump Mode
- **`q`**: Return to Normal Mode
- Can enter Dataset Mode (**`d`**) after positioning cursor

### To Jump Mode  
- Available from Normal Mode with **`j`**
- Preserves current cursor position
- Returns to exact same position when exiting

## Common Workflows

### Quick Dataset Access
```
Normal Mode → Navigate to general area
Jump Mode → Use 'k' to find specific dataset
Normal Mode → Select dataset
Dataset Mode → Analyze data
```

### Structure Exploration
```
Jump Mode → 't' (go to root)
Normal Mode → Expand major groups
Jump Mode → 'n' (tour top-level groups)
Normal Mode → Dive into interesting areas
```

### Comparative Analysis
```
Normal Mode → Find first dataset
Dataset Mode → Get statistics
Jump Mode → 'k' (find similar dataset)
Dataset Mode → Compare statistics
```

## Tips for Efficiency

!!! tip "Quick Orientation"
    Use **`t`** frequently to return to the root when you get lost in deep hierarchies.

!!! tip "Systematic Exploration"
    Combine **`n`** with Normal Mode expansion to systematically explore each major section.

!!! tip "Search Strategy"
    Expand major groups before searching to ensure comprehensive coverage.

!!! warning "Search Scope"
    Remember that search only covers currently loaded items. Expand groups if you need to search their contents.

## Next Steps

Jump Mode integrates seamlessly with other modes:

- Return to [Normal Mode](normal.md) for detailed navigation
- Enter [Dataset Mode](dataset.md) after positioning cursor on datasets
- Use [Window Mode](window.md) to adjust interface focus
- Switch to [Plotting Mode](plotting.md) or [Histogram Mode](histogram.md) for visualization

The combination of Jump Mode's quick positioning with other modes' specialized tools creates efficient exploration workflows.