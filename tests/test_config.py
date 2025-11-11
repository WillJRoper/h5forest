"""Tests for the ConfigManager class."""

import warnings
from unittest.mock import patch

import pytest
import yaml

from h5forest import __version__
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
            "configuration": {"vim_mode": False, "always_chunk": True},
            "keymaps": {"normal_mode": {"quit": "Q"}},
        }

        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager()

        assert config.get("configuration.vim_mode") is False
        assert config.get("configuration.always_chunk") is True
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
        assert config.get("configuration.always_chunk") is False
        assert config.get("keymaps.normal_mode.quit") == "q"

    def test_handles_invalid_yaml(self, mock_home_dir):
        """Test handling of invalid YAML in config file."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create invalid YAML
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: ][")

        # Should emit a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ConfigManager()

            # Should fall back to defaults
            assert config.get("configuration.vim_mode") is False

            # Should have warning about failed config read
            assert len(w) > 0
            assert "Failed to read config" in str(w[0].message)

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
        assert move_up == "up"

    def test_get_keymap_missing_raises_error(self, mock_home_dir):
        """Test that missing keymaps raise an error."""
        config = ConfigManager()

        # The error handler wraps the KeyError, so we expect a TypeError
        # when it tries to instantiate H5Forest without required args
        with pytest.raises((KeyError, TypeError)):
            config.get_keymap("nonexistent_mode", "action")


class TestVimModeValidation:
    """Test vim mode key reservation and validation."""

    def test_reserved_keys_list(self, mock_home_dir):
        """Test that reserved keys are defined."""
        config = ConfigManager()

        expected_keys = {"h", "j", "k", "l", "g", "G"}
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

    def test_validates_config_on_load(self, mock_home_dir):
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

        # Should emit a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ConfigManager()

            # Should have warning about conflict with vim_mode
            assert len(w) > 0
            warning_message = str(w[0].message)
            assert (
                "conflict with vim_mode" in warning_message
                or "vim" in warning_message.lower()
            )

    def test_allows_reserved_keys_in_default_bindings(self, mock_home_dir):
        """Test that reserved keys are allowed in their default bindings."""
        config = ConfigManager()

        # Default bindings use arrow keys
        assert config.get_keymap("tree_navigation", "move_up") == "up"
        assert config.get_keymap("tree_navigation", "move_down") == "down"
        assert config.get_keymap("tree_navigation", "move_left") == "left"
        assert config.get_keymap("tree_navigation", "move_right") == "right"


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
        assert config.get_keymap("normal_mode", "copy_path") == "c"
        assert config.get_keymap("normal_mode", "expand_attributes") == "A"

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
        assert config.get_keymap("tree_navigation", "move_up") == "up"
        assert config.get_keymap("jump_mode", "leader") == "g"
        assert config.get_keymap("dataset_mode", "leader") == "d"


class TestConfigVersion:
    """Test configuration version tracking and migration."""

    def test_default_config_has_version(self, mock_home_dir):
        """Test that default config includes version."""
        config = ConfigManager()

        assert "version" in config.config
        assert config.get("version") == __version__

    def test_new_config_file_has_version(self, mock_home_dir):
        """Test that newly created config file has version."""
        ConfigManager()

        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        with open(config_path, "r") as f:
            content = f.read()

        assert f'version: "{__version__}"' in content

    def test_old_config_without_version_gets_migrated(self, mock_home_dir):
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

        # Version should be updated
        assert config.get("version") == __version__

        # User settings should be preserved
        assert config.get("configuration.vim_mode") is False
        assert config.get_keymap("normal_mode", "quit") == "x"

        # New defaults should be added
        assert config.get("configuration.always_chunk") is False
        assert config.get_keymap("normal_mode", "copy_path") == "c"

    def test_migration_preserves_user_settings(self, mock_home_dir):
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

        # All user settings preserved
        assert config.get("configuration.vim_mode") is False
        assert config.get_keymap("normal_mode", "quit") == "x"
        assert config.get_keymap("normal_mode", "copy_path") == "y"
        assert config.get_keymap("tree_navigation", "move_up") == "w"
        assert config.get_keymap("tree_navigation", "move_down") == "s"

        # New defaults added for missing keys
        assert config.get_keymap("normal_mode", "expand_attributes") == "A"
        assert config.get_keymap("tree_navigation", "move_left") == "left"

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
        assert updated_config["version"] == __version__

        # File should have new defaults
        assert "always_chunk" in updated_config["configuration"]
        assert "keymaps" in updated_config

    def test_same_version_no_migration(self, mock_home_dir, capsys):
        """Test that same version doesn't trigger migration."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with current version
        current_config = {
            "version": __version__,
            "configuration": {"vim_mode": True, "always_chunk": False},
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

    def test_general_exception_during_load(self, mock_home_dir, mocker):
        """Test handling of general exceptions during config load."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config file with bad content that causes exception
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: ][")

        # Should emit a warning and fall back to defaults
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ConfigManager()

            # Should have warning about failed config read
            assert len(w) > 0
            assert "Failed to read config" in str(w[0].message)

            # Config should use defaults
            assert config.get("configuration.vim_mode") is False

    def test_save_config_error_handling(self, mock_home_dir, mocker):
        """Test error handling when saving config fails."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create old config without version
        old_config = {"configuration": {"vim_mode": True}}

        with open(config_path, "w") as f:
            yaml.dump(old_config, f)

        # Mock the YAML dump method to raise an exception when writing
        from ruamel.yaml import YAML

        original_dump = YAML.dump

        def mock_dump(self, data, stream):
            if hasattr(stream, "name") and "config.yaml" in str(stream.name):
                raise PermissionError("Cannot write to file")
            return original_dump(self, data, stream)

        mocker.patch.object(YAML, "dump", mock_dump)

        # Should emit a warning about failed write
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ConfigManager()

            # Should have warning about failed config write
            assert len(w) > 0
            assert any(
                "Cannot write to file" in str(warning.message) for warning in w
            )

    def test_invalid_version_type(self, mock_home_dir):
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
        assert config.get("version") == __version__

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
            "version": __version__,
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
        initial = {"version": __version__, "configuration": {"vim_mode": True}}
        with open(config_path, "w") as f:
            yaml.dump(initial, f)

        config = ConfigManager()
        assert config.is_vim_mode_enabled() is True

        # Modify config file
        modified = {
            "version": __version__,
            "configuration": {"vim_mode": False},
        }
        with open(config_path, "w") as f:
            yaml.dump(modified, f)

        # Before reload - still old value
        assert config.is_vim_mode_enabled() is True

        # After reload - new value
        config.reload()
        assert config.is_vim_mode_enabled() is False

    def test_reload_handles_errors(self, mock_home_dir):
        """Test that reload handles errors gracefully."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        initial = {"version": __version__, "configuration": {"vim_mode": True}}
        with open(config_path, "w") as f:
            yaml.dump(initial, f)

        config = ConfigManager()

        # Corrupt the config file after initial load
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: ][")

        # Should emit a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config.reload()

            # Should have warning about failed config read
            assert len(w) > 0
            assert "Failed to read config" in str(w[0].message)


class TestConfigKeyAllowed:
    """Test is_key_allowed method edge cases."""

    def test_key_allowed_when_vim_disabled(self, mock_home_dir):
        """Test that all keys are allowed when vim mode is disabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": __version__,
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
            "version": __version__,
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

    def test_validation_with_no_vim_conflicts(self, mock_home_dir):
        """Test that validation passes with no conflicts."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Config with vim mode and no conflicts
        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": {"quit": "q", "copy_path": "c"},  # No conflicts
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Should not emit any warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ConfigManager()

            # Should have no warnings about conflicts
            conflict_warnings = [
                warning
                for warning in w
                if "conflict" in str(warning.message).lower()
            ]
            assert len(conflict_warnings) == 0

    def test_validation_with_multiple_conflicts(self, mock_home_dir):
        """Test validation reports multiple conflicts."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Config with multiple vim key conflicts
        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": {
                    "quit": "h",  # Conflict!
                    "copy_path": "j",  # Conflict!
                },
                "dataset_mode": {
                    "view_values": "k",  # Conflict!
                },
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Should emit a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ConfigManager()

            # Should have warnings for all conflicts
            assert len(w) > 0
            warning_message = str(w[0].message)
            assert "normal_mode.quit = 'h'" in warning_message
            assert "normal_mode.copy_path = 'j'" in warning_message
            assert "dataset_mode.view_values = 'k'" in warning_message


