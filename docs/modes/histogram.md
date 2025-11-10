# Histogram Mode

Histogram Mode provides tools for generating histograms and analyzing data distributions. It enables exploration of statistical properties, data quality assessment, and distribution visualization for HDF5 datasets.

## Purpose

Histogram Mode is designed for:
- Creating histograms to understand data distributions
- Analyzing statistical properties of datasets
- Quality assessment and outlier detection
- Comparing distributions across related datasets

## Keyboard Reference

### Data Selection and Histogram Generation

| Key | Action | Description |
|-----|--------|-------------|
| **`Enter`** | Select Dataset | Select the dataset under cursor for histogram (when in tree view) |
| **`h`** | Show Histogram | Compute and display histogram of selected dataset |
| **`H`** | Save Histogram | Compute histogram and save to file |

### Direct Configuration

| Key | Action | Description |
|-----|--------|-------------|
| **`b`** | Edit Bins | Edit the number of histogram bins |
| **`x`** | Toggle X-Scale | Toggle x-axis between linear and logarithmic scale |
| **`y`** | Toggle Y-Scale | Toggle y-axis between linear and logarithmic scale |
| **`J`** | Jump to Config | Jump to configuration window for advanced editing |
| **`r`** | Reset Configuration | Reset histogram configuration to defaults |

### Advanced Configuration (When in Config Window)

| Key | Action | Description |
|-----|--------|-------------|
| **`Enter`** | Edit Parameter | Edit the parameter under cursor |
| **`q`** | Exit Config | Return to tree view |

### Mode Control

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Exit Histogram Mode | Return to Normal Mode (when in tree view) |

## Entering Histogram Mode

From Normal Mode, press **`h`** to enter Histogram Mode. You can also access it via Window Mode (**`w`** → **`h`**) which simultaneously enters Histogram Mode and focuses the histogram panel.

## Creating Histograms

### Basic Histogram Workflow

1. **Navigate to dataset** of interest
2. **Enter Histogram Mode** (**`h`**)
3. **Select dataset** (**`Enter`**) - configures histogram parameters
4. **Generate histogram** (**`h`**) - computes and displays the histogram
5. **Examine distribution** in histogram panel
6. **Optionally adjust settings** using direct key bindings

### Dataset Selection

**Select Dataset** (**`Enter`**)
- When focused on a dataset in the tree view, press **`Enter`** to select it
- Automatically configures histogram parameters for the selected dataset
- Sets default binning, labels, and scales
- Displays configuration in the histogram panel

### Histogram Generation

**Show Histogram** (**`h`**)
- Computes histogram using current configuration
- Displays histogram in an external window
- Uses automatic binning based on data characteristics
- Shows the histogram visualization alongside the TUI

**Save Histogram** (**`H`**)
- Computes histogram as above
- Prompts for filename
- Saves histogram to file (PNG, PDF, etc.)
- Allows you to preserve the analysis for later use

## Histogram Configuration

### Direct Configuration Bindings

Histogram Mode now provides direct key bindings for common configuration tasks, eliminating the need to enter a separate configuration mode for basic adjustments:

**Edit Number of Bins** (**`b`**)
- Directly edit the number of histogram bins
- Prompts for new bin count
- Updates configuration immediately
- No need to navigate to configuration window

**Toggle X-Scale** (**`x`**)
- Instantly toggle x-axis between linear and logarithmic scale
- Particularly useful for data spanning multiple orders of magnitude
- Shows updated scale in configuration display
- May show error if log scale is incompatible with data (negative/zero values)

**Toggle Y-Scale** (**`y`**)
- Toggle y-axis (frequency) between linear and logarithmic scale
- Useful when histogram bins have very different counts
- Reveals structure in low-frequency bins
- May show error if histogram contains zero counts with log scale

### Advanced Configuration Window

**Jump to Config** (**`J`**)
- Opens the full configuration window for advanced editing
- Allows editing of all parameters including labels and custom settings
- Navigate parameters with arrow keys
- Press **`Enter`** to edit parameter under cursor
- Press **`q`** to return to tree view

### Configurable Parameters

Key histogram parameters include:

**Binning Options**
- **Number of bins**: Control histogram resolution (editable with **`b`**)
- **Bin edges**: Automatically calculated based on scale and data range
- **Scale**: Linear or logarithmic binning (controlled by x-scale setting)

**Scale Settings**
- **X-axis scale**: Linear or logarithmic (toggle with **`x`**)
- **Y-axis scale**: Linear or logarithmic frequency scale (toggle with **`y`**)
- **Labels**: Dataset path used as default x-label (editable in config window)

