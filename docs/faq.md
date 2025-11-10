# Frequently Asked Questions

Common questions and solutions for `h5forest` users.

## Installation and Setup

### Q: `h5forest` won't start - "command not found"

**A:** Ensure `h5forest` is properly installed:

```bash
# Check if installed
which h5forest

# If not found, install or reinstall
pip install h5forest

# Or if installed with --user flag
pip install --user h5forest
export PATH=$PATH:~/.local/bin
```

### Q: Import errors when starting `h5forest`

**A:** Check that all dependencies are installed:

```bash
# Check for missing dependencies
python -c "import h5py, numpy, prompt_toolkit, matplotlib"

# If any fail, reinstall h5forest
pip install --upgrade h5forest
```

### Q: `h5forest` displays incorrectly in my terminal

**A:** `h5forest` requires a modern terminal with Unicode support:

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

### Q: `h5forest` won't open my HDF5 file

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

**A:** For now, if you have a large number of Groups at the root level this is expected behavior. We do plan to introduce asynchronous tree construction in a future release to address this.



## Navigation and Interface

### Q: I'm lost in a deep hierarchy - how do I get back to the root?

**A:** `q` will always exit and eventually return you to the root. Furthermore, once in normal mode you can press `r` to restore the TUI to the state it would be if you had just opened the file.

### Q: The interface looks cramped, help!

**A:** While `h5forest` does its best to adapt to your terminal size, its not totally dynamic yet. You can try resizing your terminal window which will retrigger a redraw of the interface. If that doesn't help, you should exit, adjust your font size and re-open `h5forest`.

### Q: Keyboard shortcuts aren't working

**A:** If the key is displayed in the hotkey panel but doesn't work, please raise an issue with details of the issue (including your OS, terminal, and `h5forest` version). If the key isn't displayed, you may be in the wrong mode - check the mode indicator at the bottom of the screen and use `q` to exit to Normal Mode.

## Data Analysis

### Q: Statistical calculations are very slow

**A:** Is your dataset very large but not chunked? Statistics on large unchunked datasets can be slow due to the need to read all data at once. When chunked data is found, `h5forest` can read in manageable pieces. I'm afraid there's not much that can be done for unchunked datasets other than being patient or pre-processing the data into a chunked format. Note that exploring the file will still be fast even if statistics are slow.

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

### Q: Can't save plots or histograms

**A:** Check save functionality:

1. **Use correct key:** **`P`** (capital) for plots, **`H`** (capital) for histograms
2. **File permissions:** Ensure write permissions in current directory
3. **Filename:** Provide valid filename when prompted

## Performance

### Q: Operations freeze or become unresponsive

**A:** Do you have lots of groups at a single level? This can cause delays as `h5forest` builds the tree structure. In most cases, `h5forest` should remain responsive and display progress indicators.

Recovery options:

1. **Wait for completion:** Check for progress bars indicating ongoing operations
2. **Terminal reset:** If display is corrupted, exit and `clear` terminal, then restart h5forest.

Should you encounter a freeze with no progress and unresponsive UI/exit keys, please report a bug with details of your system and file. In normal circumstances `h5forest` should remain responsive and abort any long-running operations.

### Q: Can h5forest handle compressed datasets?

**A:** Yes, `h5forest` handles HDF5 compression transparently:

- **Automatic decompression:** All compression types supported by `h5py`
- **Performance:** Compressed data **may** be slower to access
- **Memory usage:** Decompression happens in chunks to manage memory

## Troubleshooting

### Q: `h5forest` crashed - how do I report bugs?

**A:** Gather useful information:

1. **Error message:** Copy the full error message if available
2. **File characteristics:** File size, HDF5 version, compression
3. **System info:** Operating system, Python version, terminal type
4. **Reproduction steps:** Exact sequence of actions that caused the issue
5. **Report:** Create issue at [GitHub repository](https://github.com/WillJRoper/h5forest/issues)

### Q: Display is corrupted or garbled

**A:** Terminal display recovery (there's nothing fancy here):

```bash
# Reset terminal display
clear

# Restart h5forest
h5forest /path/to/file.h5
```

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

### Q: Can I contribute to `h5forest` development?

**A:** Contributions welcome:

- **Bug reports:** Always helpful
- **Documentation:** Improvements and examples
- **Code contributions:** Follow project contribution guidelines
- **Testing:** Try `h5forest` with different file types and report issues
