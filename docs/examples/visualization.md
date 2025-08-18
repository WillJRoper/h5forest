# Visualization Examples

This page demonstrates creating effective visualizations using h5forest's Plotting and Histogram modes for data exploration and analysis.

## Overview

h5forest provides two main visualization tools:
- **Plotting Mode**: Scatter plots for exploring relationships between variables
- **Histogram Mode**: Distribution analysis for understanding data characteristics

Both modes integrate seamlessly with Dataset Mode statistical analysis for comprehensive data exploration.

## Basic Scatter Plots

### Creating Your First Plot

**Temperature vs Density relationship:**

1. **Navigate to temperature data:**
   ```
   /PartType0/Temperature
   Shape: (1000000,)
   ```

2. **Enter Plotting Mode:** Press **`p`**

3. **Select X-axis:** Press **`x`** (assigns Temperature as x-axis)

4. **Navigate to density:** 
   ```
   /PartType0/Density
   Shape: (1000000,)
   ```

5. **Select Y-axis:** Press **`y`** (assigns Density as y-axis)

6. **Generate plot:** Press **`p`**

**Result:** Scatter plot appears in plot panel showing Temperature-Density relationship, likely revealing the expected correlation between these physical quantities.

### Multi-Dimensional Data Plotting

**Position analysis (3D coordinates → 2D plot):**

1. **Navigate to coordinates:**
   ```
   /PartType0/Coordinates
   Shape: (1000000, 3)  # 3D positions
   ```

2. **Enter Plotting Mode:** **`p`**

3. **Select X-axis:** **`x`** (uses first column - X coordinates)

4. **Navigate to same dataset for Y-axis:** Stay on Coordinates

5. **Select Y-axis:** **`y`** (uses second column - Y coordinates)

6. **Plot:** **`p`**

**Result:** 2D projection of particle positions, showing spatial distribution in the X-Y plane.

## Advanced Plot Configuration

### Logarithmic Scaling

**For wide dynamic range data:**

1. **Create basic Temperature vs Density plot** (as above)

2. **Enter configuration mode:** Press **`e`**

3. **Configure X-axis scale:**
   ```
   Configuration Panel:
   ▶ X-axis scale: Linear    ← cursor here
     Y-axis scale: Linear
     Point size: 1.0
     Alpha: 0.6
   ```

4. **Edit parameter:** Press **`Enter`** → Toggle to "Logarithmic"

5. **Configure Y-axis scale:** Navigate down, **`Enter`** → "Logarithmic"

6. **Apply configuration:** Press **`q`** to exit config mode

7. **Regenerate plot:** Press **`p`**

**Result:** Log-log plot revealing power-law relationships that might be hidden in linear scaling.

### Visual Customization

**Optimizing plot appearance for dense data:**

1. **Open configuration:** **`e`**

2. **Adjust point properties:**
   ```
   Configuration:
     X-axis scale: Linear
     Y-axis scale: Linear  
   ▶ Point size: 1.0        ← Reduce to 0.5 for dense data
     Alpha: 0.6             ← Reduce to 0.3 for transparency
   ```

3. **Edit each parameter:** Use **`Enter`** to modify values

4. **Reset if needed:** Press **`r`** to restore defaults

5. **Generate final plot:** Press **`p`**

## Histogram Analysis

### Basic Distribution Analysis

**Understanding particle velocities:**

1. **Navigate to velocity data:**
   ```
   /PartType0/Velocities  
   Shape: (1000000, 3)
   ```

2. **Enter Histogram Mode:** Press **`h`**

3. **Generate histogram:** Press **`h`** (automatically uses current dataset)

**Result:** Histogram showing velocity distribution, likely revealing Maxwell-Boltzmann or similar physical distribution.

### Histogram Configuration

**Customizing distribution analysis:**

1. **Generate basic histogram** (as above)

2. **Enter configuration:** Press **`e`**

3. **Adjust binning:**
   ```
   Configuration:
   ▶ Number of bins: 50     ← Increase to 100 for more detail
     Y-axis scale: Linear   ← Try Logarithmic for tail analysis
     Normalization: Count   ← Options: Count, Density, Probability
   ```

4. **Edit parameters:** Use **`Enter`** for each setting

5. **Regenerate:** Press **`h`**

**Result:** Higher resolution histogram with better tail visibility and appropriate normalization.

## Comprehensive Analysis Workflows

### Physical Relationship Exploration

**Investigating galaxy formation physics:**

1. **Temperature-Density Phase Diagram:**
   ```
   X-axis: /PartType0/Density (log scale)
   Y-axis: /PartType0/Temperature (log scale)
   Configuration: Alpha=0.1 (for overdense regions)
   Result: Reveals equation of state, phase structure
   ```

2. **Spatial Distribution:**
   ```
   X-axis: /PartType0/Coordinates (column 0)
   Y-axis: /PartType0/Coordinates (column 1)  
   Configuration: Point size=0.5
   Result: Shows large-scale structure, clustering
   ```

3. **Velocity Distribution:**
   ```
   Histogram: /PartType0/Velocities
   Configuration: 100 bins, log y-axis
   Result: Thermal + bulk motion components
   ```

### Data Quality Assessment

**Systematic visualization-based quality checks:**

1. **Range Validation Plots:**
   ```
   Plot: Index vs Value (using range viewing)
   Purpose: Check for systematic trends or jumps
   
   Plot coordinates:
   X-axis: Array index (0, 1, 2, ...)
   Y-axis: Data values
   Look for: Discontinuities, systematic drifts
   ```

