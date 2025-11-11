"""Tests for the ConfigManager class."""

from unittest.mock import patch

import pytest
import yaml

from h5forest.config import ConfigManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / ".h5forest"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create a temporary config file for testing."""
    config_path = temp_config_dir / "config.yaml"
    return config_path


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset the ConfigManager singleton instance between tests."""
    ConfigManager._instance = None
    ConfigManager._initialized = False
    yield
    ConfigManager._instance = None
    ConfigManager._initialized = False


@pytest.fixture
def mock_home_dir(temp_config_dir):
    """Mock Path.home() to use temp directory."""
    with patch("h5forest.config.Path.home") as mock_home:
        mock_home.return_value = temp_config_dir.parent
        yield temp_config_dir.parent


class TestConfigManagerSingleton:
    """Test ConfigManager singleton behavior."""

    def test_singleton_instance(self, mock_home_dir):
        """Test that ConfigManager is a singleton."""
        config1 = ConfigManager()
        config2 = ConfigManager()

        assert config1 is config2

    def test_singleton_initialized_once(self, mock_home_dir):
        """Test that ConfigManager is initialized only once."""
        config1 = ConfigManager()
        config1._config["test"] = "value"

        config2 = ConfigManager()

        # Should have the same config since it's the same instance
        assert "test" in config2._config
        assert config2._config["test"] == "value"


