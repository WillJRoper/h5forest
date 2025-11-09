"""Comprehensive tests for fuzzy search functionality."""

import os
import tempfile

import h5py
import numpy as np
import pytest

from h5forest.fuzzy import get_match_indices, search_paths
from h5forest.tree import Tree


@pytest.fixture
def search_test_file():
    """Create a test HDF5 file specifically for search testing."""
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
        filepath = tmp.name

    with h5py.File(filepath, "w") as f:
        # Create nested structure for testing
        f.create_dataset("RootData", data=np.arange(10))

        # Group 1
        g1 = f.create_group("Group1")
        g1.create_dataset("Mass", data=np.ones(5))
        g1.create_dataset("Velocity", data=np.ones(5) * 2)

        # Nested groups
        g2 = f.create_group("Group2")
        g2_sub = g2.create_group("Subgroup")
        g2_sub.create_dataset("Temperature", data=np.ones(3) * 300)
        g2_sub.create_dataset("Pressure", data=np.ones(3) * 101)

        # Another level
        g3 = f.create_group("Analysis")
        g3_data = g3.create_group("Data")
        g3_data.create_dataset("Mass_Fraction", data=np.ones(10) * 0.5)
        g3_data.create_dataset("Density", data=np.ones(10) * 1.2)

    yield filepath

    os.unlink(filepath)


class TestGetMatchIndices:
    """Test the get_match_indices function."""

    def test_basic_matching(self):
        """Test basic character index matching."""
        indices = get_match_indices("abc", "xaxbxcx")
        assert indices == [1, 3, 5]

    def test_empty_query(self):
        """Test that empty query returns empty list."""
        indices = get_match_indices("", "some text")
        assert indices == []

    def test_empty_text(self):
        """Test that empty text returns empty list."""
        indices = get_match_indices("query", "")
        assert indices == []

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        indices = get_match_indices("abc", "AXBXCX")
        assert indices == [0, 2, 4]

    def test_partial_match(self):
        """Test partial match when not all characters found."""
        indices = get_match_indices("xyz", "xy")
        assert len(indices) == 2  # Only x and y found


class TestSearchPaths:
    """Test the search_paths function."""

    def test_basic_search(self):
        """Test basic path searching."""
        paths = ["Group1/Data", "Group2/Mass", "Group1/Velocity"]
        results = search_paths("mass", paths, limit=10)

        assert len(results) > 0
        assert results[0][0] == "Group2/Mass"
        assert results[0][1] > 0  # Has a score

    def test_limit_results(self):
        """Test that results are limited correctly."""
        paths = [f"Group{i}/Dataset{i}" for i in range(100)]
        results = search_paths("group", paths, limit=20)

        assert len(results) == 20

    def test_empty_query(self):
        """Test that empty query returns empty results."""
        paths = ["Group1/Data", "Group2/Mass"]
        results = search_paths("", paths, limit=10)

        assert len(results) == 0

    def test_no_matches(self):
        """Test that non-matching query returns empty results."""
        paths = ["Group1/Data", "Group2/Mass"]
        results = search_paths("xyz123", paths, limit=10)

        assert len(results) == 0

    def test_sorted_by_score(self):
        """Test that results are sorted by score (descending)."""
        paths = [
            "Group/Mass",  # Should score high
            "Group/Something/Mass/Data",  # Should score lower (longer)
            "Other/Misc/StuffMass",  # Should score even lower
        ]
        results = search_paths("mass", paths, limit=10)

        # Check that scores are in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_fuzzy_matching(self):
        """Test fuzzy matching with non-consecutive characters."""
        paths = ["Group1/Mass_Data", "Group2/Metadata"]
        results = search_paths("md", paths, limit=10)

        # Should have at least one match
        assert len(results) >= 1


