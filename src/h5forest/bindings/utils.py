"""A submodule containing utility functions for H5Forest bindings."""


def translate_key_label(key: str) -> str:
    """Translate a prompt_toolkit key name to a nice display label.

    This function converts lower-case prompt_toolkit key identifiers into
    human-readable labels suitable for display in the UI. Single letter keys
    are left unchanged, while special keys get capitalized or formatted nicely.

    Args:
        key: A prompt_toolkit key identifier (e.g., "enter", "escape", "c-c").

    Returns:
        str: A nicely formatted label for display (e.g., "Enter", "ESC",
            "Ctrl+C")

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