class TestConfigFileCreation:
    """Test config file creation and default values."""

    def test_creates_config_directory(self, mock_home_dir):
        """Test that config directory is created if it doesn't exist."""
        # Use a different temp directory without .h5forest
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_dir = tmp_path / ".h5forest"

            # Directory shouldn't exist yet
            assert not config_dir.exists()

            with patch("h5forest.config.Path.home") as mock_home:
                mock_home.return_value = tmp_path
                ConfigManager()

            # Directory should now exist
            assert config_dir.exists()
            assert config_dir.is_dir()

    def test_creates_default_config_file(self, mock_home_dir):
        """Test that default config file is created if it doesn't exist."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"

        assert not config_path.exists()

        ConfigManager()

        assert config_path.exists()
        assert config_path.is_file()

    def test_default_config_is_valid_yaml(self, mock_home_dir):
        """Test that default config file contains valid YAML."""
        ConfigManager()

        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict)
        assert "configuration" in config
        assert "keymaps" in config

    def test_default_vim_mode_disabled(self, mock_home_dir):
        """Test that vim mode is disabled by default."""
        config = ConfigManager()

        assert config.is_vim_mode_enabled() is False
        assert config.get("configuration.vim_mode") is False


class TestConfigLoading:
    """Test configuration loading from file."""

    def test_loads_existing_config(self, mock_home_dir):
        """Test loading an existing config file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create custom config
        custom_config = {
            "configuration": {"vim_mode": False, "theme": "custom"},
            "keymaps": {"normal_mode": {"quit": "Q"}},
        }

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        assert config.get("configuration.vim_mode") is False
        assert config.get("configuration.theme") == "custom"
        assert config.get("keymaps.normal_mode.quit") == "Q"

    def test_merges_with_defaults(self, mock_home_dir):
        """Test that user config is merged with defaults."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create partial config (only override vim_mode)
        custom_config = {"configuration": {"vim_mode": False}}

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # User override
        assert config.get("configuration.vim_mode") is False

        # Default values still present
        assert config.get("configuration.theme") == "default"
        assert config.get("keymaps.normal_mode.quit") == "q"

    def test_handles_invalid_yaml(self, mock_home_dir, capsys):
        """Test handling of invalid YAML in config file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create invalid YAML
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: ][")

        config = ConfigManager()

        # Should fall back to defaults
        assert config.get("configuration.vim_mode") is False

        # Should print error message
        captured = capsys.readouterr()
        assert "Error parsing config file" in captured.out

    def test_handles_missing_sections(self, mock_home_dir):
        """Test handling config files with missing sections."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with only configuration section
        custom_config = {"configuration": {"vim_mode": False}}

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # User config
        assert config.get("configuration.vim_mode") is False

        # Defaults should fill in missing keymaps
        assert config.get("keymaps.normal_mode.quit") == "q"


class TestGetMethods:
    """Test configuration retrieval methods."""

    def test_get_simple_key(self, mock_home_dir):
        """Test getting a simple key."""
        config = ConfigManager()

        vim_mode = config.get("configuration.vim_mode")
        assert vim_mode is False

    def test_get_nested_key(self, mock_home_dir):
        """Test getting a nested key using dot notation."""
        config = ConfigManager()

        quit_key = config.get("keymaps.normal_mode.quit")
        assert quit_key == "q"

    def test_get_missing_key_returns_default(self, mock_home_dir):
        """Test that missing keys return the default value."""
        config = ConfigManager()

        result = config.get("nonexistent.key", "default_value")
        assert result == "default_value"

    def test_get_keymap(self, mock_home_dir):
        """Test getting keymap values."""
        config = ConfigManager()

        quit_key = config.get_keymap("normal_mode", "quit")
        assert quit_key == "q"

        move_up = config.get_keymap("tree_navigation", "move_up")
        assert move_up == "k"

    def test_get_keymap_missing_returns_none(self, mock_home_dir):
        """Test that missing keymaps return None."""
        config = ConfigManager()

        result = config.get_keymap("nonexistent_mode", "action")
        assert result is None


class TestVimModeValidation:
    """Test vim mode key reservation and validation."""

    def test_reserved_keys_list(self, mock_home_dir):
        """Test that reserved keys are defined."""
        config = ConfigManager()

        expected_keys = {"h", "j", "k", "l", "{", "}", "g", "G"}
        assert config.VIM_RESERVED_KEYS == expected_keys

    def test_is_key_allowed_with_vim_mode(self, mock_home_dir):
        """Test key validation with vim mode enabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        custom_config = {"configuration": {"vim_mode": True}}

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # Reserved keys should not be allowed
        assert config.is_key_allowed("h") is False
        assert config.is_key_allowed("j") is False
        assert config.is_key_allowed("k") is False
        assert config.is_key_allowed("l") is False

        # Non-reserved keys should be allowed
        assert config.is_key_allowed("q") is True
        assert config.is_key_allowed("s") is True
        assert config.is_key_allowed("A") is True

    def test_is_key_allowed_without_vim_mode(self, mock_home_dir):
        """Test key validation with vim mode disabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        custom_config = {"configuration": {"vim_mode": False}}

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # All keys should be allowed when vim mode is off
        assert config.is_key_allowed("h") is True
        assert config.is_key_allowed("j") is True
        assert config.is_key_allowed("k") is True
        assert config.is_key_allowed("l") is True

    def test_validates_config_on_load(self, mock_home_dir, capsys):
        """Test that config validation runs on load."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Try to remap a reserved key with vim mode enabled
        custom_config = {
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": {"quit": "j"}  # Try to use reserved key
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        # Should print warning
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "vim_mode" in captured.out

    def test_allows_reserved_keys_in_default_bindings(self, mock_home_dir):
        """Test that reserved keys are allowed in their default bindings."""
        config = ConfigManager()

        # Default bindings use reserved keys, which should be OK
        assert config.get_keymap("tree_navigation", "move_up") == "k"
        assert config.get_keymap("tree_navigation", "move_down") == "j"
        assert config.get_keymap("tree_navigation", "move_left") == "h"
        assert config.get_keymap("tree_navigation", "move_right") == "l"


class TestConfigProperties:
    """Test ConfigManager properties."""

    def test_config_path_property(self, mock_home_dir):
        """Test config_path property returns correct path."""
        config = ConfigManager()

        expected_path = mock_home_dir / ".h5forest" / "config.yaml"
        assert config.config_path == expected_path

    def test_config_property_returns_copy(self, mock_home_dir):
        """Test that config property returns a copy, not reference."""
        config = ConfigManager()

        config_dict = config.config
        config_dict["test"] = "modified"

        # Original should be unchanged
        assert "test" not in config.config


class TestConfigReload:
    """Test configuration reloading."""

    def test_reload_updates_config(self, mock_home_dir):
        """Test that reload updates configuration from file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Initial config
        initial_config = {"configuration": {"vim_mode": True}}
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        config = ConfigManager()
        assert config.is_vim_mode_enabled() is True

        # Modify config file
        updated_config = {"configuration": {"vim_mode": False}}
        with open(config_path, "w") as f:
            yaml.dump(updated_config, f)

        # Reload
        config.reload()

        assert config.is_vim_mode_enabled() is False


class TestDeepMerge:
    """Test deep merge functionality."""

    def test_deep_merge_nested_dicts(self, mock_home_dir):
        """Test that nested dictionaries are merged correctly."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Override only one keymap in normal_mode
        custom_config = {
            "keymaps": {
                "normal_mode": {
                    "quit": "Q"  # Override this
                    # search, copy_path, etc. should use defaults
                }
            }
        }

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # Custom override
        assert config.get_keymap("normal_mode", "quit") == "Q"

        # Defaults preserved
        assert config.get_keymap("normal_mode", "search") == "s"
        assert config.get_keymap("normal_mode", "copy_path") == "c"

    def test_deep_merge_preserves_other_modes(self, mock_home_dir):
        """Test that modifying one mode doesn't affect others."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Only modify normal_mode
        custom_config = {"keymaps": {"normal_mode": {"quit": "Q"}}}

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        # Other modes should still have defaults
        assert config.get_keymap("tree_navigation", "move_up") == "k"
        assert config.get_keymap("jump_mode", "leader") == "g"
        assert config.get_keymap("dataset_mode", "leader") == "d"


class TestConfigVersion:
    """Test configuration version tracking and migration."""

    def test_default_config_has_version(self, mock_home_dir):
        """Test that default config includes version."""
        config = ConfigManager()

        assert "version" in config.config
        assert config.get("version") == "1.0"

    def test_new_config_file_has_version(self, mock_home_dir):
        """Test that newly created config file has version."""
        ConfigManager()

        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        with open(config_path, "r") as f:
            content = f.read()

        assert 'version: "1.0"' in content

    def test_old_config_without_version_gets_migrated(
        self, mock_home_dir, capsys
    ):
        """Test that config without version gets migrated."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create old config without version
        old_config = {
            "configuration": {"vim_mode": False},
            "keymaps": {"normal_mode": {"quit": "x"}},
        }

        with open(config_path, "w") as f:
            yaml.dump(old_config, f)

        config = ConfigManager()

        # Should have migrated
        captured = capsys.readouterr()
        assert "Migrating config from version 0.0 to 1.0" in captured.out
        assert "Config migrated successfully" in captured.out

        # Version should be updated
        assert config.get("version") == "1.0"

        # User settings should be preserved
        assert config.get("configuration.vim_mode") is False
        assert config.get_keymap("normal_mode", "quit") == "x"

        # New defaults should be added
        assert config.get("configuration.theme") == "default"
        assert config.get_keymap("normal_mode", "search") == "s"

    def test_migration_preserves_user_settings(self, mock_home_dir, capsys):
        """Test that migration preserves all user customizations."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create old config with custom settings
        old_config = {
            "version": "0.9",  # Old version
            "configuration": {"vim_mode": False},
            "keymaps": {
                "normal_mode": {
                    "quit": "x",
                    "search": "f",
                    "copy_path": "y",
                },
                "tree_navigation": {
                    "move_up": "w",
                    "move_down": "s",
                },
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(old_config, f)

        config = ConfigManager()

        # Should have migrated
        captured = capsys.readouterr()
        assert "Migrating config from version 0.9 to 1.0" in captured.out

        # All user settings preserved
        assert config.get("configuration.vim_mode") is False
        assert config.get_keymap("normal_mode", "quit") == "x"
        assert config.get_keymap("normal_mode", "search") == "f"
        assert config.get_keymap("normal_mode", "copy_path") == "y"
        assert config.get_keymap("tree_navigation", "move_up") == "w"
        assert config.get_keymap("tree_navigation", "move_down") == "s"

        # New defaults added for missing keys
        assert config.get_keymap("normal_mode", "expand_attributes") == "A"
        assert config.get_keymap("tree_navigation", "move_left") == "h"

    def test_migration_updates_config_file(self, mock_home_dir):
        """Test that migration saves updated config to file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create old config
        old_config = {
            "configuration": {"vim_mode": True},
        }

        with open(config_path, "w") as f:
            yaml.dump(old_config, f)

        ConfigManager()

        # Read the updated file
        with open(config_path, "r") as f:
            updated_config = yaml.safe_load(f)

        # File should have version now
        assert updated_config["version"] == "1.0"

        # File should have new defaults
        assert "theme" in updated_config["configuration"]
        assert "keymaps" in updated_config

    def test_same_version_no_migration(self, mock_home_dir, capsys):
        """Test that same version doesn't trigger migration."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with current version
        current_config = {
            "version": "1.0",
            "configuration": {"vim_mode": True, "theme": "default"},
            "keymaps": {"normal_mode": {"quit": "q"}},
        }

        with open(config_path, "w") as f:
            yaml.dump(current_config, f)

        ConfigManager()

        # Should NOT have migrated
        captured = capsys.readouterr()
        assert "Migrating config" not in captured.out


class TestConfigErrorHandling:
    """Test configuration error handling and edge cases."""

    def test_general_exception_during_load(
        self, mock_home_dir, capsys, mocker
    ):
        """Test handling of general exceptions during config load."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create valid config file
        with open(config_path, "w") as f:
            yaml.dump({"configuration": {"vim_mode": True}}, f)

        # Mock open to raise a general exception (not YAMLError)
        mocker.patch(
            "builtins.open",
            side_effect=PermissionError("Permission denied"),
        )

        config = ConfigManager()

        # Should fall back to defaults
        captured = capsys.readouterr()
        assert "Error loading config file" in captured.out
        assert "Permission denied" in captured.out

        # Config should use defaults
        assert config.get("configuration.vim_mode") is False

    def test_save_config_error_handling(self, mock_home_dir, capsys, mocker):
        """Test error handling when saving config fails."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create old config without version
        old_config = {"configuration": {"vim_mode": True}}

        with open(config_path, "w") as f:
            yaml.dump(old_config, f)

        # Mock open for writing to raise exception
        original_open = open

        def mock_open(*args, **kwargs):
            if len(args) > 1 and args[1] == "w":
                raise PermissionError("Cannot write to file")
            return original_open(*args, **kwargs)

        mocker.patch("builtins.open", side_effect=mock_open)

        ConfigManager()

        # Should have tried to migrate and save
        captured = capsys.readouterr()
        assert "Migrating config" in captured.out
        assert "Error saving config file" in captured.out

    def test_invalid_version_type(self, mock_home_dir, capsys):
        """Test handling of invalid version type in config."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with non-string version
        invalid_config = {
            "version": 1.0,  # Number instead of string
            "configuration": {"vim_mode": True},
        }

        with open(config_path, "w") as f:
            yaml.dump(invalid_config, f)

        config = ConfigManager()

        # Should handle it gracefully - version will be compared as number
        # and likely trigger migration
        assert config.get("version") == "1.0"

    def test_missing_config_sections(self, mock_home_dir):
        """Test handling of config with completely missing sections."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with no sections at all
        empty_config = {}

        with open(config_path, "w") as f:
            yaml.dump(empty_config, f)

        config = ConfigManager()

        # Should merge with defaults
        assert config.get("configuration.vim_mode") is False
        assert config.get_keymap("normal_mode", "quit") == "q"

    def test_null_config_file(self, mock_home_dir):
        """Test handling of null/empty config file content."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create empty file
        config_path.touch()

        config = ConfigManager()

        # yaml.safe_load on empty file returns None, which we handle
        assert config.get("configuration.vim_mode") is False

    def test_config_with_extra_unknown_keys(self, mock_home_dir):
        """Test that unknown keys in config don't break anything."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with unknown keys
        config_with_extras = {
            "version": "1.0",
            "configuration": {
                "vim_mode": True,
                "unknown_option": "value",
            },
            "unknown_section": {"key": "value"},
            "keymaps": {"normal_mode": {"quit": "q"}},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_with_extras, f)

        config = ConfigManager()

        # Should load without errors
        assert config.get("configuration.vim_mode") is True
        # Unknown keys are preserved
        assert config.get("configuration.unknown_option") == "value"


class TestConfigReloadMethod:
    """Test the reload() method thoroughly."""

    def test_reload_picks_up_changes(self, mock_home_dir):
        """Test that reload picks up changes made to config file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Initial config
        initial = {"version": "1.0", "configuration": {"vim_mode": True}}
        with open(config_path, "w") as f:
            yaml.dump(initial, f)

        config = ConfigManager()
        assert config.is_vim_mode_enabled() is True

        # Modify config file
        modified = {"version": "1.0", "configuration": {"vim_mode": False}}
        with open(config_path, "w") as f:
            yaml.dump(modified, f)

        # Before reload - still old value
        assert config.is_vim_mode_enabled() is True

        # After reload - new value
        config.reload()
        assert config.is_vim_mode_enabled() is False

    def test_reload_handles_errors(self, mock_home_dir, capsys, mocker):
        """Test that reload handles errors gracefully."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        initial = {"version": "1.0", "configuration": {"vim_mode": True}}
        with open(config_path, "w") as f:
            yaml.dump(initial, f)

        config = ConfigManager()

        # Make file unreadable by raising exception
        mocker.patch("builtins.open", side_effect=PermissionError("No access"))

        config.reload()

        # Should have error message
        captured = capsys.readouterr()
        assert "Error loading config file" in captured.out


class TestConfigKeyAllowed:
    """Test is_key_allowed method edge cases."""

    def test_key_allowed_when_vim_disabled(self, mock_home_dir):
        """Test that all keys are allowed when vim mode is disabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": "1.0",
            "configuration": {"vim_mode": False},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigManager()

        # All reserved keys should be allowed
        for key in config.VIM_RESERVED_KEYS:
            assert config.is_key_allowed(key) is True

        # Non-reserved keys also allowed
        assert config.is_key_allowed("q") is True
        assert config.is_key_allowed("x") is True

    def test_key_allowed_when_vim_enabled(self, mock_home_dir):
        """Test key restrictions when vim mode is enabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": "1.0",
            "configuration": {"vim_mode": True},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigManager()

        # Reserved keys should NOT be allowed
        for key in config.VIM_RESERVED_KEYS:
            assert config.is_key_allowed(key) is False

        # Non-reserved keys should be allowed
        assert config.is_key_allowed("q") is True
        assert config.is_key_allowed("x") is True
        assert config.is_key_allowed("A") is True


class TestConfigValidationEdgeCases:
    """Test configuration validation edge cases."""

    def test_validation_with_no_vim_conflicts(self, mock_home_dir, capsys):
        """Test that validation passes with no conflicts."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Config with vim mode and no conflicts
        config_data = {
            "version": "1.0",
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": {"quit": "q", "search": "s"},  # No conflicts
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        ConfigManager()

        # Should have no warnings
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out

    def test_validation_with_multiple_conflicts(self, mock_home_dir, capsys):
        """Test validation reports multiple conflicts."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Config with multiple vim key conflicts
        config_data = {
            "version": "1.0",
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": {
                    "quit": "h",  # Conflict!
                    "search": "j",  # Conflict!
                },
                "dataset_mode": {
                    "view_values": "k",  # Conflict!
                },
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        ConfigManager()

        # Should have warnings for all conflicts
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "normal_mode.quit = 'h'" in captured.out
        assert "normal_mode.search = 'j'" in captured.out
        assert "dataset_mode.view_values = 'k'" in captured.out
