# Basic Navigation Examples

This page provides practical examples of navigating HDF5 files with h5forest, covering common scenarios and useful techniques.

## Example File Structure

For these examples, we'll use a simulated HDF5 file with this structure:

```
simulation_output.h5
├── Header/
│   ├── NumPart_Total
│   ├── BoxSize
│   └── attributes: (units, simulation_code, etc.)
├── PartType0/  (Gas particles)
│   ├── Coordinates
│   ├── Velocities  
│   ├── Masses
│   ├── Temperature
│   └── Density
├── PartType1/  (Dark matter)
│   ├── Coordinates
│   ├── Velocities
│   └── Masses
└── Analysis/
    ├── Profiles/
    │   ├── Radius
    │   ├── Density_Profile
    │   └── Temperature_Profile
    └── Statistics/
        ├── Total_Mass
        └── Center_of_Mass
```

## Basic Tree Navigation

### Opening and Initial Exploration

```bash
h5forest simulation_output.h5
```

Upon opening, you'll see:
```
▼ simulation_output
  ▶ Header
  ▶ PartType0
  ▶ PartType1
  ▶ Analysis
```

The root is automatically expanded, showing top-level groups with collapse/expand arrows (▶/▼).

### Expanding Groups

**Expand the Header group:**
1. Navigate to `Header` using arrow keys
2. Press **`Enter`** to expand

Result:
```
▼ simulation_output
  ▼ Header
    • NumPart_Total
    • BoxSize
  ▶ PartType0
  ▶ PartType1
  ▶ Analysis
```

Datasets are shown without arrows (•), groups with arrows (▶/▼).

### Fast Movement Through Large Sections

**Skip quickly through particle data:**
1. Navigate to `PartType0`
2. Press **`}`** to jump down 10 lines
3. Press **`{`** to jump back up 10 lines

This is useful when files have hundreds of datasets.

## Exploring Particle Data

### Gas Particle Analysis

**Examine gas particle datasets:**

1. **Navigate to PartType0 and expand:**
   ```
   ▼ PartType0
     • Coordinates
     • Velocities
     • Masses
     • Temperature
     • Density
   ```

2. **Check coordinate metadata:**
   - Select `Coordinates`
   - Metadata panel shows:
     ```
     Dataset:            /PartType0/Coordinates
     Shape:              (1000000, 3)
     Datatype:           float32
     Compressed Memory:  11.4 MB
     Compression:        gzip
     ```

3. **Examine attributes:**
   - Attributes panel might show:
     ```
     units: kpc
     description: Comoving coordinates
     ```

### Comparing Particle Types

**Navigate between particle types efficiently:**

1. **Current position:** `/PartType0/Coordinates`
2. **Enter Jump Mode:** Press **`j`**
3. **Jump to parent:** Press **`p`** (now at `/PartType0/`)
4. **Next sibling:** Press **`n`** (now at `/PartType1/`)
5. **Exit Jump Mode:** Press **`q`**
6. **Expand PartType1:** Press **`Enter`**
7. **Navigate to Coordinates:** Use arrow keys

This efficiently moves between related structures.

## Deep Hierarchy Navigation

### Nested Analysis Results

**Navigate to nested analysis data:**

1. **Go to Analysis group:**
   - Use arrow keys or Jump Mode (**`j`** → **`k`** → type "analysis")

2. **Expand Analysis:**
   ```
   ▼ Analysis
     ▶ Profiles
     ▶ Statistics
   ```

3. **Explore Profiles:**
   - Navigate to `Profiles` and press **`Enter`**
   ```
   ▼ Analysis
     ▼ Profiles
       • Radius
       • Density_Profile  
       • Temperature_Profile
     ▶ Statistics
   ```

### Using Jump Mode for Deep Navigation

**Quick access to deeply nested data:**

1. **Enter Jump Mode:** **`j`**
2. **Search for profile data:** **`k`** → type "profile"
3. **Jump to first match:** Automatically moves to `Density_Profile`
4. **Continue search:** Press **`k`** again to find `Temperature_Profile`

## Attribute-Heavy Navigation

### Files with Extensive Metadata

Some HDF5 files have rich attribute documentation:

1. **Navigate to Header group**
2. **Expand attributes panel:** Press **`A`**
3. **Focus on attributes:** Press **`w`** → **`a`**
4. **Scroll through attributes:** Use arrow keys

The expanded layout gives more space for complex metadata:
```
┌─────────────┬─────────────────────┐
│    Tree     │     Attributes      │
├─────────────┤  units: kpc         │
│  Metadata   │  simulation: EAGLE  │
│             │  version: 2.0.1     │
│             │  created: 2024-01-15│
│             │  contact: user@edu  │
└─────────────┴─────────────────────┘
```

## Efficient Exploration Patterns

### Systematic File Survey

**Complete file structure overview:**

1. **Start at root:** Jump Mode **`j`** → **`t`**
2. **Expand all top-level groups:** 
   - Navigate to each group
   - Press **`Enter`** to expand
3. **Survey each section:**
   - Use **`{`** and **`}`** for quick scanning
   - Note interesting datasets for later analysis
4. **Document structure:**
   - Check group attributes for documentation
   - Note dataset shapes and types

### Targeted Dataset Discovery

**Finding specific data types:**

1. **Search for coordinates:** Jump Mode **`j`** → **`k`** → "coord"
2. **Search for temperatures:** **`k`** → "temp"  
3. **Search for masses:** **`k`** → "mass"

This quickly locates similar datasets across different groups.

### Quality Check Navigation

**Rapid data validation workflow:**

1. **Navigate to dataset of interest**
2. **Check basic metadata** (shape, type, compression)
3. **Enter Dataset Mode:** **`d`**
4. **Quick value check:** **`v`**
5. **Return to navigation:** **`q`**
6. **Move to next dataset**

## Navigation Shortcuts Reference

### Essential Movement
- **`↑`/`↓`** or **`k`/`j`**: Line-by-line movement
- **`{`/`}`**: Jump 10 lines up/down
- **`Enter`**: Expand/collapse groups

### Quick Positioning  
- **`j`** → **`t`**: Jump to top (root)
- **`j`** → **`b`**: Jump to bottom
- **`j`** → **`p`**: Jump to parent group
- **`j`** → **`n`**: Next item at same level

### Search and Discovery
- **`j`** → **`k`** → text: Find items containing text
- **`A`**: Toggle expanded attributes
- **`w`** → **`a`**: Focus on attributes panel

## Common Navigation Mistakes

### Inefficient Patterns

**❌ Don't:**
- Manually navigate through every single item
- Expand everything at once in large files
- Forget to use Jump Mode for repositioning
- Ignore the attributes panel for documentation

**✅ Do:**
- Use **`{`** and **`}`** for quick scanning
- Use Jump Mode search (**`k`**) to find specific items
- Expand groups selectively
- Check attributes for important metadata
- Use parent/sibling jumps for related structures

### Performance Tips

**For Large Files:**
- Avoid expanding all groups simultaneously
- Use search instead of manual browsing
- Focus on specific sections of interest
- Let lazy loading work efficiently

**For Complex Hierarchies:**
- Use Jump Mode parent navigation (**`p`**)
- Map out structure before deep diving
- Use expanded attributes (**`A`**) for documentation

## Next Steps

Once comfortable with navigation:

- Try [Data Analysis Examples](analysis.md) for statistical workflows
- Explore [Visualization Examples](visualization.md) for plotting
- Check the [Mode Reference](../modes/overview.md) for complete keyboard shortcuts

Efficient navigation is the foundation for all other h5forest operations!