# Frequently Asked Questions

Common questions and solutions for h5forest users.

## Installation and Setup

### Q: h5forest won't start - "command not found"

**A:** Ensure h5forest is properly installed:

```bash
# Check if installed
which h5forest

# If not found, install or reinstall
pip install h5forest

# Or if installed with --user flag
pip install --user h5forest
export PATH=$PATH:~/.local/bin
```

### Q: Import errors when starting h5forest

**A:** Check that all dependencies are installed:

```bash
# Check for missing dependencies
python -c "import h5py, numpy, prompt_toolkit, matplotlib"

# If any fail, reinstall h5forest
pip install --upgrade h5forest
```

### Q: h5forest displays incorrectly in my terminal

**A:** h5forest requires a modern terminal with Unicode support:

- **Recommended terminals:** iTerm2 (macOS), Windows Terminal, modern Linux terminals
- **Check Unicode support:** Ensure your terminal displays Unicode characters correctly
- **Font issues:** Use a monospace font with good Unicode coverage
- **Color support:** Enable 256-color support in your terminal

## File Compatibility

### Q: "Permission denied" or "File not found" errors

**A:** Common file access issues:

```bash
# Check file exists and is readable
ls -la /path/to/your/file.h5

# Check file permissions
chmod 644 /path/to/your/file.h5

# Ensure HDF5 file is valid
h5dump -H /path/to/your/file.h5
```

### Q: h5forest won't open my HDF5 file

**A:** Verify file format and integrity:

1. **Check if it's a valid HDF5 file:**
   ```bash
   file /path/to/your/file.h5
   # Should show: "Hierarchical Data Format (version 5) data"
   ```

2. **Test with standard tools:**
   ```bash
   h5ls /path/to/your/file.h5
   # Should list top-level groups/datasets
   ```

3. **Check for corruption:**
   ```bash
   h5check /path/to/your/file.h5
   ```

### Q: Large files are slow to open

**A:** This is expected behavior - h5forest uses lazy loading:

- **Initial loading:** Only the root level is read immediately
- **Group expansion:** Children are loaded on-demand when you expand groups
- **Performance:** Even multi-GB files should open quickly at the root level
- **If still slow:** Check available memory and disk I/O

## Navigation and Interface

### Q: I'm lost in a deep hierarchy - how do I get back to the root?

**A:** Use Jump Mode navigation:

```
Press 'j' (enter Jump Mode)
Press 't' (jump to top/root)
Press 'q' (exit Jump Mode)
```

### Q: The interface looks cramped - can I adjust panel sizes?

**A:** Use these interface controls:

- **`A`** - Toggle expanded attributes panel
- **`w`** → **`a`** - Focus attributes panel for scrolling
- **`c`** (in Dataset Mode) - Close values panel
- **Window Mode (`w`)** - Manage panel focus

### Q: Keyboard shortcuts aren't working

**A:** Check mode and focus:

1. **Verify current mode:** Look at the hotkey display at the bottom
2. **Check panel focus:** Some shortcuts only work in specific panels
3. **Mode conflicts:** Exit current mode with **`q`** and try again
4. **Terminal issues:** Ensure your terminal isn't intercepting key combinations

## Data Analysis

### Q: Statistical calculations are very slow

**A:** This is normal for large datasets:

- **Progress bars:** h5forest shows progress for time-intensive operations
- **Chunked processing:** Large datasets are processed in chunks to prevent memory overflow
- **Can be interrupted:** Use **`Ctrl+C`** to cancel if needed
- **Patience:** Multi-GB datasets may take several minutes for full statistics

### Q: Min/max shows unexpected values

**A:** Check for data quality issues:

1. **Verify data type:** Check metadata panel for correct data type
2. **Check for outliers:** Use Dataset Mode value viewing (**`v`**) to sample data
3. **Units:** Check attributes for unit information
4. **Processing artifacts:** Compare with known data characteristics

### Q: "Unable to compute statistics" errors

**A:** Common causes and solutions:

- **Non-numeric data:** Statistics only work on numeric datasets
- **Empty datasets:** Zero-length arrays can't have statistics computed
- **Memory limitations:** Very large datasets might exceed available memory
- **Data corruption:** Try with a different, known-good file

## Visualization

### Q: Plots are empty or show strange patterns

**A:** Troubleshoot plot issues:

1. **Check data compatibility:**
   ```
   Verify both datasets have compatible shapes
   Use Dataset Mode to check value ranges
   ```

2. **Scale issues:**
   ```
   Try logarithmic scaling for wide value ranges
   Check for negative values with log scales
   ```

3. **Data range:**
   ```
   Use min/max statistics to verify reasonable ranges
   Check for NaN or infinite values
   ```

