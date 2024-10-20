from prompt_toolkit.styles import Style

style = Style.from_dict(
    {
        "group": "bold",
        "highlighted": "reverse",
        "group highlighted": "bold reverse",
        "under_cursor": "blink",
    }
)