class TestTranslateKeyLabel:
    """Tests for the translate_key_label function."""

    def test_control_keys(self):
        """Test control key translation."""
        from h5forest.config import translate_key_label

        assert translate_key_label("c-c") == "Ctrl+C"
        assert translate_key_label("c-a") == "Ctrl+A"
        assert translate_key_label("c-z") == "Ctrl+Z"

    def test_alt_keys(self):
        """Test alt key translation."""
        from h5forest.config import translate_key_label

        assert translate_key_label("a-x") == "Alt+X"
        assert translate_key_label("m-x") == "Alt+X"  # m- is also alt
        assert translate_key_label("a-p") == "Alt+P"

    def test_shift_keys(self):
        """Test shift key translation."""
        from h5forest.config import translate_key_label

        assert translate_key_label("s-a") == "Shift+A"
        assert translate_key_label("s-x") == "Shift+X"

    def test_capitalize_fallback(self):
        """Test capitalize fallback for unknown keys."""
        from h5forest.config import translate_key_label

        # Test fallback for keys not in the translation map
        assert translate_key_label("insert") == "Insert"
        assert translate_key_label("scrolllock") == "Scrolllock"


class TestConfigManagerEdgeCases:
    """Tests for ConfigManager edge cases."""

    def test_use_default_config(self, mock_home_dir):
        """Test loading default config without reading from disk."""
        from h5forest.config import ConfigManager

        # Force default config by passing use_default=True
        config = ConfigManager(use_default=True)

        # Should still have basic config structure
        assert config.get("configuration.vim_mode") is False
        assert config.get("configuration.always_chunk") is False

    def test_always_chunk_datasets_true(self, mock_home_dir):
        """Test always_chunk_datasets method when enabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": False, "always_chunk": True},
            "keymaps": {},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigManager()
        assert config.always_chunk_datasets() is True

    def test_always_chunk_datasets_false(self, mock_home_dir):
        """Test always_chunk_datasets method when disabled."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": False, "always_chunk": False},
            "keymaps": {},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigManager()
        assert config.always_chunk_datasets() is False

    def test_add_missing_keys_with_non_dict(self):
        """Test _add_missing_keys with non-dict inputs."""
        from h5forest.config import ConfigManager

        # Test with non-dict target (should return False, no change)
        result = ConfigManager._add_missing_keys("not a dict", {})
        assert result is False

        # Test with non-dict reference (should return False, no change)
        result = ConfigManager._add_missing_keys({}, "not a dict")
        assert result is False

    def test_to_plain_with_list(self):
        """Test _to_plain with list input."""
        from h5forest.config import ConfigManager

        # Test with list containing dicts
        test_list = [{"a": 1}, {"b": 2}, 3]
        result = ConfigManager._to_plain(test_list)
        assert result == [{"a": 1}, {"b": 2}, 3]

    def test_validate_config_with_non_dict_keymaps(self, mock_home_dir):
        """Test _validate_config when a keymap mode value is not a dict."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with non-dict keymaps and vim_mode enabled
        # (vim_mode must be True for _validate_config to actually run)
        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": True},
            "keymaps": {
                "normal_mode": "not a dict",  # This will be skipped
                "tree_navigation": {"move_up": "up"},  # Valid
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Should not raise, just skip the invalid keymap
        config = ConfigManager()
        # Valid keymap should still work
        assert config.get_keymap("tree_navigation", "move_up") == "up"

    def test_get_keymap_with_non_string_value(self, mock_home_dir):
        """Test get_keymap raises error when keymap value is not a string."""
        config_path = mock_home_dir / ".h5forest" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config with non-string keymap value
        config_data = {
            "version": __version__,
            "configuration": {"vim_mode": False},
            "keymaps": {"normal_mode": {"quit": 123}},  # Integer, not string
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigManager()

        # Should raise ValueError for non-string keymap
        # error_handler wraps it, may try to print via H5Forest
        import warnings

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            try:
                result = config.get_keymap("normal_mode", "quit")
                # If we get here, check that error was handled
                assert result is None or isinstance(result, str)
            except (ValueError, TypeError):
                # Expected - ValueError or TypeError from H5Forest
                pass
