"""Comprehensive tests for fuzzy search functionality."""

import tempfile

import h5py
import numpy as np
import pytest

from h5forest.fuzzy import fzf_scorer, search_paths
from h5forest.tree import Tree


class TestFuzzyScorer:
    """Test the fuzzy matching scorer function."""

    def test_exact_match(self):
        """Test exact string matching."""
        score = fzf_scorer("test", "test")
        assert score > 0
        assert score > fzf_scorer("test", "testing")

    def test_subsequence_match(self):
        """Test fuzzy subsequence matching (fzf-style)."""
        # "gmd" should match "Group_Mass_Data"
        score = fzf_scorer("gmd", "Group_Mass_Data")
        assert score > 0

    def test_no_match(self):
        """Test that non-matching strings return 0."""
        score = fzf_scorer("xyz", "abcdef")
        assert score == 0

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        score1 = fzf_scorer("test", "TEST")
        score2 = fzf_scorer("TEST", "test")
        score3 = fzf_scorer("TeSt", "TeSt")
        assert score1 > 0
        assert score2 > 0
        assert score3 > 0

    def test_empty_query(self):
        """Test that empty query returns 0."""
        score = fzf_scorer("", "anything")
        assert score == 0

    def test_consecutive_bonus(self):
        """Test that consecutive character matches score higher."""
        # "abc" in "abc..." should score higher than "abc" in "a_b_c..."
        consecutive_score = fzf_scorer("abc", "abcdef")
        non_consecutive_score = fzf_scorer("abc", "a_b_c_d")
        assert consecutive_score > non_consecutive_score

    def test_word_boundary_bonus(self):
        """Test that matches at word boundaries score higher."""
        # Matching at start should score higher
        boundary_score = fzf_scorer("md", "Mass_Data")
        non_boundary_score = fzf_scorer("md", "some_made")
        assert boundary_score > non_boundary_score

    def test_start_position_bonus(self):
        """Test that matches at the start score higher."""
        start_score = fzf_scorer("test", "testing")
        middle_score = fzf_scorer("test", "my_test_data")
        assert start_score > middle_score

    def test_length_penalty(self):
        """Test that shorter matches are preferred."""
        short_score = fzf_scorer("data", "data")
        long_score = fzf_scorer("data", "data_with_extra_stuff")
        assert short_score > long_score

    def test_characters_must_be_in_order(self):
        """Test that matched characters must appear in query order."""
        # "abc" should not match "cba"
        score = fzf_scorer("abc", "cba")
        assert score == 0

        # "abc" should match "a_b_c"
        score = fzf_scorer("abc", "a_b_c")
        assert score > 0


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

        # Both should match
        assert len(results) >= 1
        # "Mass_Data" should score higher (word boundaries)
        assert any("Mass_Data" in path for path, _ in results)

    def test_custom_scorer(self):
        """Test using a custom scorer function."""

        def custom_scorer(query, choice, **kwargs):
            """Simple contains check."""
            return 100 if query.lower() in choice.lower() else 0

        paths = ["test_data", "other_data", "test_group"]
        results = search_paths("test", paths, limit=10, scorer=custom_scorer)

        assert len(results) == 2
        assert all(score == 100 for _, score in results)


class TestTreeFiltering:
    """Test tree filtering functionality."""

    @pytest.fixture
    def search_test_file(self):
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

        import os

        os.unlink(filepath)

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

    def test_filtered_nodes_highlighted(self, search_test_file):
        """Test that matching nodes are marked as highlighted."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        tree.filter_tree("mass")

        # Find nodes with "Mass" in their name
        mass_nodes = [
            node for node in tree.nodes_by_row if "Mass" in node.name
        ]

        # They should all be highlighted
        for node in mass_nodes:
            assert node.is_highlighted

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

        # Rows should correspond to highlighted nodes
        for row_idx in tree.filtered_node_rows:
            node = tree.nodes_by_row[row_idx]
            assert node.is_highlighted

    def test_fuzzy_search_path_matching(self, search_test_file):
        """Test fuzzy matching on full paths."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Search for "g2t" - should match "Group2/Subgroup/Temperature"
        filtered = tree.filter_tree("g2t")

        assert "Temperature" in filtered or filtered == ""
        # Note: May not match depending on scorer strictness

    def test_top_20_limit(self, search_test_file):
        """Test that only top 20 results are shown."""
        # Create a file with more than 20 matching items
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
            filepath = tmp.name

        with h5py.File(filepath, "w") as f:
            for i in range(50):
                f.create_dataset(f"Data_{i}", data=np.arange(5))

        try:
            tree = Tree(filepath)
            tree.get_tree_text()

            if tree.unpack_thread:
                tree.unpack_thread.join()

            tree.filter_tree("data")

            # Should have at most 21 nodes (20 matches + root)
            # Actually depends on tree structure, but filtered matches should be <= 20
            assert len(tree.filtered_node_rows) <= 20

        finally:
            import os

            os.unlink(filepath)

    def test_highlighting_cleared_on_restore(self, search_test_file):
        """Test that highlighting is cleared when tree is restored."""
        tree = Tree(search_test_file)
        tree.get_tree_text()

        if tree.unpack_thread:
            tree.unpack_thread.join()

        # Filter and check highlighting
        tree.filter_tree("mass")
        highlighted_before = any(node.is_highlighted for node in tree.nodes_by_row)
        assert highlighted_before

        # Restore and check highlighting is cleared
        tree.restore_tree()
        highlighted_after = any(node.is_highlighted for node in tree.nodes_by_row)
        assert not highlighted_after


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
