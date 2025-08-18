# Dataset Mode

Dataset Mode provides comprehensive tools for analyzing and inspecting HDF5 datasets. It offers value viewing, statistical analysis, and data validation capabilities.

## Purpose

Dataset Mode is designed for:
- Viewing actual dataset values and content
- Computing statistical measures (min/max, mean, standard deviation)
- Data validation and quality checking
- Understanding data distributions and ranges

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

## Entering Dataset Mode

From Normal Mode, navigate to any dataset and press **`d`** to enter Dataset Mode. The hotkey display will update to show Dataset Mode commands.

!!! note "Dataset Selection"
    Dataset Mode commands only work when a dataset (not a group) is selected. The metadata panel will show "Dataset:" for valid targets.

## Value Inspection

### Basic Value Viewing

**View Values** (**`v`**)
- Shows actual data content from the selected dataset
- Automatically truncates large datasets to prevent overwhelming the interface
- Opens the values panel on the right side of the screen

Example output for a small dataset:
```
[[1.234 5.678 9.012]
 [2.345 6.789 0.123]
 [3.456 7.890 1.234]]
```

Example output for a large dataset:
```
[[1.234 5.678 9.012]
 [2.345 6.789 0.123]
 [3.456 7.890 1.234]
 ...
 
Showing 1000/3000000 elements.
```

### Range-Specific Viewing

**View Range** (**`V`**)
- Prompts for specific start and end indices
- Allows examination of particular sections of large datasets
- Useful for inspecting specific data regions

Usage:
1. Press **`V`**
2. Enter range in format `start:end` (e.g., `100:200`)
3. Press Enter to view elements 100 through 199

Range examples:
- `0:100` - First 100 elements
- `1000:1100` - Elements 1000-1099
- `-100:` - Last 100 elements (in some contexts)

### Closing Values Panel

**Close Values** (**`c`**)
- Hides the values panel
- Returns screen space to tree and metadata
- Values can be reopened with **`v`** or **`V`**

## Statistical Analysis

### Minimum and Maximum Values

**Min/Max** (**`m`**)
- Computes global minimum and maximum values across the entire dataset
- Uses efficient chunked processing for large datasets
- Shows progress bar for time-intensive operations

Example output:
```
Minimum: -15.7432
Maximum: 98.2156
```

For large datasets, you'll see a progress indicator:
```
Min/Max ████████████████████████████████ 100%
Minimum: -15.7432
Maximum: 98.2156
```

### Mean Calculation

**Mean** (**`M`**)
- Calculates the arithmetic mean (average) of all values
- Handles large datasets efficiently with streaming computation
- Provides progress feedback for long operations

Example output:
```
Mean: 42.7891
```

### Standard Deviation

**Standard Deviation** (**`s`**)
- Computes the standard deviation across all dataset values
- Uses numerically stable algorithms
- Efficient chunked processing for memory management

Example output:
```
Standard Deviation: 12.3456
```

## Data Type Considerations

### Numeric Data
All statistical functions work with:
- Integer types (int8, int16, int32, int64)
- Floating point types (float32, float64)
- Complex numbers (statistics on magnitude)

### Non-Numeric Data
- String datasets: Only value viewing is available
- Boolean datasets: Statistics show counts/percentages
- Compound datasets: Limited statistical support

### Multidimensional Arrays
- Statistics computed across all dimensions (flattened)
- Value viewing respects array structure
- Large arrays are intelligently subsampled for display

## Performance and Memory Management

### Chunked Processing
For large datasets, h5forest uses sophisticated chunked processing:

1. **Automatic chunking**: Based on available memory and dataset size
2. **Progress feedback**: Shows completion percentage for long operations
3. **Memory safety**: Prevents system memory overflow
4. **Interruption**: Operations can be cancelled with **`Ctrl+C`**

### Lazy Computation
- Statistics are computed on-demand only
- Results are displayed immediately when ready
- No unnecessary computation or memory usage

### Optimization Strategies
h5forest automatically optimizes based on:
- Dataset size and chunk structure
- Available system memory
- HDF5 file compression and layout

## Workflow Examples

### Quick Data Validation
```
1. Navigate to dataset in Normal Mode
2. Press 'd' to enter Dataset Mode
3. Press 'v' to see sample values
4. Press 'm' to check data range
5. Press 'q' to return to Normal Mode
```

### Statistical Summary
```
1. Select dataset of interest
2. Enter Dataset Mode ('d')
3. Get min/max ('m') for range
4. Calculate mean ('M') for central tendency
5. Compute std dev ('s') for spread
6. View values ('v') to validate results
```

### Data Quality Check
```
1. Check metadata for expected shape/type
2. View sample values ('v') for sanity
3. Check range ('m') for outliers
4. Verify mean ('M') against expectations
5. Use range viewing ('V') to examine suspicious regions
```

## Error Handling

### Common Issues

**Dataset Too Large**
- Operations automatically use chunked processing
- Progress bars indicate completion
- Can be interrupted if necessary

**Incompatible Data Types**
- Clear error messages for unsupported operations
- Fallback to value viewing when possible

**Memory Constraints**
- Automatic adjustment of chunk sizes
- Graceful degradation for very large datasets

### Recovery Strategies
- Use range viewing for manageable subset analysis
- Check dataset metadata before heavy operations
- Consider system memory when working with massive datasets

## Advanced Features

### Value Panel Navigation
When the values panel is open:
- Scroll through values using normal navigation
- Values panel can be focused using Window Mode
- Panel resizes based on content and available space

### Statistical Precision
- Floating point statistics use appropriate precision
- Large integer datasets maintain accuracy
- Scientific notation for very large/small values

### Integration with Visualization
Dataset Mode statistics inform visualization modes:
- Min/max values help set plot ranges
- Mean and std dev guide histogram binning
- Value inspection helps choose appropriate plot types

## Tips for Efficient Analysis

!!! tip "Start Small"
    For very large datasets, use range viewing (**`V`**) to examine representative samples before computing full statistics.

!!! tip "Progress Monitoring"
    Watch progress bars for long operations. Very large datasets may take several minutes for complete statistical analysis.

!!! tip "Memory Awareness"
    If system memory is limited, avoid computing multiple statistics simultaneously on massive datasets.

!!! warning "Data Types"
    Check dataset metadata before statistical analysis. Some operations may not be meaningful for certain data types.

## Integration with Other Modes

### From Dataset Mode
- **`q`**: Return to Normal Mode
- Can switch to visualization modes after statistical analysis

### To Dataset Mode
- Available from Normal Mode when a dataset is selected
- Preserves current dataset selection
- Statistical computations begin fresh each time

### With Visualization Modes
- Statistical results inform plotting ranges
- Min/max values guide axis scaling
- Mean values help center visualizations

## Next Steps

Dataset Mode provides the foundation for data understanding:

- Use [Plotting Mode](plotting.md) to visualize relationships between datasets
- Use [Histogram Mode](histogram.md) to understand data distributions  
- Return to [Normal Mode](normal.md) to navigate to related datasets
- Use [Jump Mode](jump.md) to quickly find similar datasets for comparison

The statistical insights from Dataset Mode guide effective use of visualization and further analysis.