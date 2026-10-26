import re

from hiru_tsatsi.work_apps.window_guessing import telltale_words
from hiru_tsatsi.work_apps.windows import Window

SEPARATOR = re.compile(r" [–—·|-] ")


def _title_start(title: str) -> str:
    return SEPARATOR.split(title)[0].strip()


def _shares_class(window: Window, windows: list[Window]) -> bool:
    same_class = 0
    for other in windows:
        if other.window_class == window.window_class:
            same_class += 1
    return same_class > 1


def _class_tells(window: Window, windows: list[Window], command: str) -> bool:
    if _shares_class(window, windows):
        return False
    words = telltale_words(command)
    if not words:
        return True
    for word in words:
        if word in window.window_class.lower():
            return True
    return False


def name_for(window: Window, windows: list[Window], command: str = "") -> str:
    title = _title_start(window.title)
    if _class_tells(window, windows, command) or title == "":
        return window.window_class
    return title
