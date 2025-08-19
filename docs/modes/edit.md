# Edit Mode

Edit Mode allows you to rename groups and datasets in your HDF5 files safely and efficiently. This mode provides a two-step confirmation process to prevent accidental modifications.

## Entering Edit Mode

From Normal Mode, press **`e`** to enter Edit Mode.

## Basic Workflow

### Renaming Process

1. **Select Target**: Navigate to the group or dataset you want to rename
2. **Enter Edit Mode**: Press **`e`** to enter Edit Mode
3. **Start Editing**: Press **`e`** again to begin renaming the selected item
4. **Edit Name**: Type the new name in the mini buffer
5. **Confirm**: Press **Enter** to confirm the new name
6. **Final Confirmation**: Confirm the rename operation when prompted

### Step-by-Step Example

```
1. Navigate to the item you want to rename
   ├── my_group
   │   ├── old_dataset_name ← cursor here
   │   └── other_data

2. Press 'e' to enter Edit Mode
   [Hotkeys show: e → Edit Name, q → Exit Edit Mode]

3. Press 'e' to start editing 'old_dataset_name'
   Edit name for old_dataset_name: old_dataset_name

4. Change the name to 'new_dataset_name'
   Edit name for old_dataset_name: new_dataset_name

5. Press Enter to confirm
   Rename Dataset 'old_dataset_name' to 'new_dataset_name'? (y/n):

6. Type 'y' and press Enter
   Rename operation started for old_dataset_name
   Successfully renamed dataset to new_dataset_name
```

## Keyboard Reference

| Key | Action | Context |
|-----|--------|---------|
| **`e`** | Enter Edit Mode | Normal Mode |
| **`e`** | Edit name of selected item | Edit Mode |
| **`q`** | Exit Edit Mode | Edit Mode |
| **Enter** | Confirm name edit | Name editing |
| **Enter** | Confirm rename operation | Confirmation prompt |
| **Escape** | Cancel operation | Name editing or confirmation |

## Safety Features

### Validation

- **Empty names**: Cannot rename to empty string
- **Duplicate names**: Prevents creating duplicate names in the same group
- **Invalid characters**: Rejects names containing '/' character
- **Unchanged names**: Detects and skips when new name equals old name

### Confirmation Process

1. **Name Validation**: Input is checked before proceeding
2. **Existence Check**: Verifies target name doesn't already exist
3. **User Confirmation**: Explicit yes/no confirmation required
4. **Progress Tracking**: Shows progress for large operations

## Technical Details

### Memory-Safe Operations

For large datasets and groups:

- **Chunked Copying**: Data is copied in memory-safe chunks
- **Progress Indicators**: Real-time progress updates during operations
- **Error Recovery**: Comprehensive error handling for failed operations

### File Operations

- **Copy-then-Delete**: Creates new item before removing old one
- **Atomic Operations**: Minimizes risk of data loss
- **Attribute Preservation**: All HDF5 attributes are preserved
- **Compression Settings**: Original compression settings maintained

## Performance Considerations

### Small Items (< 1M elements)
- **Fast Operation**: Direct copying for quick completion
- **Immediate Update**: Tree display updates instantly

### Large Items (≥ 1M elements)
- **Chunked Processing**: Processes data in manageable chunks
- **Progress Tracking**: Visual progress indication
- **Memory Efficient**: Prevents memory overflow

### Groups with Many Items
- **Recursive Processing**: Handles nested structures
- **Bulk Operations**: Efficiently processes multiple datasets
- **Progress Updates**: Shows overall progress

## Error Handling

### Common Error Scenarios

| Error Type | Description | Resolution |
|------------|-------------|-----------|
| **Name Exists** | Target name already exists | Choose different name |
| **File Access** | Cannot access HDF5 file | Check file permissions |
| **Memory Error** | Insufficient memory for operation | Try smaller chunks |
| **I/O Error** | Disk write/read failure | Check disk space and permissions |
| **HDF5 Error** | HDF5 library error | Check file integrity |

### Error Messages

- **Clear Descriptions**: Human-readable error explanations
- **Context Information**: Details about what failed
- **Recovery Suggestions**: Hints for resolving issues

## Best Practices

### Before Renaming
1. **Backup Important Files**: Always backup before major changes
2. **Check Dependencies**: Ensure no external references to old names
3. **Plan Structure**: Consider impact on file organization

### During Operation
1. **Review Names Carefully**: Double-check spelling and format
2. **Confirm Deliberately**: Read confirmation prompts carefully
3. **Monitor Progress**: Watch for error messages during operation

### After Renaming
1. **Verify Results**: Check that rename completed successfully
2. **Test Access**: Ensure renamed items are accessible
3. **Update Documentation**: Update any external documentation

## Workflow Integration

### Typical Workflows

#### Simple Rename
```
Normal Mode → Navigate to item
     ↓
Edit Mode → Press 'e' to edit
     ↓
Edit Name → Type new name
     ↓
Confirm → Verify operation
     ↓
Normal Mode → Continue exploring
```

#### Batch Organization
```
Normal Mode → Navigate to first item
     ↓
Edit Mode → Rename first item
     ↓
Normal Mode → Navigate to next item
     ↓
Edit Mode → Rename next item
     ↓
Repeat as needed
```

## Limitations

### Current Limitations
- **No Undo**: Rename operations cannot be undone
- **Single Item**: Can only rename one item at a time
- **Name Restrictions**: Limited by HDF5 naming conventions

### Future Enhancements
- **Batch Rename**: Multiple item renaming
- **Pattern Matching**: Regex-based renaming
- **Undo Support**: Operation reversal capability

## Tips and Tricks

### Efficiency Tips
1. **Navigate First**: Move to target before entering Edit Mode
2. **Use Clear Names**: Choose descriptive, consistent names
3. **Group Related Items**: Organize items with similar naming patterns

### Avoiding Errors
1. **Check Spelling**: Verify names before confirming
2. **Avoid Special Characters**: Stick to letters, numbers, and underscores
3. **Test with Small Items**: Practice on small datasets first

## Related Modes

- **[Normal Mode](normal.md)**: Basic navigation to locate items
- **[Goto Mode](goto.md)**: Quick navigation to specific items
- **[Dataset Mode](dataset.md)**: Analyze data before renaming
- **[Window Mode](window.md)**: Manage display during operations