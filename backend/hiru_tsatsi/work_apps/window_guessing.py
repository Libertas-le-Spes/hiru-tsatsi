import re

from hiru_tsatsi.work_apps.windows import Window, starts_with

WORD_BREAK = re.compile(r"[\s\"'/~?&=]+")
SHORTEST_WORD = 4


def words_in(text: str) -> list[str]:
    words = []
    for word in WORD_BREAK.split(text.lower()):
        if len(word) >= SHORTEST_WORD:
            words.append(word)
    return words


def telltale_words(command: str) -> list[str]:
    program, _, arguments = command.strip().partition(" ")
    from_arguments = words_in(arguments)
    if from_arguments:
        return from_arguments
    return words_in(program)


def _strength(window: Window, word: str) -> int:
    text = f"{window.window_class} {window.title}".lower()
    if word not in text:
        return 0
    leads = starts_with(window.window_class, word) or starts_with(window.title, word)
    return len(word) * 2 + int(leads)


def _strongest(window: Window, words: list[str]) -> int:
    strongest = 0
    for word in words:
        strongest = max(strongest, _strength(window, word))
    return strongest


def _clues(name: str, command: str) -> list[str]:
    clues = []
    for word in telltale_words(command) + words_in(name):
        if word not in clues:
            clues.append(word)
    return clues


def _ranked(name: str, command: str, windows: list[Window]) -> list[tuple[int, Window]]:
    clues = _clues(name, command)
    scored = []
    for window in windows:
        scored.append((_strongest(window, clues), window))
    return sorted(scored, key=_score, reverse=True)


def _score(scored: tuple[int, Window]) -> int:
    return scored[0]


def guess_window(name: str, command: str, windows: list[Window]) -> Window | None:
    ranked = _ranked(name, command, windows)
    if not ranked or _score(ranked[0]) == 0:
        return None
    if len(ranked) > 1 and _score(ranked[1]) == _score(ranked[0]):
        return None
    return ranked[0][1]


def likeliest_first(name: str, command: str, windows: list[Window]) -> list[Window]:
    ordered = []
    for _, window in _ranked(name, command, windows):
        ordered.append(window)
    return ordered
