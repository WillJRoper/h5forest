# Dataset Mode

Dataset Mode is where the magic happens - or where you discover your data is complete nonsense. Either way, it's comprehensive.

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

- Only works when a dataset (not group) is selected - because asking for statistics on a folder is like asking for the average color of a rainbow
- Large datasets show progress bars so you know it's actually doing something and hasn't just given up on life
- Statistics work on numeric data; strings just show you their values and shrug
- Values panel opens on the right side of screen (we're not monsters)