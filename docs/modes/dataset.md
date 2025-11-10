# Dataset Mode

Dataset Mode provides comprehensive tools for examining and analyzing HDF5 dataset contents. Use this mode to inspect actual data values, compute statistics, and validate data quality.

## Purpose

Dataset Mode is designed for:
- Viewing actual dataset values and content
- Computing statistical measures (min/max, mean, standard deviation)
- Data validation and quality checking
- Understanding data distributions and ranges

## Entering Dataset Mode

From Normal Mode, navigate to any dataset and press **`d`** to enter Dataset Mode.

## Keyboard Reference

### Value Inspection

| Key | Action | Description |
|-----|--------|-------------|
| **`v`** | View Values | Show dataset values (truncated for large arrays) |
| **`V`** | View Range | Show values in specific index range (prompts for input) |
| **`c`** | Close Values | Hide the values panel |

### Statistical Analysis

| Key | Action | Description |
|-----|--------|-------------|
| **`m`** | Min/Max | Calculate minimum and maximum values |
| **`M`** | Mean | Calculate mean (average) value |
| **`s`** | Standard Deviation | Calculate standard deviation |

### Mode Control

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Exit Dataset Mode | Return to Normal Mode |

## Basic Usage

**Value Inspection:**
- `v` - View dataset values (truncated for large arrays)
- `V` - View specific range (prompts for start-end indices)
- `c` - Close values panel

**Statistics:**
- `m` - Calculate min/max values
- `M` - Calculate mean
- `s` - Calculate standard deviation

**Exit:**
- `q` - Return to Normal Mode

## Notes

- Only available when a dataset is selected (not a group)
- Large datasets display progress bars during statistical computations
- Statistical operations require numeric data types
- String datasets display their values but cannot compute numerical statistics
- Values panel appears on the right side of the screen