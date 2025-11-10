"""Tests for lazy search initialization features."""


def test_tree_lazy_initialization(temp_h5_file):
    """Test that search index is not built on Tree initialization."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)

    # Verify lazy initialization flags
    assert not tree.paths_initialized, "Paths should not be initialized"
    assert not tree.index_building, "Should not be building index yet"
    assert tree.unpack_thread is None, "Should not have started thread yet"
    assert len(tree.all_node_paths) == 0, "Should not have collected paths yet"


def test_tree_get_all_paths_lazy_start(temp_h5_file):
    """Test that get_all_paths starts the indexing thread."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)

    # Call get_all_paths
    tree.get_all_paths()

    # Verify thread was started
    assert tree.paths_initialized, "Paths should be initialized"
    assert tree.index_building, "Should be building index"
    assert tree.unpack_thread is not None, "Should have started thread"
    assert tree.unpack_thread.daemon, "Thread should be daemon"

    # Wait for thread to complete
    tree.unpack_thread.join(timeout=2.0)

    # Verify indexing completed
    assert not tree.index_building, "Should have finished building"
    assert len(tree.all_node_paths) > 0, "Should have collected paths"


def test_tree_get_all_paths_only_runs_once(temp_h5_file):
    """Test that get_all_paths only starts once if called multiple times."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)

    # Call get_all_paths multiple times
    tree.get_all_paths()
    first_thread = tree.unpack_thread

    tree.get_all_paths()
    second_thread = tree.unpack_thread

    # Should be the same thread
    assert first_thread is second_thread, "Should reuse same thread"
    assert tree.paths_initialized, "Should stay initialized"

    # Clean up
    if tree.unpack_thread:
        tree.unpack_thread.join(timeout=2.0)


def test_filter_tree_returns_early_when_building(temp_h5_file):
    """Test that filter_tree returns immediately when index is building."""
    import threading
    import time

    from h5forest.tree import Tree

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
    assert result == tree.tree_text, "Should return unfiltered while building"

    # Clean up
    tree.unpack_thread.join(timeout=1.0)


def test_filter_tree_with_empty_query_restores_original(temp_h5_file):
    """Test that empty query restores original tree."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)
    tree.get_tree_text()
    original_text = tree.tree_text

    # Build index and filter
    tree.get_all_paths()
    tree.unpack_thread.join(timeout=2.0)
    tree.filter_tree("group")

    # Now filter with empty query
    result = tree.filter_tree("")

    # Should restore original tree
    assert result == original_text, "Empty query should restore original"
    assert tree.tree_text == original_text


def test_filter_tree_successful_filtering(temp_h5_file):
    """Test successful filtering with matches."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)
    tree.get_tree_text()

    # Build index
    tree.get_all_paths()
    tree.unpack_thread.join(timeout=2.0)

    # Filter with a query that should match
    result = tree.filter_tree("group")

    # Should have filtered results
    assert result != tree.original_tree_text, "Should filter tree"
    assert tree.original_tree_text is not None, "Should save original"


def test_filter_tree_no_matches(temp_h5_file):
    """Test filtering with no matches returns empty tree."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)
    tree.get_tree_text()

    # Build index
    tree.get_all_paths()
    tree.unpack_thread.join(timeout=2.0)

    # Filter with query that won't match anything
    result = tree.filter_tree("nonexistent_xyz_123")

    # Should return empty tree
    assert result == "", "No matches should return empty tree"
    assert tree.tree_text == ""
    assert len(tree.tree_text_split) == 0
    assert len(tree.nodes_by_row) == 0


def test_filter_tree_multiple_searches(temp_h5_file):
    """Test multiple sequential searches."""
    from h5forest.tree import Tree

    tree = Tree(temp_h5_file)
    tree.get_tree_text()
    original_text = tree.tree_text

    # Build index
    tree.get_all_paths()
    tree.unpack_thread.join(timeout=2.0)

    # First search
    result1 = tree.filter_tree("group")
    assert result1, "First search should have results"

    # Second search with different query (search for "data")
    result2 = tree.filter_tree("data")
    assert result2, "Second search should have results"

    # Clear search
    result3 = tree.filter_tree("")
    assert result3 == original_text, "Should restore original"