### Q: Histograms look wrong or uninformative

**A:** Optimize histogram parameters:

- **Bin count:** Adjust number of bins in configuration (**`e`**)
- **Scaling:** Try logarithmic y-axis for wide frequency ranges
- **Range:** Focus on specific data ranges if outliers dominate
- **Normalization:** Try different normalization options (count vs density)

### Q: Can't save plots or histograms

**A:** Check save functionality:

1. **Use correct key:** **`P`** (capital) for plots, **`H`** (capital) for histograms
2. **File permissions:** Ensure write permissions in current directory
3. **Filename:** Provide valid filename when prompted
4. **Dependencies:** Ensure matplotlib is properly installed

## Performance

### Q: h5forest uses too much memory

**A:** Memory optimization strategies:

1. **Avoid expanding all groups:** Only expand what you need to examine
2. **Use statistics instead of values:** Statistics use streaming algorithms
3. **Range viewing:** Use Dataset Mode **`V`** instead of **`v`** for large datasets
4. **Close panels:** Use **`c`** to close values panel when not needed

### Q: Operations freeze or become unresponsive

**A:** Recovery options:

1. **Wait for completion:** Check for progress bars indicating ongoing operations
2. **Interrupt operations:** **`Ctrl+C`** to cancel statistical calculations
3. **Force quit:** **`Ctrl+Q`** to exit h5forest immediately
4. **Terminal reset:** If display is corrupted, restart terminal

## Advanced Usage

### Q: How do I analyze specific slices of multidimensional arrays?

**A:** Use Dataset Mode range viewing:

```
Navigate to multidimensional dataset
Press 'd' (Dataset Mode)
Press 'V' (range viewing)
Enter slice notation: 1000:2000 (elements 1000-1999)
```

Note: Currently supports 1D slicing - full multidimensional slicing is a planned feature.

### Q: Can h5forest handle compressed datasets?

**A:** Yes, h5forest handles HDF5 compression transparently:

- **Automatic decompression:** All compression types supported by h5py
- **Performance:** Compressed data may be slower to access
- **Memory usage:** Decompression happens in chunks to manage memory
- **Statistics:** Work normally on compressed data

### Q: How do I compare datasets across different files?

**A:** Current workflow for cross-file comparison:

1. **Open first file:** Analyze and document statistics
2. **Close and open second file:** h5forest handles one file at a time
3. **Compare manually:** Document findings from each file
4. **Future feature:** Multi-file support is planned

## Troubleshooting

### Q: h5forest crashed - how do I report bugs?

**A:** Gather useful information:

1. **Error message:** Copy the full error message if available
2. **File characteristics:** File size, HDF5 version, compression
3. **System info:** Operating system, Python version, terminal type
4. **Reproduction steps:** Exact sequence of actions that caused the issue
5. **Report:** Create issue at [GitHub repository](https://github.com/WillJRoper/h5forest/issues)

### Q: Display is corrupted or garbled

**A:** Terminal display recovery:

```bash
# Reset terminal display
reset

# Or restart h5forest
Ctrl+Q (force quit)
h5forest /path/to/file.h5
```

### Q: Feature X from the documentation doesn't work

**A:** Check version and implementation status:

1. **Version check:** Some features may be version-specific
2. **Development status:** h5forest is actively developed - some documented features may be planned
3. **Mode requirements:** Ensure you're in the correct mode for the feature
4. **Update:** Try updating to the latest version

## Getting Help

### Q: Where can I get additional help?

**A:** Help resources:

- **Built-in help:** Hotkey display shows current mode's available commands
- **Documentation:** Complete mode references and examples
- **GitHub Issues:** Report bugs and request features
- **Community:** Check existing issues for similar problems

### Q: How do I request new features?

**A:** Feature request process:

1. **Check existing issues:** See if feature is already requested
2. **Describe use case:** Explain what you're trying to accomplish
3. **Provide context:** Scientific domain, data types, workflow needs
4. **Create GitHub issue:** Use feature request template

### Q: Can I contribute to h5forest development?

**A:** Contributions welcome:

- **Bug reports:** Always helpful
- **Documentation:** Improvements and examples
- **Code contributions:** Follow project contribution guidelines
- **Testing:** Try h5forest with different file types and report issues

## Performance Tips

!!! tip "Memory Management"
    Use statistical functions instead of value viewing for large datasets - they use streaming algorithms that don't load all data into memory.

!!! tip "Navigation Efficiency"
    Learn Jump Mode shortcuts (**`j`** → **`t`**, **`k`**, **`n`**, **`p`**) for quick navigation in large files.

!!! warning "Terminal Compatibility"
    h5forest requires a modern terminal with Unicode support. Very old or limited terminals may not display correctly.