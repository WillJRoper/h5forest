# Search Mode

Search Mode provides real-time fuzzy search functionality to quickly find datasets and groups in your HDF5 file. As you type, the tree filters in real-time to show only matching nodes and their parent hierarchy.

## Purpose

Search Mode is designed for:
- Quickly finding specific datasets or groups by name
- Filtering large hierarchies to focus on relevant items
- Exploring files with deep or complex structures
- Case-insensitive fuzzy matching

## Entering Search Mode

From Normal Mode, with the **tree panel focused**:
- Press **`s`** to enter Search Mode

The search input box will appear at the bottom of the screen and receive focus.

## Keyboard Reference

| Key | Action | Description |
|-----|--------|-------------|
| **`Enter`** | Accept Results | Keep filtered tree and return to Normal Mode |
| **`Escape`** | Cancel Search | Restore original tree and return to Normal Mode |
| **`Ctrl+C`** | Cancel Search | Same as Escape - restore and return |
| **`Backspace`** | Delete Character | Remove last character from search |
| **Any character** | Add to Search | Add character and update filter |

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
- Example: Searching "gmd" would match "/Group/Mass_Data"

### After Search

**Accept Results (Enter)**:
- Keeps the filtered tree visible
- Returns to Normal Mode
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

## Usage Examples

### Basic Search

1. Press `s` to enter Search Mode
2. Type "temperature" to find all temperature-related datasets
3. Press `Enter` to keep results and explore them
4. Press `r` to restore original tree when done

### Abbreviation Search

1. Press `s` to enter Search Mode
2. Type "gmd" to find paths containing those letters in order
3. Might match: "/Group/Mass_Data", "/Galaxy/Metadata"
4. Press `Escape` if results aren't what you wanted

### Exploring Complex Files

1. Open large HDF5 file with many nested groups
2. Press `s` and search for specific dataset name
3. See only relevant parts of hierarchy
4. Use `d` mode to analyze found datasets
5. Press `r` to restore full tree

## Search Limits

- Maximum of **100 results** displayed to maintain performance
- Results are ranked by match quality (best matches first)
- All query characters must appear in order in the path
- Empty search query shows the full tree

## Tips

- **Start with fewer characters** for broader results
- **Add more characters** to narrow down matches
- **Use abbreviations** of long paths (e.g., "grpsubtemp" for "/Group/Subgroup/Temperature")
- **Accept results** to work with filtered tree before restoring
- **Press `r`** anytime in Normal Mode to reset everything

## Visual Indicators

- **Highlighted nodes**: Matching datasets/groups in search results
- **Expanded parents**: Parent groups opened to show matches
- **Input focus**: Search box at bottom receives keyboard input

## Returning to Normal Mode

From Search Mode:
- **`Enter`** - Accept filtered results, return to Normal Mode
- **`Escape`** or **`Ctrl+C`** - Cancel and restore, return to Normal Mode

Once back in Normal Mode:
- **`r`** - Reset tree to initial state (collapses all)
- All other mode keys work normally

## Related Modes

- [Normal Mode](normal.md) - Return here after search
- [Goto Mode](jump.md) - Alternative navigation method
- [Dataset Mode](dataset.md) - Analyze found datasets
