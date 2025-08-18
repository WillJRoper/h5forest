# Plotting Mode

Plotting Mode enables creation of scatter plots from HDF5 datasets. It provides tools for axis selection, plot configuration, and data visualization to help understand relationships between variables.

## Purpose

Plotting Mode is designed for:
- Creating scatter plots from numeric datasets
- Exploring relationships between different variables
- Configuring plot parameters (scaling, ranges, etc.)
- Generating publication-quality visualizations

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

## Entering Plotting Mode

From Normal Mode, press **`p`** to enter Plotting Mode. You can also access it via Window Mode (**`w`** → **`p`**) which simultaneously enters Plotting Mode and focuses the plot panel.

## Creating Scatter Plots

### Basic Plotting Workflow

1. **Navigate to first dataset** (x-axis data)
2. **Enter Plotting Mode** (**`p`**)
3. **Select x-axis** (**`x`**) - assigns current dataset
4. **Navigate to second dataset** (y-axis data)
5. **Select y-axis** (**`y`**) - assigns current dataset
6. **Generate plot** (**`p`**)

### Axis Selection Details

**X-axis Selection** (**`x`**)
- Assigns the currently selected dataset as x-axis data
- Works with any numeric dataset
- Previous x-axis selection is replaced
- Dataset name appears in plot configuration

**Y-axis Selection** (**`y`**)
- Assigns the currently selected dataset as y-axis data
- Works with any numeric dataset  
- Previous y-axis selection is replaced
- Dataset name appears in plot configuration

!!! note "Dataset Compatibility"
    Both datasets should have compatible shapes for meaningful plotting. h5forest will attempt to handle shape mismatches gracefully.

### Plot Generation

**Plot** (**`p`**)
- Creates scatter plot using selected x and y axes
- Displays plot in the plot panel
- Uses current configuration settings
- Shows basic axis labels and title

**Plot and Save** (**`P`**)
- Generates plot as above
- Prompts for filename
- Saves plot to file (PNG, PDF, etc.)
- Useful for including plots in reports or publications

## Plot Configuration

### Configuration Editor

**Edit Configuration** (**`e`**)
- Opens interactive configuration editor
- Shows configurable parameters as a list
- Allows editing of plot appearance and behavior
- Available only when x and y axes are selected

### Configurable Parameters

Common plot parameters include:
- **X-axis scale**: Linear or logarithmic
- **Y-axis scale**: Linear or logarithmic  
- **Point size**: Marker size for scatter points
- **Alpha**: Transparency of points
- **Color scheme**: Color mapping options
- **Axis ranges**: Manual override of automatic ranges

### Parameter Editing

**Edit Parameter** (**`Enter`**)
- When in configuration mode, edits the parameter under cursor
- Toggle options (like linear/log scale) with simple selection
- Numeric parameters accept typed input
- String parameters accept text input

**Reset Configuration** (**`r`**)
- Restores all parameters to default values
- Useful when configuration becomes too complex
- Preserves axis selections, resets only display parameters

## Advanced Plotting Features

### Scale Options

**Linear vs Logarithmic Scaling**
- Toggle x-axis and y-axis between linear and log scales
- Logarithmic scaling useful for data spanning many orders of magnitude
- Automatic handling of zero and negative values in log scale

**Custom Ranges**
- Override automatic axis ranges
- Useful for focusing on specific data regions
- Zoom in on areas of interest

### Visual Customization

**Point Appearance**
- Adjust marker size for better visibility
- Control transparency (alpha) for dense datasets
- Choose appropriate symbols and colors

**Axis Labels and Titles**
- Automatic labeling based on dataset names and paths
- Include units from HDF5 attributes when available
- Clear, informative plot titles

### Large Dataset Handling

**Automatic Subsampling**
- Large datasets are intelligently subsampled for plotting
- Maintains statistical properties while improving performance
- Prevents overcrowded, unreadable plots

**Performance Optimization**
- Efficient plotting algorithms for interactive response
- Memory-conscious handling of massive datasets
- Progress indication for slow plotting operations

## Data Compatibility

### Supported Data Types

