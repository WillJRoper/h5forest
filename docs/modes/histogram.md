# Histogram Mode

Histogram Mode provides tools for generating histograms and analyzing data distributions. It enables exploration of statistical properties, data quality assessment, and distribution visualization for HDF5 datasets.

## Purpose

Histogram Mode is designed for:
- Creating histograms to understand data distributions
- Analyzing statistical properties of datasets
- Quality assessment and outlier detection
- Comparing distributions across related datasets

## Keyboard Reference

### Histogram Generation

| Key | Action | Description |
|-----|--------|-------------|
| **`h`** | Generate Histogram | Create histogram from dataset under cursor |
| **`H`** | Generate and Save | Create histogram and save to file |

### Configuration

| Key | Action | Description |
|-----|--------|-------------|
| **`e`** | Edit Configuration | Open histogram configuration editor (when parameters available) |
| **`Enter`** | Edit Parameter | Edit the parameter under cursor (when in config mode) |
| **`r`** | Reset Configuration | Reset histogram configuration to defaults |

### Mode Control

| Key | Action | Description |
|-----|--------|-------------|
| **`q`** | Exit Histogram Mode | Return to Normal Mode or exit configuration |

## Entering Histogram Mode

From Normal Mode, press **`h`** to enter Histogram Mode. You can also access it via Window Mode (**`w`** → **`h`**) which simultaneously enters Histogram Mode and focuses the histogram panel.

## Creating Histograms

### Basic Histogram Workflow

1. **Navigate to dataset** of interest
2. **Enter Histogram Mode** (**`h`**)
3. **Generate histogram** (**`h`**) - automatically uses current dataset
4. **Examine distribution** in histogram panel
5. **Optionally configure** and regenerate

### Automatic Dataset Selection

When you press **`h`** to generate a histogram:
- Uses the dataset currently under the cursor
- No need for explicit selection (unlike Plotting Mode)
- Immediate histogram generation for quick analysis
- Works with any numeric dataset

### Histogram Generation

**Generate Histogram** (**`h`**)
- Creates histogram of the currently selected dataset
- Uses automatic binning based on data characteristics
- Displays histogram in the histogram panel
- Shows basic statistics alongside the histogram

**Generate and Save** (**`H`**)
- Creates histogram as above
- Prompts for filename
- Saves histogram to file (PNG, PDF, etc.)
- Includes statistical summary in saved output

## Histogram Configuration

### Configuration Editor

**Edit Configuration** (**`e`**)
- Opens interactive configuration editor
- Shows adjustable histogram parameters
- Allows customization of appearance and analysis
- Updates histogram in real-time when possible

### Configurable Parameters

Key histogram parameters include:

**Binning Options**
- **Number of bins**: Control histogram resolution
- **Bin edges**: Manual bin boundary specification
- **Binning method**: Automatic, fixed-width, or percentile-based

**Scale and Range**
- **Y-axis scale**: Linear or logarithmic frequency scale
- **X-axis range**: Focus on specific data ranges
- **Normalization**: Raw counts, density, or probability

**Visual Appearance**
- **Bar style**: Filled bars, outlines, or step plots
- **Color scheme**: Color coding options
- **Transparency**: Alpha channel for overlapping histograms

### Parameter Editing

**Edit Parameter** (**`Enter`**)
- Edits the parameter currently under cursor
- Toggle options (like linear/log scale) with simple selection
- Numeric parameters (bin count, ranges) accept typed input
- Real-time preview when computationally feasible

**Reset Configuration** (**`r`**)
- Restores all parameters to intelligent defaults
- Preserves dataset selection
- Useful when configuration becomes too complex

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
3. Press 'h' to generate histogram
4. Examine shape and statistics
5. Look for outliers or unexpected patterns
```

### Detailed Distribution Analysis
```
1. Generate basic histogram as above
2. Press 'e' to edit configuration
3. Adjust bin count for better resolution
4. Set logarithmic y-axis if needed
5. Focus on specific data range
6. Press 'H' to save analysis
```

### Quality Assessment Workflow
```
1. Check histogram for overall shape
2. Look for unexpected gaps or spikes
3. Examine min/max values for outliers
4. Check mean/median relationship
5. Assess data completeness and quality
```

### Comparative Analysis
```
1. Generate histogram for first dataset
2. Note key statistics and shape
3. Navigate to related dataset
4. Generate second histogram
5. Compare distributions visually and statistically
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

**Extreme Values**
- Automatic handling of infinite values
- NaN value detection and reporting
- Robust binning even with outliers

### Recovery Strategies
- Use Dataset Mode to validate data first
- Check dataset metadata for expected properties
- Use configuration reset (**`r`**) to start fresh
- Try different binning strategies for problematic data

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
    Begin with default histogram settings, then refine configuration based on initial results.

!!! tip "Bin Count Guidelines"
    For most datasets, automatic binning works well. Increase bins for more detail, decrease for smoother curves.

!!! tip "Scale Selection"
    Use logarithmic y-axis when frequency counts span several orders of magnitude.

!!! warning "Outlier Impact"
    Extreme outliers can compress the main distribution. Consider focusing on specific ranges for better resolution.

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