2. **Distribution Shape Analysis:**
   ```
   Histogram: Each key dataset
   Look for: 
   - Unexpected gaps or spikes
   - Multiple peaks (contamination?)
   - Extreme outliers
   - Non-physical values
   ```

### Comparative Analysis

**Multi-dataset comparison workflow:**

1. **Generate reference plot/histogram**

2. **Document key characteristics:**
   - Value ranges, distribution shape
   - Notable features or anomalies
   - Physical interpretation

3. **Navigate to comparison dataset:**
   ```
   Use Jump Mode: 'j' → 'k' → search for similar datasets
   Or systematic navigation through related groups
   ```

4. **Generate comparison visualization:**
   - Same plot configuration for consistent comparison
   - Note differences in ranges, shapes, features

5. **Physical interpretation:**
   - Expected similarities/differences?
   - Evidence for different physical processes?
   - Data quality variations?

## Specialized Visualization Techniques

### Large Dataset Strategies

**Effective visualization of massive datasets:**

1. **Automatic Subsampling:**
   ```
   h5forest automatically subsamples very large datasets
   Maintains statistical properties while ensuring interactivity
   Progress bars indicate when subsampling occurs
   ```

2. **Density Visualization:**
   ```
   Configuration: Alpha = 0.05-0.1
   Purpose: Reveal density structure in overcrowded plots
   
   Alternative: Use histogram for 1D density analysis
   ```

3. **Focus Regions:**
   ```
   Use Dataset Mode range viewing first:
   'V' → specify interesting range (e.g., 1000:2000)
   Then create plots from subset
   Allows detailed examination of specific regions
   ```

### Multi-Component Analysis

**Analyzing data with multiple components:**

1. **Component Separation:**
   ```
   Example: 3D velocities
   Plot 1: Vx vs Vy (transverse motion)
   Plot 2: Vz vs |V| (bulk vs random motion)
   Plot 3: |V| histogram (speed distribution)
   ```

2. **Cross-Variable Relationships:**
   ```
   Position-dependent properties:
   Plot 1: Radius vs Density
   Plot 2: Radius vs Temperature  
   Plot 3: Density vs Temperature (phase diagram)
   ```

## Saving and Documentation

### Creating Publication-Quality Figures

**Workflow for high-quality output:**

1. **Optimize configuration:**
   - Appropriate scaling (linear/log)
   - Suitable point size and transparency
   - Clear, interpretable parameter ranges

2. **Generate and save:**
   ```
   Plotting Mode: 'P' (capital P)
   Histogram Mode: 'H' (capital H)
   Enter filename: analysis_temp_density.png
   ```

3. **Saved output includes:**
   - High-resolution figure
   - Automatic axis labels from dataset names/paths
   - Statistical information (for histograms)

### Documentation Workflow

**Systematic analysis documentation:**

1. **For each visualization:**
   - Record dataset paths and shapes
   - Note configuration parameters used
   - Document key findings and interpretations

2. **Analysis log example:**
   ```
   Temperature-Density Phase Diagram:
   - X: /PartType0/Density, log scale, range: 10^-3 to 10^2
   - Y: /PartType0/Temperature, log scale, range: 10^1 to 10^6
   - Config: Alpha=0.1, Point size=0.5
   - Finding: Clear equation of state, T ∝ ρ^0.6
   - Physics: Consistent with adiabatic compression
   ```

## Troubleshooting Visualizations

### Common Plot Issues

**Empty or strange plots:**
- **Check data compatibility:** Ensure both datasets have compatible shapes
- **Verify data ranges:** Use Dataset Mode min/max to check for reasonable values
- **Check for NaN/Inf:** Statistical analysis will reveal problematic values

**Overcrowded plots:**
- **Reduce point size:** Configuration → Point size < 1.0
- **Increase transparency:** Configuration → Alpha < 0.5
- **Consider subsampling:** Use Dataset Mode range viewing for subset analysis

**Poor scaling:**
- **Try logarithmic scales:** Configuration → X/Y-axis scale → Logarithmic
- **Check value ranges:** Wide ranges often benefit from log scaling
- **Custom ranges:** Focus on specific value ranges of interest

### Histogram Issues

**Poor resolution:**
- **Increase bin count:** Configuration → Number of bins
- **Check data range:** Ensure interesting range is captured
- **Consider log scaling:** Y-axis log scale for wide frequency ranges

**Interpretation difficulties:**
- **Try different normalizations:** Count vs Density vs Probability
- **Check for outliers:** Extreme values can compress main distribution
- **Validate with Dataset Mode:** Confirm histogram with statistical analysis

## Integration with Statistical Analysis

### Analysis-Informed Visualization

**Using Dataset Mode results to guide visualization:**

1. **Get value ranges first:**
   ```
   Dataset Mode: 'd' → 'm' (min/max)
   Use ranges to choose appropriate scaling
   ```

2. **Check distribution shape:**
   ```
   Dataset Mode: 'M' (mean), 's' (standard deviation)
   If mean >> median: expect skewed distribution
   Large std dev: expect wide histogram spread
   ```

3. **Validate visualizations:**
   ```
   Compare plot/histogram features with statistical measures
   Ensure visualizations accurately represent the statistics
   ```

## Next Steps

Master visualization by:

- Practice with the [complete mode references](../modes/plotting.md)
- Combine with [statistical analysis examples](analysis.md)
- Apply to your own data following these patterns
- Explore the relationship between statistics and visual features

Effective visualization reveals patterns that statistics alone might miss, while statistical analysis validates and quantifies what visualizations suggest!