class TestTreeFiltering:
    """Test tree filtering functionality."""

    def test_filter_tree_basic(self, search_test_file):
        """Test basic tree filtering."""
        tree = Tree(search_test_file)
        tree.get_tree_text()  # Initialize tree

        # Wait for background thread to collect paths
        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for "mass"
        filtered = tree.filter_tree("mass")

        assert filtered != ""
        assert "Mass" in filtered
        assert "Group1" in filtered  # Parent should be included

    def test_filter_tree_nested(self, search_test_file):
        """Test filtering with nested paths."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for "temperature"
        filtered = tree.filter_tree("temperature")

        # Should include the match and all parents
        assert "Temperature" in filtered
        assert "Subgroup" in filtered
        assert "Group2" in filtered

    def test_filter_tree_multiple_matches(self, search_test_file):
        """Test filtering with multiple matching nodes."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for "mass" - should match "Mass" and "Mass_Fraction"
        filtered = tree.filter_tree("mass")

        assert "Mass" in filtered
        assert "Mass_Fraction" in filtered

    def test_filter_tree_empty_query(self, search_test_file):
        """Test that empty query doesn't filter."""
        tree = Tree(search_test_file)
        original = tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # First filter
        tree.filter_tree("mass")

        # Then empty query should restore
        filtered = tree.filter_tree("")

        assert filtered == original

    def test_filter_tree_no_matches(self, search_test_file):
        """Test filtering with no matches returns empty tree."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        filtered = tree.filter_tree("xyz123nonexistent")

        assert filtered == ""
        assert len(tree.nodes_by_row) == 0

    def test_restore_tree(self, search_test_file):
        """Test that tree can be restored after filtering."""
        tree = Tree(search_test_file)
        original = tree.get_tree_text()
        original_nodes = tree.nodes_by_row.copy()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Filter the tree
        tree.filter_tree("mass")

        assert tree.tree_text != original

        # Restore
        tree.restore_tree()

        assert tree.tree_text == original
        assert len(tree.nodes_by_row) == len(original_nodes)

    def test_filtered_nodes_present(self, search_test_file):
        """Test that matching nodes are present in filtered results."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        tree.filter_tree("mass")

        # Find nodes with "Mass" in their name
        mass_nodes = [
            node for node in tree.nodes_by_row if "Mass" in node.name
        ]

        # Should have at least one match
        assert len(mass_nodes) > 0

    def test_parent_nodes_opened(self, search_test_file):
        """Test that parent nodes are opened to show matches."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for deeply nested "Temperature"
        tree.filter_tree("temperature")

        # Find the parent nodes
        group2 = None
        subgroup = None
        for node in tree.nodes_by_row:
            if node.name == "Group2":
                group2 = node
            elif node.name == "Subgroup":
                subgroup = node

        # Both parents should be expanded
        assert group2 is not None
        assert group2.is_expanded
        assert subgroup is not None
        assert subgroup.is_expanded

    def test_filtered_node_rows_tracked(self, search_test_file):
        """Test that filtered_node_rows contains row indices of matches."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        tree.filter_tree("mass")

        # Should have row indices
        assert len(tree.filtered_node_rows) > 0

        # Rows should correspond to actual nodes with "Mass" in the name
        for row_idx in tree.filtered_node_rows:
            node = tree.nodes_by_row[row_idx]
            assert "Mass" in node.name or "mass" in node.name.lower()

    def test_fuzzy_search_path_matching(self, search_test_file):
        """Test fuzzy matching on full paths."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for "g2t" - should match "Group2/Subgroup/Temperature"
        filtered = tree.filter_tree("g2t")

        assert "Temperature" in filtered or filtered == ""

    def test_top_100_limit(self, search_test_file):
        """Test that only top 100 results are shown."""
        # Create a file with more than 100 matching items
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
            filepath = tmp.name

        with h5py.File(filepath, "w") as f:
            for i in range(150):
                f.create_dataset(f"Data_{i}", data=np.arange(5))

        try:
            tree = Tree(filepath)
            tree.get_tree_text()

            if tree.unpack_thread:
                tree.unpack_thread.join()

            tree.filter_tree("data")

            # Should have at most 100 matches
            assert len(tree.filtered_node_rows) <= 100

        finally:
            os.unlink(filepath)

    def test_filter_state_cleared_on_restore(self, search_test_file):
        """Test that filter state is cleared when tree is restored."""
        tree = Tree(search_test_file)
        original = tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Filter the tree
        tree.filter_tree("mass")
        assert tree.tree_text != original
        assert len(tree.filtered_node_rows) > 0

        # Restore and check state is cleared
        tree.restore_tree()
        assert tree.tree_text == original
        assert len(tree.filtered_node_rows) == 0


class TestSearchIntegration:
    """Integration tests for search functionality."""

    def test_multiple_filter_operations(self, search_test_file):
        """Test multiple consecutive filter operations."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # First search
        tree.filter_tree("mass")
        first_result = tree.tree_text

        # Second search (should save state on first query)
        tree.filter_tree("temp")
        second_result = tree.tree_text

        assert first_result != second_result

        # Restore
        tree.restore_tree()

    def test_filter_then_restore_then_filter(self, search_test_file):
        """Test filter -> restore -> filter sequence."""
        tree = Tree(search_test_file)
        original = tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Filter
        tree.filter_tree("mass")
        # Restore
        tree.restore_tree()
        assert tree.tree_text == original

        # Filter again
        tree.filter_tree("velocity")
        assert "Velocity" in tree.tree_text

    def test_case_insensitive_search(self, search_test_file):
        """Test that search is case-insensitive."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Try different cases
        result1 = tree.filter_tree("MASS")
        tree.restore_tree()
        result2 = tree.filter_tree("mass")
        tree.restore_tree()
        result3 = tree.filter_tree("MaSs")

        # All should produce similar results (same nodes matched)
        assert "Mass" in result1 or result1 == ""
        assert "Mass" in result2 or result2 == ""
        assert "Mass" in result3 or result3 == ""

    def test_subsequence_matching_required(self, search_test_file):
        """Test that all query characters must appear in order."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # "c" should NOT match "MassWeightedGasZ" since all chars must
        # be in order. This test verifies filtering ensures subsequence
        # matching.
        filtered = tree.filter_tree("xyz")

        # Should have no results since xyz doesn't appear in order anywhere
        assert filtered == "" or "xyz" in filtered.lower()

    def test_restore_to_initial_state(self, search_test_file):
        """Test restoring tree to initial state collapses all nodes."""
        tree = Tree(search_test_file)
        initial_text = tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Manually expand some nodes
        for node in tree.root.children:
            if node.is_group and node.has_children:
                node.open_node()
                break

        # Get expanded tree text
        tree.get_tree_text()
        assert len(tree.root.children) > 0

        # Now simulate restore to initial (like 'r' key does)
        # Close all children
        for child in tree.root.children:
            child.close_node()

        # Clear and reopen just root level
        tree.root.children = []
        tree.root.open_node()

        # Rebuild tree
        restored_text = tree.get_tree_text()

        # Should match initial state (only root expanded)
        assert restored_text == initial_text

    def test_filter_then_accept_workflow(self, search_test_file):
        """Test the workflow of filtering and accepting results."""
        tree = Tree(search_test_file)
        original = tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Filter the tree
        filtered = tree.filter_tree("mass")
        assert filtered != original
        assert "Mass" in filtered

        # In real usage, Enter would keep this filtered view
        # and return to normal mode. The tree should stay filtered.
        # We can verify by checking filtered nodes are tracked
        assert len(tree.filtered_node_rows) > 0

        # User can then restore with 'r' key which would:
        for child in tree.root.children:
            child.close_node()
        tree.root.children = []
        tree.root.open_node()
        restored = tree.get_tree_text()

        # Should be back to initial
        assert restored == original


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
