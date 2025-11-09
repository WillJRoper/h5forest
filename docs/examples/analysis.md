# Data Analysis Examples

This page demonstrates practical data analysis workflows using h5forest's Dataset Mode and statistical capabilities.

## Overview

Dataset Mode provides powerful tools for understanding your data:
- Value inspection (truncated and range-specific)
- Statistical analysis (min/max, mean, standard deviation)
- Quality assessment and validation
- Efficient handling of large datasets

## Basic Statistical Analysis

### Single Dataset Analysis

**Analyzing particle coordinates:**

1. **Navigate to particle coordinates:**
   ```
   /PartType0/Coordinates  
   Shape: (1000000, 3)
   ```

2. **Enter Dataset Mode:** Press **`d`**

3. **Get data range:** Press **`m`** for min/max
   ```
   Computing Min/Max...
   Min/Max ████████████████████████████████ 100%
   Minimum: [-50.123, -50.234, -50.345]
   Maximum: [49.876, 49.765, 49.654]
   ```

4. **Calculate center:** Press **`M`** for mean
   ```
   Computing Mean...
   Mean ████████████████████████████████ 100%
   Mean: [-0.123, 0.045, -0.091]
   ```

5. **Check distribution spread:** Press **`s`** for standard deviation
   ```
   Computing Standard Deviation...
   StDev ████████████████████████████████ 100%
   Standard Deviation: [28.912, 28.847, 28.934]
   ```

**Interpretation:**
- Data spans roughly -50 to +50 in all dimensions
- Slightly off-center (mean ≠ 0)
- Similar spread in all three dimensions

### Value Inspection Workflow

**Examining actual data values:**

1. **View sample values:** Press **`v`**
   ```
   [[-23.456  12.789  -8.123]
    [ 15.234  -6.789  23.456]
    [ -1.234   4.567  -9.012]
    ...
    
   Showing 1000/3000000 elements.
   ```

2. **Examine specific range:** Press **`V`**
   ```
   Enter range (start:end): 100:110
   ```
   Shows elements 100-109, useful for checking data patterns.

3. **Close values panel:** Press **`c`** to reclaim screen space

## Comparative Analysis

### Comparing Related Datasets

**Temperature vs Density analysis:**

1. **Analyze temperature first:**
   ```
   Navigate to: /PartType0/Temperature
   Dataset Mode: 'd'
   Min/Max: 'm' → Min: 10.5 K, Max: 10^6.7 K
   Mean: 'M' → Mean: 10^4.2 K
   ```

2. **Switch to density:**
   ```
   Exit Dataset Mode: 'q'
   Navigate to: /PartType0/Density  
   Dataset Mode: 'd'
   Min/Max: 'm' → Min: 10^-3, Max: 10^2 g/cm³
   Mean: 'M' → Mean: 1.2 g/cm³
   ```

3. **Note for correlation analysis:**
   - Both span several orders of magnitude
   - Suggests logarithmic relationship
   - Good candidates for scatter plot

### Cross-Particle Type Comparison

**Comparing masses between particle types:**

1. **Gas particle masses:**
   ```
   /PartType0/Masses
   Min/Max → Min: 1.2e-6, Max: 1.2e-6 M_sun
   Mean → 1.2e-6 M_sun
   ```
   *Result: Uniform gas particle masses*

2. **Dark matter masses:**
   ```
   /PartType1/Masses  
   Min/Max → Min: 6.8e-6, Max: 6.8e-6 M_sun
   Mean → 6.8e-6 M_sun
   ```
   *Result: Uniform DM masses, ~5.7x heavier than gas*

## Quality Assessment Workflows

### Data Validation Pipeline

**Systematic quality checking:**

1. **Check metadata consistency:**
   ```
   Navigate to dataset
   Verify: Shape, datatype, compression
   Check: Attributes for units, description
   ```

2. **Validate value ranges:**
   ```
   Dataset Mode: 'd'
   Min/Max: 'm' → Check for reasonable ranges
   Sample values: 'v' → Look for obvious errors
   ```

3. **Look for common issues:**
   - **Extreme outliers:** Min/max values outside physical ranges
   - **Default values:** Suspicious repeating values (0.0, -1.0, etc.)
   - **NaN/Inf:** Statistical operations will report these
   - **Unit consistency:** Check attribute units vs value ranges

### Outlier Detection

**Finding problematic data points:**

1. **Get overall statistics:**
   ```
   Temperature dataset:
   Min: 0.1 K (suspicious - too cold?)
   Max: 10^8 K (suspicious - too hot?)
   Mean: 10^4 K  
   StdDev: 10^3 K
   ```

2. **Investigate extreme values:**
   ```
   Range viewing: 'V'
   Check first 100: 0:100
   Check last 100: -100:
   Look for patterns in extreme values
   ```

