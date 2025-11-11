"""A module defining configuration management for h5forest.

This module provides a singleton `ConfigManager` that loads and manages
user configuration from ``~/.h5forest/config.yaml``. The initial configuration
is seeded from the packaged YAML template ``h5forest/default_config.yaml`` and
then written to the user's config directory on first run. Subsequent runs will
round-trip the user's file (preserving comments and ordering) and merge in any
new options shipped with h5forest.

Packaging
---------
Include ``h5forest/default_config.yaml`` as package data, for example:

- ``pyproject.toml``:
    [tool.setuptools.package-data]
    "h5forest" = ["default_config.yaml"]

- ``MANIFEST.in``:
    include h5forest/default_config.yaml

Dependencies
------------
- ruamel.yaml>=0.18  (round-trip YAML with preserved comments)
"""

from __future__ import annotations

import copy
import warnings
from importlib import resources as importlib_resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ruamel.yaml import YAML

from h5forest import __version__
from h5forest.errors import error_handler


class ConfigManager:
    """Singleton class to manage h5forest configuration.

    This class loads configuration from ``~/.h5forest/config.yaml`` and
    provides helpers to access values using dot notation and keymap shortcuts.
    It ensures only one instance exists throughout the application lifecycle.

    Behavior:
      - On first run, copies the packaged ``default_config.yaml`` to the user's
        config path, stamping ``version`` with the running ``__version__``.
      - On subsequent runs, loads and *round-trips* the user's config, merging
        any *new* options from the packaged template while preserving comments,
        ordering, and user values.
      - If the user's config version differs from the package template version,
        automatically updates the stored ``version`` and writes the file.

    Attributes:
        VIM_RESERVED_KEYS:
            Keys that cannot be remapped when vim mode is enabled.
    """

    # Singleton instance and initialization flag.
    _instance: Optional["ConfigManager"] = None
    _initialized: bool = False

    # Reserved keys that cannot be remapped when vim mode is enabled.
    VIM_RESERVED_KEYS: Set[str] = {"h", "j", "k", "l", "g", "G"}

    def __new__(cls, use_default: bool = False) -> "ConfigManager":
        """Ensure only one instance of :class:`ConfigManager` exists.

        Args:
            use_default: If True, forces loading default config without
                reading from disk.

        Returns:
            ConfigManager: The singleton instance.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, use_default: bool = False) -> None:
        """Initialize the ConfigManager (only happens once).

        Args:
            use_default: If True, forces loading default config without
                reading from disk.
        """
        if self._initialized:
            return

        # Are we forcing default config load?
        self._use_default = use_default

        # Paths and YAML loader configured for round-trip behavior.
        self._yaml = YAML(typ="rt")
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=4, offset=2)

        self._config_dir = Path.home() / ".h5forest"
        self._config_path = self._config_dir / "config.yaml"
        self._template_path = importlib_resources.files("h5forest").joinpath(
            "data",
            "default_config.yaml",
        )

        # Round-trip document (CommentedMap) and plain dict mirrors, used for
        # validation and lookups.
        self._config_doc: Any = None
        self._defaults_plain: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}

        self._load_config()
        ConfigManager._initialized = True

    def _ensure_config_dir_exists(self) -> None:
        """Create the config directory if it does not exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _load_default_template(self) -> Any:
        """Load the packaged default YAML template as a round-trip document.

        The template's ``version`` is overwritten with the current package
        version before returning.

        Returns:
            Any: A ruamel ``CommentedMap`` representing the template.
        """
        with importlib_resources.as_file(self._template_path) as p:
            with p.open("r", encoding="utf-8") as f:
                doc = self._yaml.load(f)
        # Stamp the runtime version into the template.
        doc["version"] = str(__version__)
        return doc

    def _create_default_config(self) -> None:
        """Create the initial user config file from the packaged template.

        Raises:
            OSError: If the file cannot be written.
        """
        self._ensure_config_dir_exists()
        tmpl = self._load_default_template()
        with self._config_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(tmpl, f)

    def _load_config(self) -> None:
        """Load configuration from disk, creating or migrating as needed.

        The algorithm is:
          1. If the user config does not exist, create it from the template.
          2. Load the user config and the packaged template as round-trip docs.
          3. Recursively add any keys missing from the user config using the
             template as reference (preserving comments).
          4. If ``version`` differs, update it and mark the document as
             changed.
          5. If changed, write the updated doc back to disk.
          6. Cache a plain-dict mirror for fast lookups and validation.

        On YAML parse errors, a warning is emitted and a fresh default config
        is written to the user's config path.

        Raises:
            OSError: If reading or writing the config file fails.
        """
        # The user's config file exists right?
        if not self._config_path.exists():
            self._create_default_config()

        # If we're forcing default config load, skip reading from disk and
        # just load the default template.
        if self._use_default:
            default_doc = self._load_default_template()
            self._config_doc = default_doc
            self._config = self._to_plain(default_doc)
            self._defaults_plain = self._to_plain(default_doc)
            return

        # Load user config, recreating on parse errors.
        try:
            with self._config_path.open("r", encoding="utf-8") as f:
                user_doc = self._yaml.load(f) or {}
        except Exception as exc:
            warnings.warn(
                f"Failed to read config at '{self._config_path}': {exc}. "
                "Using default configuration."
            )
            self._create_default_config()
            with self._config_path.open("r", encoding="utf-8") as f:
                user_doc = self._yaml.load(f) or {}

        # Load default template.
        default_doc = self._load_default_template()

        # Merge missing keys from default into user config.
        changed = self._add_missing_keys(user_doc, default_doc)

        # Update version if it differs and flag that the config has changed.
        if str(user_doc.get("version")) != str(default_doc.get("version")):
            user_doc["version"] = default_doc["version"]
            changed = True

        # If we made any changes, write back to disk including the new keys
        # and updated version.
        if changed:
            try:
                with self._config_path.open("w", encoding="utf-8") as f:
                    self._yaml.dump(user_doc, f)
            except Exception as exc:
                warnings.warn(f"Failed to write updated config: {exc}")

        # Cache both round-trip and plain forms.
        self._config_doc = user_doc
        self._config = self._to_plain(user_doc)
        self._defaults_plain = self._to_plain(default_doc)

        # Validate after load/merge.
        self._validate_config()

    @staticmethod
    def _add_missing_keys(target: Any, reference: Any) -> bool:
        """Recursively add keys from ``reference`` to ``target`` if absent.

        This operates on ruamel round-trip nodes, so comments and anchors are
        preserved when copying nodes from ``reference`` to ``target``.

        Args:
            target: The document to modify in place.
            reference: The document providing the reference structure.

        Returns:
            bool: True if ``target`` was modified; False otherwise.
        """
        changed = False
        if not isinstance(reference, dict) or not isinstance(target, dict):
            return changed

        for key, ref_val in reference.items():
            if key not in target:
                target[key] = copy.deepcopy(ref_val)
                changed = True
            else:
                tgt_val = target[key]
                if isinstance(ref_val, dict) and isinstance(tgt_val, dict):
                    if ConfigManager._add_missing_keys(tgt_val, ref_val):
                        changed = True
        return changed

    @staticmethod
    def _to_plain(node: Any) -> Any:
        """Convert a ruamel node tree to standard Python objects.

        Args:
            node: A value that may contain ruamel
                ``CommentedMap``/``CommentedSeq``.

        Returns:
            Any: The same data represented as ``dict``, ``list``, and scalars.
        """
        if isinstance(node, dict):
            return {k: ConfigManager._to_plain(v) for k, v in node.items()}
        if isinstance(node, list):
            return [ConfigManager._to_plain(x) for x in node]
        return node

    def _validate_config(self) -> None:
        """Validate configuration and protect reserved keys in vim mode.

        Emits a warning if the user attempts to remap a reserved key to an
        action that is not mapped to that key in the defaults.

        Reserved keys: ``h, j, k, l, {, }, g, G``.
        """
        vim_mode = self.get("configuration.vim_mode", False)
        if not vim_mode:
            return

        violations: List[str] = []
        keymaps = self._config.get("keymaps", {})
        for mode, bindings in keymaps.items():
            if not isinstance(bindings, dict):
                continue
            for action, key in bindings.items():
                default_for_action = (
                    self._defaults_plain.get("keymaps", {})
                    .get(mode, {})
                    .get(action)
                )
                if (
                    isinstance(key, str)
                    and key in self.VIM_RESERVED_KEYS
                    and key != default_for_action
                ):
                    violations.append(f"{mode}.{action} = '{key}'")

        if violations:
            warnings.warn(
                "The following keybindings conflict with vim_mode and will "
                "be ignored:\n"
                + "\n".join(f"  - {v}" for v in violations)
                + "\n\nVim reserved keys: "
                + ", ".join(sorted(self.VIM_RESERVED_KEYS))
                + "\nTo use these keys for other actions, disable vim mode "
                "by setting\n  configuration.vim_mode: false\n"
            )

    @error_handler
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Dot notation descends through nested mappings. Keys containing slashes
        (e.g., ``expand/collapse``) are treated as literal key names.

        Args:
            key_path: Path to the config value (e.g.,
                ``"configuration.vim_mode"``).
            default: Value to return if the path does not exist.

        Returns:
            Any: The configuration value or ``default`` if not found.

        Example:
            >>> cfg = ConfigManager()
            >>> cfg.get("configuration.vim_mode")
            False
            >>> cfg.get("keymaps.normal_mode.quit")
            'q'
        """
        keys = key_path.split(".")
        value: Any = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @error_handler
    def get_keymap(self, mode: str, action: str) -> Optional[str]:
        """Get a specific key binding for a mode and action.

        Args:
            mode: Mode name (e.g., ``"normal_mode"``, ``"tree_navigation"``).
            action: Action name (e.g., ``"quit"``, ``"move_up"``).

        Returns:
            Optional[str]: The key binding or ``None`` if not found.

        Example:
            >>> ConfigManager().get_keymap("normal_mode", "quit")
            'q'
        """
        v = self.get(f"keymaps.{mode}.{action}")

        # Ensure the result is a string if found, otherwise throw an error.
        if v is None:
            raise KeyError(
                f"Keymap for mode '{mode}' action '{action}' not found "
                f"in the config @ {self.config_path}."
            )
        elif not isinstance(v, str):
            raise ValueError(
                f"Keymap for mode '{mode}' action '{action}' is not a string."
            )
        return v

    @error_handler
    def is_vim_mode_enabled(self) -> bool:
        """Return whether vim mode is enabled.

        Returns:
            bool: True if vim mode is enabled; False otherwise.
        """
        return bool(self.get("configuration.vim_mode", False))

    @error_handler
    def always_chunk_datasets(self) -> bool:
        """Return whether datasets should always be chunked.

        Returns:
            bool: True if datasets should always be chunked; False otherwise.
        """
        return bool(self.get("configuration.always_chunk", False))

    @error_handler
    def is_key_allowed(self, key: str) -> bool:
        """Return whether a key may be used when vim mode is enabled.

        Args:
            key: A key identifier (e.g., ``"up"``, ``"{"``, ``"G"``).

        Returns:
            bool: ``True`` if the key is allowed or vim mode is disabled;
            otherwise ``False``.
        """
        if not self.is_vim_mode_enabled():
            return True
        return key not in self.VIM_RESERVED_KEYS

    @error_handler
    def reload(self) -> None:
        """Reload configuration from disk.

        Useful for testing or if the config file is modified while the
        application is running.
        """
        self._load_config()

    @property
    def config_path(self) -> Path:
        """Path to the user's ``config.yaml``."""
        return self._config_path

    @property
    def config(self) -> Dict[str, Any]:
        """A shallow copy of the full configuration dictionary.

        Returns:
            Dict[str, Any]: The loaded configuration.
        """
        return self._config.copy()


