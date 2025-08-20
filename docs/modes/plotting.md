# Plotting Mode

Plotting Mode is for when you need to turn your mysterious numerical soup into beautiful scatter plots. Because sometimes the only way to understand your data is to throw it at a graph and see what sticks.

## Purpose

Plotting Mode is designed for:
- Creating scatter plots from numeric datasets
- Exploring relationships between different variables
- Configuring plot parameters (scaling, ranges, etc.)
- Generating visualizations for analysis

## Entering Plotting Mode

From Normal Mode, press **`p`** to enter Plotting Mode.

## Keyboard Reference

### Axis Selection

| Key | Action | Description |
|-----|--------|-------------|
| **`x`** | Select X-axis | Use dataset under cursor as x-axis data |
| **`y`** | Select Y-axis | Use dataset under cursor as y-axis data |

### Plot Configuration

| Key | Action | Description |
|-----|--------|-------------|
| **`e`** | Edit Configuration | Open plot configuration editor (when parameters available) |
| **`Enter`** | Edit Parameter | Edit the parameter under cursor (when in config mode) |
| **`r`** | Reset Configuration | Reset plot configuration to defaults |

### Plot Generation

| Key | Action | Description |
|-----|--------|-------------|
| **`p`** | Plot | Generate and display the scatter plot |
| **`P`** | Plot and Save | Generate plot and save to file |

### Mode Control

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Exit Plotting Mode | Return to Normal Mode or exit configuration |

## Basic Workflow

1. Navigate to first dataset in Normal Mode
2. Press `p` to enter Plotting Mode  
3. Press `x` to select x-axis dataset
4. Navigate to second dataset
5. Press `y` to select y-axis dataset
6. Press `p` to generate scatter plot

## Configuration

**Plot Configuration:**
- `e` - Edit plot configuration (when both axes selected)
- `r` - Reset configuration to defaults
- `Enter` - Edit selected parameter (when in config mode)
- `P` - Generate plot and save to file

**Available Parameters:**
- X/Y axis scaling (linear or logarithmic)
- Point size and transparency
- Color schemes
- Axis ranges

## Requirements and Notes

- Only works with numeric datasets (sorry, but you can't plot your grocery list)
- Both datasets should have compatible shapes - mismatched arrays are like trying to dance with someone who has three legs
- Large datasets are automatically subsampled so your computer doesn't catch fire
- Plot appears in right panel when generated (assuming you've done everything correctly)
- Configuration settings persist while in Plotting Mode, unlike your motivation on Monday mornings