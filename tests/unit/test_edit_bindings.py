"""Tests for direct edit bindings functionality."""

from unittest.mock import Mock

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import VSplit

from h5forest.bindings.edit_bindings import _init_edit_bindings


class TestDirectEditBindingsInitialization:
    """Test initialization of direct edit bindings."""

    def test_init_edit_bindings_returns_empty_hotkeys(self):
        """Test that _init_edit_bindings returns empty hotkeys widget."""
        # Create a mock app with minimal required interface
        mock_app = Mock()
        mock_app.kb = Mock()
        mock_app.kb.add = Mock(return_value=lambda func: func)
        mock_app.flag_normal_mode = True

        # Call the initialization function
        result = _init_edit_bindings(mock_app)

        # Should return an empty VSplit since edit is no longer a mode
        assert isinstance(result, VSplit)
        assert len(result.children) == 0

        # Should have called kb.add to set up key bindings
        mock_app.kb.add.assert_called()

    def test_edit_bindings_registers_keybindings(self):
        """Test that edit bindings registers the correct keybindings."""
        mock_app = Mock()

        # Track what keybindings are registered
        registered_keys = []

        def mock_add(key, **kwargs):
            registered_keys.append((key, kwargs))
            return lambda func: func

        mock_app.kb.add = mock_add
        mock_app.flag_normal_mode = True

        _init_edit_bindings(mock_app)

        # Should register the 'e' key for direct edit
        assert len(registered_keys) == 1
        assert registered_keys[0][0] == "e"
        assert "filter" in registered_keys[0][1]

    def test_edit_bindings_uses_normal_mode_filter(self):
        """Test that edit bindings use normal mode filter."""
        mock_app = Mock()
        mock_app.flag_normal_mode = True

        # Capture the filter condition
        captured_filter = None

        def mock_add(key, **kwargs):
            nonlocal captured_filter
            if "filter" in kwargs:
                captured_filter = kwargs["filter"]
            return lambda func: func

        mock_app.kb.add = mock_add

        _init_edit_bindings(mock_app)

        # Should have captured a Condition filter
        assert captured_filter is not None
        assert isinstance(captured_filter, Condition)


class TestDirectEditBindingsIntegration:
    """Test direct edit bindings integration with the application."""

    def test_edit_bindings_imports_successfully(self):
        """Test that edit bindings can be imported and initialized."""
        # Test import
        from h5forest.bindings.edit_bindings import _init_edit_bindings

        # Create mock app
        mock_app = Mock()
        mock_app.kb = Mock()
        mock_app.kb.add = Mock(return_value=lambda func: func)
        mock_app.flag_normal_mode = True

        # Should initialize without error
        result = _init_edit_bindings(mock_app)
        assert result is not None
        assert isinstance(result, VSplit)


class TestDirectEditFunctionality:
    """Test the actual direct edit functionality (mocked)."""

    def test_direct_edit_function_exists(self):
        """Test that direct edit function can be accessed."""
        mock_app = Mock()
        mock_app.kb = Mock()

        # Capture the registered function
        registered_function = None

        def mock_add(key, **kwargs):
            def decorator(func):
                nonlocal registered_function
                registered_function = func
                return func

            return decorator

        mock_app.kb.add = mock_add
        mock_app.flag_normal_mode = True

        _init_edit_bindings(mock_app)

        # Should have captured the direct_edit function
        assert registered_function is not None
        assert callable(registered_function)

    def test_direct_edit_handles_tree_context(self):
        """Test direct edit with tree context."""
        mock_app = Mock()
        mock_app.app = Mock()
        mock_app.app.layout = Mock()
        mock_app.tree_content = Mock()
        mock_app.app.layout.current_window = mock_app.tree_content

        mock_node = Mock()
        mock_node.name = "test_dataset"
        mock_app.tree = Mock()
        mock_app.tree.get_current_node.return_value = mock_node
        mock_app.current_row = 0
        mock_app.input = Mock()

        # Capture the direct_edit function
        direct_edit_func = None

        def mock_add(key, **kwargs):
            def decorator(func):
                nonlocal direct_edit_func
                direct_edit_func = func
                return func

            return decorator

        mock_app.kb.add = mock_add

        _init_edit_bindings(mock_app)

        # Call the direct_edit function
        mock_event = Mock()
        direct_edit_func(mock_event)

        # Should call input to get new name for tree item
        mock_app.input.assert_called_once()

    def test_direct_edit_handles_attributes_context(self):
        """Test direct edit with attributes context."""
        mock_app = Mock()
        mock_app.app = Mock()
        mock_app.app.layout = Mock()
        mock_app.attributes_content = Mock()
        mock_app.app.layout.current_window = mock_app.attributes_content

        # Mock the buffer and document for attributes content
        mock_doc = Mock()
        mock_doc.cursor_position_row = 0
        mock_doc.text = "test_key: test_value"
        mock_app.attributes_content.buffer = Mock()
        mock_app.attributes_content.buffer.document = mock_doc

        mock_node = Mock()
        mock_node.path = "/test"
        mock_node.get_current_attribute.return_value = (
            "test_key",
            "test_value",
        )
        mock_app.tree = Mock()
        mock_app.tree.get_current_node.return_value = mock_node
        mock_app.current_row = 0
        mock_app.input = Mock()
        mock_app.print = Mock()
        mock_app.default_focus = Mock()

        # Capture the direct_edit function
        direct_edit_func = None

        def mock_add(key, **kwargs):
            def decorator(func):
                nonlocal direct_edit_func
                direct_edit_func = func
                return func

            return decorator

        mock_app.kb.add = mock_add

        _init_edit_bindings(mock_app)

        # Call the direct_edit function
        mock_event = Mock()
        direct_edit_func(mock_event)

        # Should call input to edit attribute key (first step)
        mock_app.input.assert_called_once()


class TestDirectEditValidation:
    """Test validation logic in direct edit bindings."""

    def test_validates_initialization(self):
        """Test that direct edit bindings initialize correctly."""
        mock_app = Mock()
        mock_app.kb = Mock()
        mock_app.kb.add = Mock(return_value=lambda func: func)
        mock_app.flag_normal_mode = True

        # Initialize bindings
        result = _init_edit_bindings(mock_app)

        # Should successfully initialize and return empty hotkeys
        assert result is not None
        assert isinstance(result, VSplit)
        assert len(result.children) == 0  # No hotkeys since not a mode


class TestDirectEditHotkeys:
    """Test the hotkey display for direct edit bindings."""

    def test_returns_empty_hotkeys(self):
        """Test that direct edit returns empty hotkeys."""
        mock_app = Mock()
        mock_app.kb = Mock()
        mock_app.kb.add = Mock(return_value=lambda func: func)
        mock_app.flag_normal_mode = True

        result = _init_edit_bindings(mock_app)

        # Should return empty VSplit since edit is not a mode
        assert isinstance(result, VSplit)
        assert len(result.children) == 0

    def test_hotkeys_structure(self):
        """Test the structure of returned hotkeys."""
        mock_app = Mock()
        mock_app.kb = Mock()
        mock_app.kb.add = Mock(return_value=lambda func: func)
        mock_app.flag_normal_mode = True

        result = _init_edit_bindings(mock_app)

        # Should return empty VSplit
        assert isinstance(result, VSplit)
        assert hasattr(result, "children")
        assert len(result.children) == 0  # No children since not a mode
