# Plotting Mode

Plotting Mode enables creation of scatter plots to visualize relationships between datasets. This mode provides tools for selecting data sources, configuring plot parameters, and generating `matplotlib` visualizations.

## Purpose

Plotting Mode is designed for:

- Creating scatter plots from numeric datasets
- Exploring relationships between different variables

## Entering Plotting Mode

From Normal Mode, press **`p`** to enter Plotting Mode.

## Keyboard Reference

### Axis Selection

| Key     | Action        | Description                             |
| ------- | ------------- | --------------------------------------- |
| **`x`** | Select X-axis | Use dataset under cursor as x-axis data |
| **`y`** | Select Y-axis | Use dataset under cursor as y-axis data |

### Plot Configuration

| Key         | Action              | Description                                                |
| ----------- | ------------------- | ---------------------------------------------------------- |
| **`e`**     | Edit Configuration  | Edit plot configuration editor (when parameters available) |
| **`Enter`** | Edit Parameter      | Edit the parameter under cursor (when in config mode)      |
| **`r`**     | Reset Configuration | Reset plot configuration to defaults                       |

### Plot Generation

| Key     | Action        | Description                           |
| ------- | ------------- | ------------------------------------- |
| **`p`** | Plot          | Generate and display the scatter plot |
| **`P`** | Plot and Save | Generate plot and save to file        |

### Mode Control

| Key     | Action             | Description                                 |
| ------- | ------------------ | ------------------------------------------- |
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

## Scale Toggling

Plotting Mode provides direct key bindings for toggling axis scales:

**Toggle X-Scale** (**`X`**) / **Toggle Y-Scale** (**`Y`**)

- Toggle x/y-axis between linear and logarithmic scale
- Validates x/y-axis data range is computed before toggling
- Checks data compatibility when switching to log scale (must be strictly positive)
- Shows clear error if log scale is incompatible with data (negative/zero values)
- Provides immediate feedback with exact minimum value for diagnosis

## Error Handling

**Data Range Validation**

- Operations like toggling scales require the data range to be computed first
- If you see "data range not yet computed", ensure you've selected datasets with **`x`** and **`y`**
- The system automatically waits for data range computation to finish, preventing race conditions

**Logarithmic Scale Errors**

- **Negative values with log scale**: Error message indicates data contains negative values incompatible with logarithmic scale, showing exact minimum value
- **Zero values with log scale**: Error message indicates data contains zero values incompatible with logarithmic scale, showing exact minimum value
- **Immediate validation**: Scale compatibility is checked immediately when toggling to log scale

## Tips

!!! tip "Start Simple"
Begin with basic scatter plots using default settings. Adjust configurations as needed for better visualization.

!!! warning "Log Scale Constraints"
Logarithmic scales require strictly positive values. The system will prevent you from using log scales with negative or zero data and display a clear error message.