### Configuration Reset

**Reset Configuration** (**`r`**)
- Restores all parameters to intelligent defaults
- Clears dataset selection
- Closes any open histogram windows
- Returns to clean state for new analysis

## Statistical Information

### Automatic Statistics

Every histogram displays key statistics:
- **Count**: Total number of data points
- **Mean**: Average value
- **Standard deviation**: Data spread
- **Min/Max**: Data range
- **Percentiles**: Quartiles and other percentiles

### Distribution Characteristics

Histograms reveal important data properties:
- **Normality**: Bell curve vs skewed distributions
- **Outliers**: Isolated bars at extremes
- **Multimodality**: Multiple peaks indicating subpopulations
- **Data quality**: Gaps, spikes, or unusual patterns

## Advanced Features

### Intelligent Binning

**Automatic Bin Selection**
- Uses statistical methods to choose optimal bin count
- Adapts to data distribution characteristics
- Balances resolution with noise reduction
- Works well for most datasets without manual tuning

**Custom Binning**
- Manual control over bin count for specific needs
- Custom bin edges for non-uniform binning
- Logarithmic binning for wide dynamic ranges
- Percentile-based binning for robust analysis

### Scale Options

**Linear vs Logarithmic Y-axis**
- Linear: Standard frequency counting
- Logarithmic: Better for wide frequency ranges
- Useful when some bins have very different counts
- Reveals structure in tail regions

**Data Range Control**
- Focus on specific value ranges
- Exclude outliers for better main distribution view
- Zoom into regions of interest
- Handle infinite or extreme values gracefully

### Large Dataset Handling

**Efficient Processing**
- Streaming algorithms for datasets larger than memory
- Progress indication for slow histogram computation
- Automatic subsampling when appropriate
- Maintains statistical accuracy

**Memory Management**
- Chunked processing for massive datasets
- Adaptive algorithms based on available memory
- No memory overflow even for very large files

## Data Compatibility

### Supported Data Types

**Numeric Data**
- All integer types: Exact bin placement
- Floating point types: Continuous distributions
- Complex numbers: Magnitude histograms by default

**Multidimensional Arrays**
- 1D arrays: Direct histogram
- Higher dimensions: Flattened by default
- Option to select specific dimensions or slices

### Special Data Handling

**Integer Data**
- Bin edges aligned with integer values when appropriate
- Exact counting for discrete distributions
- Special handling for boolean data (0/1 counts)

**Floating Point Data**
- Continuous distribution handling
- Appropriate precision for bin edges
- Special handling for NaN and infinite values

## Workflow Examples

### Quick Distribution Check
```
1. Navigate to dataset of interest
2. Press 'h' to enter Histogram Mode
3. Press 'Enter' to select the dataset
4. Press 'h' to generate and show histogram
5. Examine shape and statistics
6. Look for outliers or unexpected patterns
```

### Detailed Distribution Analysis
```
1. Navigate to dataset and enter Histogram Mode ('h')
2. Select dataset ('Enter')
3. Adjust bin count for better resolution ('b')
4. Toggle to logarithmic y-axis if needed ('y')
5. Toggle to logarithmic x-axis for wide ranges ('x')
6. Press 'h' to view updated histogram
7. Press 'H' to save analysis
```

### Advanced Configuration Workflow
```
1. Select dataset and generate basic histogram
2. Press 'J' to jump to configuration window
3. Navigate to parameter you want to edit
4. Press 'Enter' to modify the parameter
5. Press 'q' to return to tree view
6. Press 'h' to regenerate with new settings
```

### Quality Assessment Workflow
```
1. Select dataset and generate histogram
2. Check histogram for overall shape
3. Look for unexpected gaps or spikes
4. Try logarithmic scales ('x' or 'y') to reveal hidden structure
5. Adjust bin count ('b') for better resolution
6. Assess data completeness and quality
```

### Comparative Analysis
```
1. Navigate to first dataset
2. Enter Histogram Mode and select dataset ('h', 'Enter')
3. Generate histogram ('h') and note key characteristics
4. Navigate to related dataset (within Histogram Mode)
5. Select second dataset ('Enter')
6. Generate second histogram ('h')
7. Compare distributions visually and statistically
```

## Interpreting Histograms

### Distribution Shapes

**Normal Distribution**
- Bell-shaped curve
- Mean ≈ median
- Symmetric around center
- Most data within 2-3 standard deviations