**Numeric Data**
- All integer types (int8, int16, int32, int64)
- All floating point types (float32, float64)
- Complex numbers (plots magnitude vs phase or real vs imaginary)

**Multidimensional Arrays**
- 1D arrays: Direct plotting
- 2D arrays: Plots each column or flattened data
- Higher dimensions: Flattened or user-selected slices

### Shape Compatibility

**Matching Shapes**
- Ideal: Both datasets have identical shapes
- Compatible: Datasets can be broadcast together
- Mismatched: h5forest attempts reasonable interpretation

**Common Scenarios**
- Same length 1D arrays: Direct scatter plot
- 2D position + 1D property: Property vs position component
- Time series: Value vs time or value vs index

## Workflow Examples

### Basic Relationship Exploration
```
1. Navigate to first variable (e.g., temperature)
2. Press 'p' to enter Plotting Mode
3. Press 'x' to select as x-axis
4. Navigate to second variable (e.g., pressure)
5. Press 'y' to select as y-axis
6. Press 'p' to generate scatter plot
7. Examine correlation in plot panel
```

### Publication-Quality Plot
```
1. Select axes as above
2. Press 'e' to edit configuration
3. Set logarithmic scales if appropriate
4. Adjust point size and transparency
5. Set custom axis ranges if needed
6. Press 'P' to plot and save
7. Provide filename for saved plot
```

### Comparative Analysis
```
1. Create plot of first variable pair
2. Use Jump Mode to find related datasets
3. Select new y-axis variable
4. Press 'p' to overlay or replace plot
5. Compare relationships visually
```

## Error Handling

### Common Issues

**No Axis Selected**
- Clear message when trying to plot without x or y axis
- Guidance on axis selection process

**Incompatible Data Types**
- Graceful handling of non-numeric data
- Suggestions for data type conversion

**Shape Mismatches**
- Automatic attempt at reasonable interpretation
- Clear error messages for irreconcilable shapes

**Memory Limitations**
- Automatic subsampling for very large datasets
- User notification of subsampling when it occurs

### Recovery Strategies
- Reset configuration (**`r`**) to start fresh
- Check dataset compatibility in Dataset Mode first
- Use range viewing in Dataset Mode to validate data

## Integration with Other Modes

### Data Preparation
Use Dataset Mode before plotting:
- Check data ranges with min/max statistics
- Verify data quality with value viewing
- Understand data distribution

### Navigation
Use Jump Mode and Normal Mode:
- Quickly find related datasets for comparison
- Navigate between related variables efficiently
- Explore file structure to understand relationships

### Analysis Pipeline
```
Normal Mode → Find datasets
Dataset Mode → Validate data quality  
Plotting Mode → Explore relationships
Histogram Mode → Understand distributions
```

## Performance Tips

!!! tip "Large Datasets"
    For very large datasets, h5forest automatically subsamples to maintain interactive performance while preserving statistical properties.

!!! tip "Configuration Reuse"
    Plot configurations persist while in Plotting Mode, making it easy to try different variable combinations with the same settings.

!!! tip "File Organization"
    Well-organized HDF5 files with clear dataset names and appropriate attributes will result in better automatic plot labeling.

!!! warning "Memory Usage"
    Very large 2D datasets may require significant memory for plotting. Consider using Dataset Mode range viewing to plot subsets if memory is limited.

## Visualization Best Practices

### Effective Scatter Plots
- Choose appropriate scales (linear vs log) based on data range
- Adjust point size and transparency for data density
- Use meaningful axis labels and titles
- Consider color coding for additional dimensions

### Data Exploration Strategy
1. Start with overview plots of key variables
2. Use logarithmic scales for wide dynamic ranges
3. Examine outliers and data quality issues
4. Create focused plots of interesting relationships

## Next Steps

Plotting Mode works seamlessly with other analysis tools:

- Use [Dataset Mode](dataset.md) to understand individual variables before plotting
- Combine with [Histogram Mode](histogram.md) for comprehensive data analysis
- Use [Jump Mode](jump.md) to quickly find related datasets for comparison
- Return to [Normal Mode](normal.md) to navigate and explore file structure

The combination of statistical analysis and visualization provides powerful insights into your HDF5 data.