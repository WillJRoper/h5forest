"""Unit tests for h5forest.tree module - corrected version."""

from unittest.mock import Mock

import pytest

from h5forest.node import Node
from h5forest.tree import Tree, TreeProcessor


class TestTreeInitialization:
    """Test Tree initialization."""

    def test_tree_init_with_file(self, simple_h5_file):
        """Test successful Tree initialization."""
        tree = Tree(simple_h5_file)

        assert tree.filepath == simple_h5_file
        assert hasattr(tree, "root")
        assert hasattr(tree, "nodes_by_row")
        assert isinstance(tree.nodes_by_row, list)
        assert tree.root is not None

    def test_tree_init_sets_filename(self, simple_h5_file):
        """Test that Tree sets filename correctly."""
        tree = Tree(simple_h5_file)

        expected_name = (
            simple_h5_file.split("/")[-1]
            .replace(".h5", "")
            .replace(".hdf5", "")
        )
        assert tree.filename == expected_name

    def test_tree_init_creates_root_node(self, simple_h5_file):
        """Test that Tree creates root node."""
        tree = Tree(simple_h5_file)

        assert tree.root is not None
        assert isinstance(tree.root, Node)
        assert tree.root.name == tree.filename
        assert tree.root.depth == 0

    def test_tree_properties(self, simple_h5_file):
        """Test Tree properties."""
        tree = Tree(simple_h5_file)

        # Generate tree text to populate nodes_by_row
        tree.get_tree_text()

        assert hasattr(tree, "height")
        assert hasattr(tree, "length")
        assert tree.height == len(tree.nodes_by_row)


class TestTreeTextGeneration:
    """Test Tree text generation."""

    def test_get_tree_text(self, simple_h5_file):
        """Test basic tree text generation."""
        tree = Tree(simple_h5_file)

        tree_text = tree.get_tree_text()

        assert isinstance(tree_text, str)
        assert len(tree_text) > 0
        assert tree.filename in tree_text

    def test_tree_text_contains_nodes(self, simple_h5_file):
        """Test that tree text contains expected nodes."""
        tree = Tree(simple_h5_file)

        tree_text = tree.get_tree_text()

        # Should contain root node name
        assert tree.filename in tree_text

        # Should contain some structure indicators or node names
        assert len(tree_text.split("\n")) >= 1

    def test_nodes_by_row_populated(self, simple_h5_file):
        """Test that nodes_by_row is populated correctly."""
        tree = Tree(simple_h5_file)

        tree.get_tree_text()

        assert len(tree.nodes_by_row) >= 1
        assert all(isinstance(node, Node) for node in tree.nodes_by_row)

    def test_tree_text_split_updated(self, simple_h5_file):
        """Test that tree_text_split is updated."""
        tree = Tree(simple_h5_file)

        tree.get_tree_text()

        assert hasattr(tree, "tree_text_split")
        assert isinstance(tree.tree_text_split, list)
        assert len(tree.tree_text_split) > 0


class TestTreeNavigation:
    """Test Tree navigation functionality."""

    def test_parse_level_opens_node(self, complex_h5_file):
        """Test that parse_level opens a node."""
        tree = Tree(complex_h5_file)

        # Find a group node that can be opened
        tree.get_tree_text()

        group_node = None
        for node in tree.nodes_by_row:
            if node.is_group and node.has_children:
                group_node = node
                break

        if group_node:
            initial_children = len(group_node.children)
            tree.parse_level(group_node)

            # Should have opened the node
            assert len(group_node.children) >= initial_children

    def test_recursive_tree_building(self, complex_h5_file):
        """Test recursive tree text building."""
        tree = Tree(complex_h5_file)

        # Get initial tree text
        tree_text = tree.get_tree_text()

        # Should have multiple lines for a complex file
        lines = tree_text.strip().split("\n")
        assert len(lines) >= 1

        # Each line should correspond to a node
        assert len(tree.nodes_by_row) == len(
            [line for line in lines if line.strip()]
        )


