# h5forest Configuration System

The h5forest configuration system allows users to customize various aspects of the application, including vim mode settings and key bindings.

## Configuration File Location

The configuration file is automatically created at:

```
~/.h5forest/config.yaml
```

When you first run h5forest after installing this version, the configuration file will be automatically created with default settings.

## Configuration File Structure

The configuration file is organized into sections:

### 1. General Configuration

```yaml
configuration:
  # Enable or disable vim-style key bindings
  vim_mode: true

  # UI theme (currently only 'default' is supported)
  theme: default
```

### 2. Keymaps

The `keymaps` section contains key bindings for different modes:

```yaml
keymaps:
  # Normal mode - default mode for general operations
  normal_mode:
    quit: q
    search: s
    copy_path: c
    toggle_attributes: A
    restore_tree: r

  # Tree navigation - moving through the HDF5 structure
  tree_navigation:
    move_up: k
    move_down: j
    move_left: h
    move_right: l
    jump_up_10: "{"
    jump_down_10: "}"
    expand: l
    collapse: h

  # Jump mode - quick navigation commands (press 'g' to enter)
  jump_mode:
    leader: g
    top: g           # gg to go to top
    top_alt: t       # Alternative: just 't' in jump mode
    bottom: G
    bottom_alt: b
    parent: p
    next_sibling: n
    jump_to_key: K

  # Dataset mode - operations on datasets (press 'd' to enter)
  dataset_mode:
    leader: d
    view_values: v
    statistics: s

  # Window mode - focus management (press 'w' to enter)
  window_mode:
    leader: w
    focus_tree: t
    focus_attributes: a
    focus_values: v

  # Plot mode - scatter plot creation (press 'p' to enter)
  plot_mode:
    leader: p
    select_x: x
    select_y: y
    create_plot: p

  # Histogram mode - histogram creation (press 'H' to enter)
  histogram_mode:
    leader: H
    select_dataset: d
    create_histogram: h

  # Search mode - fuzzy search (press 's' to enter)
  search_mode:
    leader: s
    exit: escape
```

## Vim Mode Key Reservation

When `vim_mode: true` is set, the following keys are **reserved** and cannot be remapped to other functions:

- `h`, `j`, `k`, `l` - Basic navigation
- `{`, `}` - Jump 10 lines up/down
- `g`, `G` - Goto commands

### Why Are Keys Reserved?

These keys provide vim-style navigation throughout the application. If you try to remap these keys to other functions while vim mode is enabled, h5forest will display a warning and ignore those remappings.

### Disabling Vim Mode

If you want to use these keys for other purposes, set `vim_mode: false` in your configuration:

```yaml
configuration:
  vim_mode: false
```

## Configuration Examples

### Example 1: Disable Vim Mode

```yaml
configuration:
  vim_mode: false
  theme: default

keymaps:
  normal_mode:
    quit: q
    # Now you can use j, k, etc. for other purposes
    jump_to_bottom: j
```

### Example 2: Customize Search Key

```yaml
configuration:
  vim_mode: true

keymaps:
  normal_mode:
    quit: q
    search: f  # Changed from 's' to 'f'
    copy_path: c
```

### Example 3: Change Dataset Mode Keys

```yaml
keymaps:
  dataset_mode:
    leader: d
    view_values: d  # Changed from 'v' to 'd'
    statistics: S   # Changed from 's' to 'S'
```

## Configuration Validation

The configuration system includes validation to ensure your settings are valid:

1. **YAML Syntax**: If your config file has invalid YAML syntax, h5forest will display an error and use default settings.

2. **Vim Mode Conflicts**: If you try to remap vim reserved keys while vim mode is enabled, you'll see a warning message listing the conflicts.

3. **Missing Sections**: If sections are missing from your config, they will be filled in with default values.

## Programmatic Access

For developers extending h5forest, the configuration can be accessed through the `ConfigManager` singleton:

```python
from h5forest.config import ConfigManager

config = ConfigManager()

# Get configuration values
vim_mode = config.get("configuration.vim_mode")
quit_key = config.get_keymap("normal_mode", "quit")

# Check if vim mode is enabled
if config.is_vim_mode_enabled():
    print("Vim mode is enabled")

# Check if a key is allowed (not reserved)
if config.is_key_allowed("h"):
    print("Key 'h' can be used for custom bindings")
```

## Extending Keybindings (For Developers)

To integrate configuration-based keybindings in h5forest's code:

```python
def _init_app_bindings(app):
    """Set up keybindings using configuration."""

    # Get the configured key for quit action
    quit_key = app.config.get_keymap("normal_mode", "quit")

    def exit_app(event):
        """Exit the app."""
        event.app.exit()

    # Bind using configured key (falls back to default if not set)
    app.kb.add(
        quit_key or "q",
        filter=Condition(lambda: app.flag_normal_mode)
    )(exit_app)
```

## Reloading Configuration

Currently, configuration is loaded when h5forest starts. To apply configuration changes:

1. Edit `~/.h5forest/config.yaml`
2. Restart h5forest

Future versions may support hot-reloading configuration while the application is running.

## Troubleshooting

### Configuration file not found

If h5forest can't find your configuration file, it will automatically create a default one at `~/.h5forest/config.yaml`.

### Invalid YAML syntax

If you see an error about YAML parsing:
1. Check your YAML syntax (proper indentation, colons, etc.)
2. Use a YAML validator like [yamllint.com](https://www.yamllint.com/)
3. You can delete the file and h5forest will recreate it with defaults

### Keys not working as expected

1. Verify your configuration syntax is correct
2. Check if vim mode is enabled and you're trying to remap reserved keys
3. Make sure you're in the correct mode (normal, jump, dataset, etc.)
4. Restart h5forest after making changes

## Default Configuration

If you want to reset to default configuration:

1. Delete `~/.h5forest/config.yaml`
2. Run h5forest again
3. A new default configuration file will be created automatically

Alternatively, you can view the default configuration in the source code at:
`src/h5forest/config.py` (search for `DEFAULT_CONFIG`)