**Skewed Distributions**
- Tail extending to one side
- Mean shifted toward tail
- Common in physical measurements
- May indicate underlying processes

**Multimodal Distributions**
- Multiple peaks
- Suggests mixed populations
- May indicate different physical regimes
- Worth investigating subgroups

### Quality Indicators

**Data Quality Issues**
- Sharp spikes: Possible default/error values
- Gaps: Missing data ranges or processing artifacts
- Extreme outliers: Data errors or interesting physics
- Unexpected shapes: Processing problems or discoveries

**Healthy Data Patterns**
- Smooth, continuous distributions
- Reasonable value ranges
- Expected statistical properties
- Consistent with known physics/processes

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

**Logarithmic Scale Errors**
- **Negative values with log x-scale**: Error message indicates data contains negative values incompatible with logarithmic x-axis
- **Zero values with log x-scale**: Error message indicates data contains zero values incompatible with logarithmic x-axis
- **Zero histogram counts with log y-scale**: Error message indicates some bins have zero counts, incompatible with logarithmic y-axis
- **Solution**: Switch back to linear scale or filter/transform data appropriately

**Extreme Values**
- Automatic handling of infinite values
- NaN value detection and reporting
- Robust binning even with outliers

### Recovery Strategies
- Use Dataset Mode to validate data first
- Check dataset metadata for expected properties
- Use configuration reset (**`r`**) to start fresh
- Try different binning strategies for problematic data
- For log scale issues, verify data is strictly positive before using logarithmic scales
- Consider transforming data (e.g., adding offset) if log scale is needed for non-positive data

## Integration with Other Modes

### Data Preparation
Use Dataset Mode before histogram analysis:
- Check basic statistics (mean, min/max)
- Validate data quality with value viewing
- Understand dataset structure and content

### Comparative Analysis
Combine with other modes:
- Use Jump Mode to find related datasets
- Generate multiple histograms for comparison
- Use Plotting Mode for correlation analysis

### Analysis Pipeline
```
Normal Mode → Navigate to dataset
Dataset Mode → Check basic statistics
Histogram Mode → Analyze distribution
Plotting Mode → Explore relationships
```

## Performance Considerations

### Large Dataset Strategies
- Automatic algorithms scale to dataset size
- Progress indication for long computations
- Memory-efficient chunked processing
- Option to subsample extremely large datasets

### Interactive Response
- Fast histogram updates for small datasets
- Progressive refinement for large datasets
- Real-time configuration preview when possible
- Cancellable operations for very slow computations

## Tips for Effective Analysis

!!! tip "Start Simple"
    Begin with default histogram settings, then refine configuration based on initial results. Use direct key bindings (**`b`**, **`x`**, **`y`**) for quick adjustments.

!!! tip "Bin Count Guidelines"
    For most datasets, automatic binning (50 bins) works well. Press **`b`** to adjust: increase bins for more detail, decrease for smoother curves.

!!! tip "Scale Selection"
    Use logarithmic y-axis (**`y`**) when frequency counts span several orders of magnitude. Use logarithmic x-axis (**`x`**) for data spanning wide ranges (e.g., 0.01 to 10000).

!!! tip "Direct Configuration"
    The new direct key bindings eliminate the need to open the configuration window for common adjustments. Use **`b`** for bins, **`x`** and **`y`** for scales, and only press **`J`** when you need to edit labels or other advanced parameters.

!!! warning "Outlier Impact"
    Extreme outliers can compress the main distribution. Consider focusing on specific ranges for better resolution.

!!! warning "Log Scale Constraints"
    Logarithmic scales require strictly positive values. The system will prevent you from using log scales with negative or zero data and display a clear error message.

## Statistical Best Practices

### Histogram Interpretation
- Consider sample size when interpreting shape
- Look for both central tendency and spread
- Pay attention to tail behavior
- Consider physical meaning of distribution shape

### Quality Assessment
- Check for data artifacts vs real features
- Validate unusual patterns with source data
- Consider measurement/simulation limitations
- Cross-reference with expected physics

## Next Steps

Histogram Mode complements other analysis tools:

- Use [Dataset Mode](dataset.md) for detailed statistical measures
- Combine with [Plotting Mode](plotting.md) for relationship analysis
- Use [Jump Mode](jump.md) to compare distributions across datasets
- Return to [Normal Mode](normal.md) for navigation and exploration

The combination of distribution analysis with other statistical and visualization tools provides comprehensive data understanding.