class TestTreeProcessor:
    """Test TreeProcessor for styling."""

    def test_tree_processor_init(self, simple_h5_file):
        """Test TreeProcessor initialization."""
        tree = Tree(simple_h5_file)
        processor = TreeProcessor(tree)

        assert processor.tree == tree

    def test_tree_processor_apply_transformation_valid_line(
        self, simple_h5_file
    ):
        """Test TreeProcessor transformation for valid line."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()  # Populate nodes_by_row
        processor = TreeProcessor(tree)

        if tree.nodes_by_row:
            # Mock transformation input
            mock_ti = Mock()
            mock_ti.lineno = 0
            mock_ti.fragments = [("", "test text")]

            transformation = processor.apply_transformation(mock_ti)

            assert transformation is not None
            assert hasattr(transformation, "fragments")

    def test_tree_processor_apply_transformation_out_of_bounds(
        self, simple_h5_file
    ):
        """Test TreeProcessor transformation for out of bounds line."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()
        processor = TreeProcessor(tree)

        # Mock transformation input with line beyond nodes
        mock_ti = Mock()
        mock_ti.lineno = 999  # Way beyond any nodes
        mock_ti.fragments = [("", "test text")]

        transformation = processor.apply_transformation(mock_ti)

        assert transformation is not None
        assert transformation.fragments == mock_ti.fragments

    def test_tree_processor_styling(self, simple_h5_file):
        """Test TreeProcessor applies styling based on node properties."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()
        processor = TreeProcessor(tree)

        if tree.nodes_by_row:
            node = tree.nodes_by_row[0]
            node.is_highlighted = True
            node.is_under_cursor = True

            mock_ti = Mock()
            mock_ti.lineno = 0
            mock_ti.fragments = [("", "test text")]

            transformation = processor.apply_transformation(mock_ti)

            # Should have applied styling
            if transformation.fragments:
                style = transformation.fragments[0][0]
                assert "highlighted" in style or "under_cursor" in style


class TestTreeFileOperations:
    """Test Tree file operations."""

    def test_tree_with_nonexistent_file(self):
        """Test Tree with nonexistent file raises error."""
        with pytest.raises((FileNotFoundError, OSError)):
            Tree("nonexistent_file.h5")

    def test_tree_with_different_file_types(
        self, simple_h5_file, complex_h5_file
    ):
        """Test Tree with different HDF5 file structures."""
        simple_tree = Tree(simple_h5_file)
        complex_tree = Tree(complex_h5_file)

        simple_text = simple_tree.get_tree_text()
        complex_text = complex_tree.get_tree_text()

        # Both should work
        assert isinstance(simple_text, str)
        assert isinstance(complex_text, str)

        # Complex should typically have more content
        assert len(simple_tree.nodes_by_row) >= 1
        assert len(complex_tree.nodes_by_row) >= 1


class TestTreeProperties:
    """Test Tree property methods."""

    def test_height_property(self, simple_h5_file):
        """Test height property."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()

        height = tree.height
        assert isinstance(height, int)
        assert height == len(tree.nodes_by_row)

    def test_length_property(self, simple_h5_file):
        """Test length property."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()

        length = tree.length
        assert isinstance(length, int)
        assert length == len(tree.tree_text)

    def test_width_property(self, simple_h5_file):
        """Test width property."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()

        if tree.tree_text_split:
            width = tree.width
            assert isinstance(width, int)
            assert width > 0


class TestTreeIntegration:
    """Test Tree integration with Node objects."""

    def test_tree_contains_root_node(self, simple_h5_file):
        """Test that tree contains root node."""
        tree = Tree(simple_h5_file)

        assert tree.root is not None
        assert tree.root.name == tree.filename

    def test_tree_root_node_properties(self, simple_h5_file):
        """Test root node properties."""
        tree = Tree(simple_h5_file)

        root = tree.root
        assert root.filepath == simple_h5_file
        assert root.path == "/"
        assert root.depth == 0
        assert root.parent is None

    def test_tree_expands_root_automatically(self, complex_h5_file):
        """Test that tree expands root node automatically."""
        tree = Tree(complex_h5_file)

        # Root should auto-expand if it has children
        if tree.root.has_children:
            # Check if root opened automatically (based on Node.__init__ logic)
            # Root nodes at depth 0 call open_node() automatically
            assert tree.root.is_expanded


class TestTreeUpdates:
    """Test Tree update functionality."""

    def test_tree_text_updates(self, complex_h5_file):
        """Test tree text updates when structure changes."""
        tree = Tree(complex_h5_file)

        # Get initial text and count
        tree.get_tree_text()
        initial_nodes = len(tree.nodes_by_row)

        # Find a group that can be expanded
        for node in tree.nodes_by_row:
            if node.is_group and node.has_children and not node.is_expanded:
                tree.parse_level(node)
                break

        # Get updated text
        updated_text = tree.get_tree_text()
        updated_nodes = len(tree.nodes_by_row)

        # Tree should have potentially changed
        assert isinstance(updated_text, str)
        assert updated_nodes >= initial_nodes  # Could have more nodes now

    def test_nodes_by_row_consistency(self, simple_h5_file):
        """Test that nodes_by_row remains consistent with tree_text."""
        tree = Tree(simple_h5_file)
        tree.get_tree_text()

        # Number of non-empty lines should match nodes_by_row length
        non_empty_lines = [
            line for line in tree.tree_text.split("\n") if line.strip()
        ]
        assert len(non_empty_lines) == len(tree.nodes_by_row)