def translate_key_label(key: str) -> str:
    """Translate a prompt_toolkit key name to a nice display label.

    This function converts lower-case prompt_toolkit key identifiers into
    human-readable labels suitable for display in the UI. Single letter keys
    are left unchanged, while special keys get capitalized or formatted nicely.

    Args:
        key: A prompt_toolkit key identifier (e.g., "enter", "escape", "c-c").

    Returns:
        str: A nicely formatted label for display (e.g., "Enter", "ESC",
            "Ctrl+C").

    Examples:
        >>> translate_key_label("a")
        'a'
        >>> translate_key_label("enter")
        'Enter'
        >>> translate_key_label("escape")
        'ESC'
        >>> translate_key_label("c-c")
        'Ctrl+C'
        >>> translate_key_label("up")
        '↑'
    """
    # Mapping of prompt_toolkit key names to display labels
    key_translations = {
        # Special keys
        "enter": "Enter",
        "escape": "ESC",
        "tab": "Tab",
        "s-tab": "Shift+Tab",
        "space": "Space",
        "backspace": "⌫",
        "delete": "Del",
        # Arrow keys
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→",
        # Navigation keys
        "home": "Home",
        "end": "End",
        "pageup": "PgUp",
        "pagedown": "PgDn",
        # Function keys
        **{f"f{i}": f"F{i}" for i in range(1, 13)},
    }

    # Check if it's already in the translation map
    if key in key_translations:
        return key_translations[key]

    # Handle control keys (c-x format)
    if key.startswith("c-") and len(key) == 3:
        letter = key[2].upper()
        return f"Ctrl+{letter}"

    # Handle alt keys (a-x or m-x format)
    if (key.startswith("a-") or key.startswith("m-")) and len(key) == 3:
        letter = key[2].upper()
        return f"Alt+{letter}"

    # Handle shift keys (s-x format) for letters
    if key.startswith("s-") and len(key) == 3:
        letter = key[2].upper()
        return f"Shift+{letter}"

    # Single letter or number keys remain unchanged
    if len(key) == 1:
        return key

    # For anything else, just capitalize the first letter
    return key.capitalize()
