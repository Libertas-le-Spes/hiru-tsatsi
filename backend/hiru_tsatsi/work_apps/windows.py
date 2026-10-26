import re
from dataclasses import dataclass

SEPARATOR = re.compile(r" [–—·|-] ")
WORD_BREAK = re.compile(r"[\s\"'/~?&=]+")
SHORTEST_WORD = 4


@dataclass(frozen=True)
class Window:
    address: str
    window_class: str
    title: str
    workspace: int
    program: str = ""
    folder: str = ""


def _starts(text: str, prefix: str) -> bool:
    return text.lower().startswith(prefix)


def belongs_to(window: Window, name: str) -> bool:
    prefix = name.strip().lower()
    return prefix != "" and (_starts(window.window_class, prefix) or _starts(window.title, prefix))


def window_named(name: str, windows: list[Window], claimed: set[str]) -> Window | None:
    return next((w for w in windows if w.address not in claimed and belongs_to(w, name)), None)


def _words(text: str) -> list[str]:
    return [word for word in WORD_BREAK.split(text.lower()) if len(word) >= SHORTEST_WORD]


def telltale_words(command: str) -> list[str]:
    program, _, arguments = command.strip().partition(" ")
    return _words(arguments) or _words(program)


def _strength(window: Window, word: str) -> int:
    text = f"{window.window_class} {window.title}".lower()
    if word not in text:
        return 0
    leads = _starts(window.window_class, word) or _starts(window.title, word)
    return len(word) * 2 + leads


def _strongest(window: Window, words: list[str]) -> int:
    return max((_strength(window, word) for word in words), default=0)


def _clues(name: str, command: str) -> list[str]:
    return list(dict.fromkeys(telltale_words(command) + _words(name)))


def _ranked(name: str, command: str, windows: list[Window]) -> list[tuple[int, Window]]:
    words = _clues(name, command)
    return sorted(((_strongest(w, words), w) for w in windows), key=lambda pair: pair[0], reverse=True)


def guess_window(name: str, command: str, windows: list[Window]) -> Window | None:
    ranked = _ranked(name, command, windows)
    if not ranked or ranked[0][0] == 0:
        return None
    tied = len(ranked) > 1 and ranked[1][0] == ranked[0][0]
    return None if tied else ranked[0][1]


def likeliest_first(name: str, command: str, windows: list[Window]) -> list[Window]:
    return [window for _, window in _ranked(name, command, windows)]


def _title_start(title: str) -> str:
    return SEPARATOR.split(title)[0].strip()


def _shares_class(window: Window, windows: list[Window]) -> bool:
    return sum(other.window_class == window.window_class for other in windows) > 1


def _class_tells(window: Window, windows: list[Window], command: str) -> bool:
    if _shares_class(window, windows):
        return False
    words = telltale_words(command)
    return not words or any(word in window.window_class.lower() for word in words)


def name_for(window: Window, windows: list[Window], command: str = "") -> str:
    title = _title_start(window.title)
    return window.window_class if _class_tells(window, windows, command) or title == "" else title
