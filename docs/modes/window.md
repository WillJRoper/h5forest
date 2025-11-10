# Window Mode

Window Mode provides control over panel focus and interface management. It allows you to navigate between different UI panels.

## Purpose

Window Mode is designed for:

- Switching focus between different interface panels
- Managing interface layout and focus
- Optimizing screen real estate usage

## Keyboard Reference

### Panel Navigation

| Key     | Action           | Description                                                      |
| ------- | ---------------- | ---------------------------------------------------------------- |
| **`t`** | Focus Tree       | Move input focus to the tree panel                               |
| **`a`** | Focus Attributes | Move input focus to the attributes panel                         |
| **`v`** | Focus Values     | Move input focus to the values panel (when visible)              |
| **`p`** | Focus Plot       | Move input focus to plot panel (also enters Plotting Mode)       |
| **`h`** | Focus Histogram  | Move input focus to histogram panel (also enters Histogram Mode) |

### Mode Control

| Key          | Action           | Description                                     |
| ------------ | ---------------- | ----------------------------------------------- |
| **`q`**      | Exit Window Mode | Return to Normal Mode                           |
| **`Escape`** | Default Focus    | Return focus to tree panel and exit Window Mode |

## Entering Window Mode

From Normal Mode, press **`w`** to enter Window Mode. The hotkey display will update to show Window Mode commands.

## Panel Focus Management

### Understanding Focus

In h5forest, "focus" determines which panel receives keyboard input. Once focused you will see the cursor in the selected panel.
