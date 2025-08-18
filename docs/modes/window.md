# Window Mode

Window Mode provides control over panel focus and interface management. It allows you to navigate between different UI panels and customize the interface layout for optimal workflow.

## Purpose

Window Mode is designed for:
- Switching focus between different interface panels
- Navigating to specific visualization panels
- Managing interface layout and focus
- Optimizing screen real estate usage

## Keyboard Reference

### Panel Navigation

| Key | Action | Description |
|-----|--------|-------------|
| **`t`** | Focus Tree | Move input focus to the tree panel |
| **`a`** | Focus Attributes | Move input focus to the attributes panel |
| **`v`** | Focus Values | Move input focus to the values panel (when visible) |
| **`p`** | Focus Plot | Move input focus to plot panel (also enters Plotting Mode) |
| **`h`** | Focus Histogram | Move input focus to histogram panel (also enters Histogram Mode) |

### Mode Control

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Exit Window Mode | Return to Normal Mode |
| **`Escape`** | Default Focus | Return focus to tree panel and exit Window Mode |

## Entering Window Mode

From Normal Mode, press **`w`** to enter Window Mode. The hotkey display will update to show Window Mode commands.

## Panel Focus Management

### Understanding Focus
In h5forest, "focus" determines which panel receives keyboard input. The focused panel typically has:
- A highlighted border or different visual styling
- Active keyboard navigation
- Responsive cursor movement

### Primary Panels

**Tree Panel** (**`t`**)
- Main navigation panel showing the HDF5 file hierarchy
- Default focus location for most operations
- Always available and focusable

**Attributes Panel** (**`a`**)
- Shows HDF5 attributes for the selected item
- Can be scrolled when it contains many attributes
- Useful when examining detailed metadata

**Values Panel** (**`v`**)
- Displays dataset values when visible
- Only available when values are being shown (Dataset Mode **`v`** command)
- Allows scrolling through large value displays

### Visualization Panels

**Plot Panel** (**`p`**)
- Shows scatter plots and plot configuration
- Automatically enters Plotting Mode when focused
- Combines focus change with mode switching for efficiency

**Histogram Panel** (**`h`**)
- Displays histograms and histogram configuration
- Automatically enters Histogram Mode when focused  
- Streamlines transition to histogram analysis

## Workflow Integration

### Focus-Driven Workflows

**Attribute Examination**
```
1. Navigate to item with many attributes
2. Press 'w' to enter Window Mode
3. Press 'a' to focus attributes panel
4. Use arrow keys to scroll through attributes
5. Press Escape to return to tree focus
```

**Value Analysis**
```
1. Select dataset and view values (Dataset Mode 'v')
2. Press 'w' to enter Window Mode  
3. Press 'v' to focus values panel
4. Scroll through values with arrow keys
5. Press 't' to return focus to tree
```

**Seamless Visualization**
```
1. Position on dataset for plotting
2. Press 'w' then 'p' (enters Plot Mode with focus)
3. Configure and create plot
4. Press 'w' then 'h' (switch to Histogram Mode)
5. Generate histogram of same data
```

### Multi-Panel Analysis

When working with complex data, Window Mode enables efficient multi-panel workflows:

1. **Tree navigation**: Find and select datasets
2. **Attributes review**: Examine metadata and documentation
3. **Values inspection**: Check actual data content
4. **Visualization**: Create plots and histograms

## Panel State Management

### Focus Persistence
- Focus changes persist until explicitly changed
- Returning to Normal Mode maintains last focus
- Some operations automatically return focus to tree

### Panel Visibility
- Focus commands only work for visible panels
- Values panel must be shown first (Dataset Mode **`v`**)
- Plot/histogram panels appear when entering those modes

### Layout Adaptation
- Interface adapts to show focused panels prominently
- Panel sizes adjust based on content and focus
- Optimal layout maintained across focus changes

## Advanced Focus Scenarios

### Scrollable Panels

**Attributes Panel Scrolling**
When focused on attributes panel:
- Arrow keys scroll through attribute list
- Page Up/Down for faster scrolling
- Useful for files with extensive metadata

**Values Panel Navigation**
When focused on values panel:
- Arrow keys navigate through dataset values
- Scroll position independent of tree position
- Particularly useful for examining large datasets

### Context-Sensitive Focus

**Conditional Panel Access**
- Values focus (**`v`**) only works when values panel is visible
- Plot focus (**`p`**) creates plot panel if needed
- Histogram focus (**`h`**) creates histogram panel if needed

**Smart Defaults**
- Default focus returns to tree panel
- Most intuitive panel receives focus after mode changes
- Focus changes support common workflow patterns

## Integration with Other Modes

### Mode Transitions
Window Mode facilitates smooth transitions:

**To Visualization Modes**
- **`p`**: Focus plot panel AND enter Plotting Mode
- **`h`**: Focus histogram panel AND enter Histogram Mode

**From Other Modes**
- Window Mode available from any mode
- Focus changes work across different modes
- Maintains mode-specific functionality

### Focus-Aware Commands

Some mode commands are focus-aware:
- Navigation keys work in the focused panel
- Mode-specific shortcuts respect current focus
- Visualization modes adapt to focus context

## Common Workflows

### Metadata-Heavy Analysis
```
Normal Mode → Select item with rich metadata
Window Mode → 'a' (focus attributes)
             → Scroll through documentation
             → 't' (return to tree focus)
Normal Mode → Continue navigation
```

### Comparative Value Analysis
```
Dataset Mode → 'v' (show values for first dataset)
Window Mode  → 'v' (focus values panel)
             → Examine values in detail
             → 't' (focus tree)
Normal Mode  → Navigate to comparison dataset
Dataset Mode → 'v' (show comparison values)
```

### Visualization Workflow
```
Normal Mode → Position on dataset
Window Mode → 'p' (enter Plot Mode with focus)
Plot Mode   → Configure and generate plot
Window Mode → 'h' (switch to Histogram Mode)
Hist Mode   → Generate histogram
Window Mode → 't' (return to tree focus)
```

## Tips for Efficient Focus Management

!!! tip "Default Returns"
    Use **`Escape`** to quickly return to tree panel focus from any panel.

!!! tip "Mode Combining"
    Window Mode's **`p`** and **`h`** commands efficiently combine focus change with mode switching.

!!! tip "Panel Visibility"
    Remember that you can only focus panels that are currently visible. Show values first before trying to focus them.

!!! warning "Focus Context"
    Be aware of which panel has focus when using navigation keys, as behavior changes based on focus.

## Customization and Preferences

### Layout Preferences
While Window Mode doesn't provide persistent customization, it enables:
- Temporary layout optimization for specific tasks
- Workflow-specific focus patterns
- Efficient multi-panel analysis sessions

### Focus Shortcuts
Learn these focus shortcuts for maximum efficiency:
- **`w`** → **`t`**: Quick return to tree
- **`w`** → **`a`**: Quick attribute examination  
- **`w`** → **`p`**: Quick plotting transition
- **`w`** → **`h`**: Quick histogram analysis

## Performance Considerations

### Focus Changes
- Focus changes are instantaneous
- No performance overhead for panel switching
- Maintains responsiveness even with large files

### Panel Updates
- Focused panels update in real-time
- Background panels remain static until focused
- Efficient memory and processing usage

## Next Steps

Window Mode enhances the efficiency of all other modes:

- Use with [Normal Mode](normal.md) for optimized navigation
- Combine with [Dataset Mode](dataset.md) for detailed value analysis
- Integrate with [Plotting Mode](plotting.md) for seamless visualization
- Coordinate with [Histogram Mode](histogram.md) for statistical analysis
- Leverage with [Jump Mode](jump.md) for rapid repositioning

Mastering Window Mode's focus management significantly improves workflow efficiency across all h5forest operations.