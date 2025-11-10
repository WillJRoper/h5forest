# Histogram Mode

Histogram Mode provides tools for generating histograms and analyzing data distributions.

## Purpose

Histogram Mode is designed for:

- Creating histograms to understand data distributions
- Quality assessment and outlier detection

## Keyboard Reference

### Data Selection and Histogram Generation

| Key         | Action         | Description                                                       |
| ----------- | -------------- | ----------------------------------------------------------------- |
| **`Enter`** | Select Dataset | Select the dataset under cursor for histogram (when in tree view) |
| **`h`**     | Show Histogram | Compute and display histogram of selected dataset                 |
| **`H`**     | Save Histogram | Compute histogram and save to file                                |

### Direct Configuration

| Key     | Action              | Description                                        |
| ------- | ------------------- | -------------------------------------------------- |
| **`e`** | Edit Config         | Jump to configuration window for advanced editing  |
| **`b`** | Edit Bins           | Edit the number of histogram bins                  |
| **`x`** | Toggle X-Scale      | Toggle x-axis between linear and logarithmic scale |
| **`y`** | Toggle Y-Scale      | Toggle y-axis between linear and logarithmic scale |
| **`r`** | Reset Configuration | Reset histogram configuration to defaults          |

### Direct Configuration Editing (When in Config Window)

| Key         | Action         | Description                     |
| ----------- | -------------- | ------------------------------- |
| **`Enter`** | Edit Parameter | Edit the parameter under cursor |
| **`q`**     | Exit Config    | Return to tree view             |

### Mode Control

| Key     | Action              | Description                               |
| ------- | ------------------- | ----------------------------------------- |
| **`q`** | Exit Histogram Mode | Return to Normal Mode (when in tree view) |

## Entering Histogram Mode

From Normal Mode, press **`H`** to enter Histogram Mode.

## Creating Histograms

### Basic Histogram Workflow

1. **Navigate to dataset** of interest
2. **Enter Histogram Mode** (**`H`**)
3. **Select dataset** (**`Enter`**) - selects the data under cursor for histogram
4. **Generate histogram** (**`h`**) - computes and "shows" the histogram
   4.5. **Save histogram** (**`H`**) - computes and saves the histogram to file
5. **Examine distribution** in histogram panel

### Dataset Selection

**Select Dataset** (**`Enter`**)

- When focused on a dataset in the tree view, press **`Enter`** to select it
- Sets default binning, labels, and scales (linear x and y, 50 bins, key as x-label)
- Displays configuration in the histogram panel

### Histogram Generation

**Show Histogram** (**`h`**)

- Computes histogram using current configuration
- Displays histogram in an external window (using `matplotlib`)

**Save Histogram** (**`H`**)

- Computes histogram as above
- Prompts for filename
- Saves histogram to file (using whatever format specified by filename extension, e.g., PNG, PDF)

## Histogram Configuration

### Direct Configuration Bindings

Histogram Mode provides direct key bindings for common configuration tasks, eliminating the need to enter a separate configuration mode for basic adjustments:

**Edit Number of Bins** (**`b`**)

- Directly edit the number of histogram bins in the prompt
- Updates configuration immediately
- No need to navigate to configuration window

**Toggle X-Scale** (**`x`**) / **Toggle Y-Scale** (**`y`**)

- Instantly toggle x/y-axis between linear and logarithmic scale
- Validates data range is computed before toggling
- Checks data compatibility when switching to log scale (must be strictly positive)
- Shows clear error if log scale is incompatible with data (negative/zero values)
- Updates configuration display immediately

### Advanced Configuration Window

**Edit Config** (**`e`**)

- Switches to the full configuration window for advanced editing
- Allows editing of all parameters
- Navigate parameters with arrow keys or Vim motion keys
- Press **`Enter`** to edit parameter under cursor
- Press **`q`** to return to tree view

### Configuration Reset

**Reset Configuration** (**`r`**)

- Restores all parameters to defaults
- Clears dataset selection
- Closes any open histogram windows
- Returns to clean state for new analysis

## Error Handling

### Common Issues

**Non-Numeric Data**

- Clear error messages for string or compound datasets
- Suggestions for appropriate data types
- Guidance on data selection

**Empty Datasets**

- Graceful handling of zero-length arrays
- Appropriate error messages
- Suggestions for data validation

**Data Range Validation**

- **Data range not yet computed**: Operations like toggling scales or editing bins require the data range to be computed first. If you see "data range not yet computed", ensure you've selected a dataset with **`Enter`**. You may need to wait for the background computation to complete for large datasets.

**Logarithmic Scale Errors**

- **Negative values with log x-scale**: Error message indicates data contains negative values incompatible with logarithmic x-axis. Shows exact minimum value for diagnosis.
- **Zero values with log x-scale**: Error message indicates data contains zero values incompatible with logarithmic x-axis. Shows exact minimum value for diagnosis.
- **Zero histogram counts with log y-scale**: Error message indicates some bins have zero counts, incompatible with logarithmic y-axis. Shows exact minimum count for diagnosis.
- **Immediate validation**: Scale compatibility is checked immediately when toggling to log scale, providing instant feedback.

## Tips

!!! tip "Start Simple"
Begin with default histogram settings, then refine configuration based on initial results. Use direct key bindings (**`b`**, **`x`**, **`y`**) for quick adjustments.

!!! tip "Bin Count Guidelines"
For most datasets, automatic binning (50 bins) works well. Press **`b`** to adjust: increase bins for more detail, decrease for smoother curves.

!!! warning "Log Scale Constraints"
Logarithmic scales require strictly positive values. The system will prevent you from using log scales with negative or zero data and display a clear error message.
