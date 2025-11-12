# Configuration file

The h5forest configuration system allows users to customize various aspects of the application, including key bindings and vim-style navigation.

## Configuration File Location

The configuration file is automatically created the first time you run `h5forest` and is located at:

```
~/.h5forest/config.yaml
```

When you update `h5forest` to a new version with additional configuration options, your config file will be automatically migrated to include the new options while preserving your custom settings.

## Configuration File Structure

The configuration file is organized into sections:

### 0. Version (Automatic)

```yaml
# Configuration version - DO NOT EDIT
# This is used to automatically update your config when h5forest is upgraded
version: "1.0.0"
```

**Important:** The version field is managed automatically by h5forest. When you upgrade to a newer version of h5forest with new configuration options, your config file will be automatically migrated. New options will be added while preserving all your custom settings.

While editing this will not break anything, it is recommended to leave it unchanged, if it is edited then the code will just assume it is an older version and attempt to migrate it again.

### 1. General Configuration

```yaml
configuration:
  # Enable or disable vim-style key bindings (h, j, k, l for navigation)
  # When enabled, vim navigation keys are reserved and cannot be remapped
  vim_mode: false

  # Should we always chunk large datasets when possible? Default is false which
  # prompts the user each time a large dataset is accessed to ask for
  # confirmation of loading/processing chunk by chunk.
  always_chunk: false
```

**Note:** Vim mode is **optional** and disabled by default. To enable vim-style navigation, edit `~/.h5forest/config.yaml` and set `vim_mode: true`.

### 2. Keymaps

The `keymaps` section contains key bindings for different modes:

```yaml
keymaps:
  # Normal mode - default mode for general operations
  normal_mode:
    quit: q
    copy_path: c
    expand_attributes: A
    restore_tree: r

  # Tree navigation - moving through the HDF5 structure
  # (Enabling vim_mode automatically adds h,j,k,l bindings)
  tree_navigation:
    move_up: up
    move_down: down
    move_left: left
    move_right: right
    jump_up_10: "{"
    jump_down_10: "}"
    expand: enter
    expand/collapse: enter # alias maintained for backwards compatibility

  # Jump mode - quick navigation commands (press 'g' to enter)
  jump_mode:
    leader: g
    top: g # gg to go to top
    top_alt: t # Alternative: just 't' in jump mode
    bottom: G
    bottom_alt: b
    parent: p
    next_sibling: n
    jump_to_key: K

  # Dataset mode - operations on datasets (press 'd' to enter)
  dataset_mode:
    leader: d
    view_values: v
    view_values_range: V
    close_values: c
    min_max: m
    mean: M
    std_dev: s

  # Window mode - focus management (press 'w' to enter)
  window_mode:
    leader: w
    focus_tree: t
    focus_attributes: a
    focus_values: v
    focus_plot: p
    focus_hist: h

  # Plot mode - scatter plot creation (press 'p' to enter)
  plot_mode:
    leader: p
    edit_config: e
    edit_entry: enter
    select_x: x
    select_y: y
    toggle_x_scale: X
    toggle_y_scale: Y
    reset: r
    show_plot: p
    save_plot: P

  # Histogram mode - histogram creation (press 'H' to enter)
  hist_mode:
    leader: H
    edit_config: e
    edit_entry: enter
    select_data: enter
    edit_bins: b
    toggle_x_scale: x
    toggle_y_scale: y
    reset: r
    show_hist: h
    save_hist: H

  # Search mode - fuzzy search (press 's' to enter)
  search_mode:
    leader: s
    accept_search: enter
    cancel_search: c-c
    exit_search: escape
```

## Vim Mode (Optional Feature)

**Vim mode is optional and disabled by default.** By default, all keys are available for custom bindings.

### Enabling Vim Mode

To enable vim-style navigation, edit `~/.h5forest/config.yaml` and set:

```yaml
configuration:
  vim_mode: true
```

### Vim Mode Key Reservation

When `vim_mode: true` is enabled, the following keys are **reserved** and cannot be remapped to other functions:

- `h`, `j`, `k`, `l` - Basic navigation
- `g`, `G` - Goto commands

These keys provide vim-style navigation throughout the application. If you try to remap these keys to other functions while vim mode is enabled, h5forest will display a warning and ignore those remappings.

## Extending Keybindings (For Developers)

To integrate configuration-based keybindings in h5forest's code you can simply add them to the config, define the functions to bind to them and then add them to H5KeyBindings with a binding and a label:
