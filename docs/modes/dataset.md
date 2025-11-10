# Dataset Mode

Dataset Mode provides tools for examining and analyzing HDF5 dataset contents. Use this mode to inspect actual data values, compute statistics, and validate data quality.

## Purpose

Dataset Mode is designed for:

- Viewing actual dataset values and content
- Computing simple statistics (min/max, mean, standard deviation)
- Understanding data distributions and ranges

## Entering Dataset Mode

From Normal Mode, navigate to any dataset and press **`d`** to enter Dataset Mode.

## Keyboard Reference

### Value Inspection

| Key     | Action       | Description                                             |
| ------- | ------------ | ------------------------------------------------------- |
| **`v`** | View Values  | Show dataset values (truncated for large arrays)        |
| **`V`** | View Range   | Show values in specific index range (prompts for input) |
| **`c`** | Close Values | Hide the values panel                                   |

### Statistical Analysis

| Key     | Action             | Description                          |
| ------- | ------------------ | ------------------------------------ |
| **`m`** | Min/Max            | Calculate minimum and maximum values |
| **`M`** | Mean               | Calculate mean (average) value       |
| **`s`** | Standard Deviation | Calculate standard deviation         |

### Mode Control

| Key     | Action            | Description           |
| ------- | ----------------- | --------------------- |
| **`q`** | Exit Dataset Mode | Return to Normal Mode |

## Notes

- Only available when a dataset is selected (not a group)
- Large datasets display progress bars during computations
- Statistical operations require numeric data types
- Values panel appears on the right side of the screen
