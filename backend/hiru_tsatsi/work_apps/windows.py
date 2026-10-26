from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    address: str
    window_class: str
    title: str
    workspace: int
    program: str = ""
    folder: str = ""


def starts_with(text: str, prefix: str) -> bool:
    return text.lower().startswith(prefix)


def belongs_to(window: Window, name: str) -> bool:
    prefix = name.strip().lower()
    if prefix == "":
        return False
    return starts_with(window.window_class, prefix) or starts_with(window.title, prefix)


def window_named(name: str, windows: list[Window], claimed: set[str]) -> Window | None:
    for window in windows:
        if window.address not in claimed and belongs_to(window, name):
            return window
    return None
