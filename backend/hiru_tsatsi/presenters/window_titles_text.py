def _on_or_off(on: bool) -> str:
    if on:
        return "on"
    return "off"


def _why(on: bool, chosen: bool) -> str:
    if chosen:
        return "as you chose"
    if on:
        return "because window-names is installed"
    return "because window-names isn't installed"


def window_titles_text(on: bool, chosen: bool) -> str:
    return (f"Window titles are {_on_or_off(on)}, {_why(on, chosen)}. "
            "Turn them on or off with `hiru-tsatsi window-titles on` or `off`.")