3. **Assessment:**
   - Minimum might indicate unphysical cooling
   - Maximum might indicate numerical instability
   - Bulk of data likely in reasonable range

## Large Dataset Strategies

### Efficient Analysis of Massive Arrays

**Handling multi-GB datasets:**

1. **Start with metadata:**
   ```
   /LargeDataset/Positions
   Shape: (100000000, 3)  # 100M particles
   Memory: 1.1 GB
   Compression: gzip
   ```

2. **Use chunked statistics:**
   ```
   Min/Max: 'm' → Progress bar shows chunked processing
   Progress: Min/Max ████████████████ 65% (shows real-time progress)
   ```

3. **Sample before full analysis:**
   ```
   Range viewing: 'V' → 0:10000 (check first 10k elements)
   Verify reasonable values before computing expensive statistics
   ```

### Memory-Conscious Workflows

**Strategies for memory-limited systems:**

1. **Statistics before values:**
   - Get min/max, mean first (streaming algorithms)
   - Use range viewing instead of full value display
   - Compute statistics separately, not simultaneously

2. **Selective analysis:**
   - Focus on specific data ranges of interest
   - Use Dataset Mode range viewing for large arrays
   - Avoid displaying values for very large datasets

## Advanced Analysis Patterns

### Multi-Step Analysis

**Comprehensive dataset characterization:**

1. **Basic properties:**
   ```
   Shape: (N, dimensions)
   Type: float32/float64/int32 etc.
   Memory: Compressed size
   ```

2. **Value distribution:**
   ```
   Min/Max: Data range and potential outliers
   Mean: Central tendency
   StdDev: Data spread and variability
   ```

3. **Quality assessment:**
   ```
   Sample values: Representative data inspection
   Range checks: Validate specific regions
   Physical reasoning: Do values make sense?
   ```

4. **Preparation for visualization:**
   - Use statistics to guide plotting ranges
   - Identify interesting relationships
   - Note logarithmic vs linear scaling needs

### Error Investigation

**When statistics reveal problems:**

1. **Unexpected ranges:**
   ```
   Example: Negative masses detected
   Min/Max shows: Min: -1.2e-6, Max: 1.2e-6
   Investigation: Range view negative values
   Action: Check data processing pipeline
   ```

2. **Statistical anomalies:**
   ```
   Example: Mean >> Median (highly skewed)
   Mean: 1000, but most values near 10
   Investigation: Look for extreme outliers
   Action: Consider outlier removal or different analysis
   ```

## Workflow Efficiency Tips

### Rapid Assessment Protocol

**Quick data characterization (< 2 minutes per dataset):**

1. **Metadata scan** (5 seconds)
2. **Min/Max check** (10-30 seconds)
3. **Value sample** (5 seconds)  
4. **Mean calculation** (if needed, 10-30 seconds)
5. **Decision point:** Detailed analysis or move on

### Batch Analysis Strategy

**Systematic multi-dataset analysis:**

1. **Survey phase:**
   - Navigate through all datasets
   - Note shapes, types, compression
   - Identify priority datasets

2. **Analysis phase:**
   - Focus on key datasets first
   - Use Jump Mode to navigate efficiently between related datasets
   - Document findings for each dataset

3. **Comparison phase:**
   - Compare statistics across related datasets
   - Note relationships and correlations
   - Identify candidates for visualization

## Integration with Visualization

### Preparing Data for Plotting

**Statistical analysis informs visualization choices:**

1. **Range-based decisions:**
   ```
   Temperature: Min: 10 K, Max: 10^6 K
   → Use logarithmic scale for plotting
   
   Coordinates: Min: -50, Max: 50
   → Linear scale appropriate
   ```

2. **Correlation candidates:**
   ```
   High-variance datasets make good scatter plot axes
   Similar value ranges suggest direct comparison potential
   ```

3. **Distribution analysis:**
   ```
   Large standard deviation → Good for histogram analysis
   Narrow ranges → May need different visualization approach
   ```

## Troubleshooting Common Issues

### Performance Problems

**Slow statistical calculations:**
- Check dataset size (Shape in metadata)
- Allow time for chunked processing of large data
- Consider using range viewing for initial assessment

**Memory errors:**
- Use statistics (streaming) instead of value viewing
- Analyze subsets with range viewing
- Close unnecessary panels to free memory

### Data Interpretation

**Unexpected statistical results:**
- Verify units in attributes
- Check for data preprocessing (scaling, transformations)
- Consider physical/logical reasonableness
- Use value viewing to validate statistical results

## Next Steps

After mastering Dataset Mode analysis:

- Explore [Visualization Examples](visualization.md) for plotting workflows
- Check [Navigation Examples](navigation.md) for efficient file exploration
- Review the complete [Dataset Mode Reference](../modes/dataset.md)

Statistical analysis provides the foundation for all other data exploration in h5forest!