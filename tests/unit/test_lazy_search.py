"""Tests for lazy search initialization features."""
import time
from unittest.mock import MagicMock, Mock, patch
import pytest


def test_tree_lazy_initialization(temp_h5_file):
    """Test that search index is not built on Tree initialization."""
    from h5forest.tree import Tree
    
    tree = Tree(temp_h5_file)
    
    # Verify lazy initialization flags
    assert tree.paths_initialized == False, "Should not have initialized paths yet"
    assert tree.index_building == False, "Should not be building index yet"
    assert tree.unpack_thread is None, "Should not have started thread yet"
    assert len(tree.all_node_paths) == 0, "Should not have collected paths yet"


def test_tree_get_all_paths_lazy_start(temp_h5_file):
    """Test that get_all_paths starts the indexing thread."""
    from h5forest.tree import Tree
    
    tree = Tree(temp_h5_file)
    
    # Call get_all_paths
    tree.get_all_paths()
    
    # Verify thread was started
    assert tree.paths_initialized == True, "Should have marked paths as initialized"
    assert tree.index_building == True, "Should be building index"
    assert tree.unpack_thread is not None, "Should have started thread"
    assert tree.unpack_thread.daemon == True, "Thread should be daemon"
    
    # Wait for thread to complete
    tree.unpack_thread.join(timeout=2.0)
    
    # Verify indexing completed
    assert tree.index_building == False, "Should have finished building"
    assert len(tree.all_node_paths) > 0, "Should have collected paths"


def test_tree_get_all_paths_only_runs_once(temp_h5_file):
    """Test that get_all_paths only starts once even if called multiple times."""
    from h5forest.tree import Tree
    
    tree = Tree(temp_h5_file)
    
    # Call get_all_paths multiple times
    tree.get_all_paths()
    first_thread = tree.unpack_thread
    
    tree.get_all_paths()
    second_thread = tree.unpack_thread
    
    # Should be the same thread
    assert first_thread is second_thread, "Should reuse same thread"
    assert tree.paths_initialized == True, "Should stay initialized"
    
    # Clean up
    if tree.unpack_thread:
        tree.unpack_thread.join(timeout=2.0)


def test_filter_tree_returns_early_when_building(temp_h5_file):
    """Test that filter_tree returns immediately when index is still building."""
    from h5forest.tree import Tree
    import threading
    import time
    
    tree = Tree(temp_h5_file)
    tree.get_tree_text()
    
    # Manually set up a long-running thread to simulate slow indexing
    tree.paths_initialized = True
    tree.index_building = True
    
    def slow_build():
        time.sleep(0.5)  # Simulate slow indexing
        tree.index_building = False
    
    tree.unpack_thread = threading.Thread(target=slow_build, daemon=True)
    tree.unpack_thread.start()
    
    # Try to filter while building
    result = tree.filter_tree("test")
    
    # Should return current tree immediately without filtering
    assert result == tree.tree_text, "Should return unfiltered tree while building"
    
    # Clean up
    tree.unpack_thread.join(timeout=1.0)
