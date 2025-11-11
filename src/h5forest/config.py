"""Configuration management for h5forest.

This module provides a singleton ConfigManager class that loads and manages
user configuration from ~/.h5forest/config.yaml.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


class ConfigManager:
    """Singleton class to manage h5forest configuration.

    This class loads configuration from ~/.h5forest/config.yaml and provides
    methods to access configuration values. It ensures only one instance
    exists throughout the application lifecycle.

    The configuration supports:
    - General settings (vim_mode, etc.)
    - Custom keymaps for different modes
    - Validation to protect reserved keys
    """

    _instance: Optional["ConfigManager"] = None
    _initialized: bool = False

    # Reserved keys that cannot be remapped when vim mode is enabled
    VIM_RESERVED_KEYS: Set[str] = {
        "h",
        "j",
        "k",
        "l",
        "{",
        "}",
        "g",
        "G",
    }

    # Default configuration structure
    DEFAULT_CONFIG: Dict[str, Any] = {
        "version": "1.0",
        "configuration": {
            "vim_mode": False,
            "theme": "default",
        },
        "keymaps": {
            "normal_mode": {
                "quit": "q",
                "search": "s",
                "copy_path": "c",
                "toggle_attributes": "A",
                "restore_tree": "r",
            },
            "tree_navigation": {
                "move_up": "k",
                "move_down": "j",
                "move_left": "h",
                "move_right": "l",
                "jump_up_10": "{",
                "jump_down_10": "}",
                "expand": "l",
                "collapse": "h",
            },
            "jump_mode": {
                "leader": "g",
                "top": "g",  # gg
                "top_alt": "t",
                "bottom": "G",
                "bottom_alt": "b",
                "parent": "p",
                "next_sibling": "n",
                "jump_to_key": "K",
            },
            "dataset_mode": {
                "leader": "d",
                "view_values": "v",
                "view_values_range": "V",
                "close_values": "c",
                "min_max": "m",
                "mean": "M",
                "std_dev": "s",
            },
            "window_mode": {
                "leader": "w",
                "focus_tree": "t",
                "focus_attributes": "a",
                "focus_values": "v",
                "focus_plot": "p",
                "focus_hist": "h",
            },
            "plot_mode": {
                "leader": "p",
                "select_x": "x",
                "select_y": "y",
                "create_plot": "p",
            },
            "histogram_mode": {
                "leader": "H",
                "select_dataset": "d",
                "create_histogram": "h",
            },
            "search_mode": {
                "leader": "s",
                "exit": "escape",
            },
        },
    }

    def __new__(cls):
        """Ensure only one instance of ConfigManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the ConfigManager (only once)."""
        if not self._initialized:
            self._config_dir = Path.home() / ".h5forest"
            self._config_path = self._config_dir / "config.yaml"
            self._config: Dict[str, Any] = {}
            self._load_config()
            ConfigManager._initialized = True

    def _ensure_config_dir(self) -> None:
        """Create the config directory if it doesn't exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _create_default_config(self) -> None:
        """Create a default config file with comments."""
        self._ensure_config_dir()

        config_content = """# h5forest Configuration File
# This file controls various aspects of the h5forest TUI application.
# Location: ~/.h5forest/config.yaml

# Configuration version - DO NOT EDIT
# This is used to automatically update your config when h5forest is upgraded
version: "1.0"

# General configuration options
configuration:
  # Enable or disable vim-style key bindings (h, j, k, l for navigation)
  # Vim mode is OPTIONAL and disabled by default
  # Set to 'true' to enable vim-style navigation (h, j, k, l, g, G, {, })
  # When enabled, vim navigation keys are reserved and cannot be remapped
  vim_mode: false

  # UI theme (currently only 'default' is supported)
  theme: default

# Key mappings for different modes
# Note: Vim mode is optional and disabled by default
# If you enable vim_mode above, you cannot remap h, j, k, l, g, G, {, }
keymaps:
  # Normal mode - default mode for general operations
  normal_mode:
    quit: q
    search: s
    copy_path: c
    toggle_attributes: A
    restore_tree: r

  # Tree navigation - moving through the HDF5 structure
  tree_navigation:
    move_up: k
    move_down: j
    move_left: h
    move_right: l
    jump_up_10: "{"
    jump_down_10: "}"
    expand: l
    collapse: h

  # Jump mode - quick navigation commands (press 'g' to enter)
  jump_mode:
    leader: g
    top: g           # gg to go to top
    top_alt: t       # Alternative: just 't' in jump mode
    bottom: G
    bottom_alt: b
    parent: p
    next_sibling: n
    jump_to_key: K

  # Dataset mode - operations on datasets (press 'd' to enter)
  dataset_mode:
    leader: d
    view_values: v
    view_values_range: V
    close_values: c
    min_max: m
    mean: M
    std_dev: s

  # Window mode - focus management (press 'w' to enter)
  window_mode:
    leader: w
    focus_tree: t
    focus_attributes: a
    focus_values: v
    focus_plot: p
    focus_hist: h

  # Plot mode - scatter plot creation (press 'p' to enter)
  plot_mode:
    leader: p
    select_x: x
    select_y: y
    create_plot: p

  # Histogram mode - histogram creation (press 'H' to enter)
  histogram_mode:
    leader: H
    select_dataset: d
    create_histogram: h

  # Search mode - fuzzy search (press 's' to enter)
  search_mode:
    leader: s
    exit: escape
"""

        with open(self._config_path, "w") as f:
            f.write(config_content)

    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        if not self._config_path.exists():
            self._create_default_config()

        try:
            with open(self._config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}

            # Merge user config with defaults (defaults as base)
            self._config = self._deep_merge(
                self.DEFAULT_CONFIG.copy(), user_config
            )

            # Check if config needs migration to newer version
            self._migrate_config_if_needed(user_config)

            # Validate configuration
            self._validate_config()

        except yaml.YAMLError as e:
            print(
                f"Error parsing config file {self._config_path}: {e}\n"
                "Using default configuration."
            )
            self._config = self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(
                f"Error loading config file {self._config_path}: {e}\n"
                "Using default configuration."
            )
            self._config = self.DEFAULT_CONFIG.copy()

    def _migrate_config_if_needed(self, user_config: Dict[str, Any]) -> None:
        """Migrate config to newer version if needed.

        Compares the version in user config with the current default version.
        If they differ, adds new configuration options while preserving user
        settings, then saves the updated config.

        Args:
            user_config: User's loaded configuration
        """
        user_version = user_config.get("version", "0.0")
        current_version = self.DEFAULT_CONFIG.get("version", "1.0")

        if user_version != current_version:
            print(
                f"Migrating config from version {user_version} to "
                f"{current_version}..."
            )

            # Config has already been merged with defaults in _load_config
            # Now we just need to update the version and save
            self._config["version"] = current_version

            # Save the updated config
            self._save_config()

            print(
                "Config migrated successfully. New options added while "
                "preserving your custom settings."
            )

    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self._config_path, "w") as f:
                yaml.dump(
                    self._config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence.

        Args:
            base: Base dictionary (defaults)
            override: Override dictionary (user config)

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _validate_config(self) -> None:
        """Validate configuration and protect reserved keys.

        Raises warnings if user tries to remap reserved keys when vim_mode
        is enabled.
        """
        vim_mode = self.get("configuration.vim_mode", False)

        if vim_mode:
            violations: List[str] = []

            # Check all keymaps for violations
            keymaps = self._config.get("keymaps", {})
            for mode, bindings in keymaps.items():
                if isinstance(bindings, dict):
                    for action, key in bindings.items():
                        if (
                            key in self.VIM_RESERVED_KEYS
                            and key
                            != self.DEFAULT_CONFIG["keymaps"]
                            .get(mode, {})
                            .get(action)
                        ):
                            violations.append(f"{mode}.{action} = '{key}'")

            if violations:
                print(
                    "WARNING: The following keybindings conflict with "
                    "vim_mode and will be ignored:"
                )
                for violation in violations:
                    print(f"  - {violation}")
                print(
                    "\nVim reserved keys: "
                    f"{', '.join(sorted(self.VIM_RESERVED_KEYS))}"
                )
                print(
                    "To use these keys for other actions, disable vim mode by setting\n"
                    "'configuration.vim_mode: false' in your config.\n"
                )

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key_path: Path to config value (e.g., "configuration.vim_mode")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config = ConfigManager()
            >>> config.get("configuration.vim_mode")
            True
            >>> config.get("keymaps.normal_mode.quit")
            'q'
        """
        keys = key_path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_keymap(self, mode: str, action: str) -> Optional[str]:
        """Get a specific key binding for a mode and action.

        Args:
            mode: Mode name (e.g., "normal_mode", "tree_navigation")
            action: Action name (e.g., "quit", "move_up")

        Returns:
            Key binding or None if not found

        Example:
            >>> config = ConfigManager()
            >>> config.get_keymap("normal_mode", "quit")
            'q'
        """
        return self.get(f"keymaps.{mode}.{action}")

    def is_vim_mode_enabled(self) -> bool:
        """Check if vim mode is enabled.

        Returns:
            True if vim mode is enabled, False otherwise
        """
        return self.get("configuration.vim_mode", False)

    def is_key_allowed(self, key: str) -> bool:
        """Check if a key is allowed to be used (not reserved by vim mode).

        Args:
            key: Key to check

        Returns:
            True if key can be used, False if reserved
        """
        if not self.is_vim_mode_enabled():
            return True

        return key not in self.VIM_RESERVED_KEYS

    def reload(self) -> None:
        """Reload configuration from file.

        Useful for testing or if config file is modified while app is running.
        """
        self._load_config()

    @property
    def config_path(self) -> Path:
        """Get the path to the config file.

        Returns:
            Path to config.yaml
        """
        return self._config_path

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary.

        Returns:
            Complete configuration
        """
        return self._config.copy()
