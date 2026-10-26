import argparse
from dataclasses import dataclass, field
from typing import Callable

from hiru_tsatsi.wiring import App


@dataclass(frozen=True)
class Argument:
    name: str
    kind: type
    help: str
    choices: tuple[str, ...] | None = None
    optional: bool = False

    def how_many(self) -> str | None:
        if self.optional:
            return "?"
        return None


@dataclass(frozen=True)
class Command:
    run: Callable[[App, argparse.Namespace], int]
    help: str
    arguments: list[Argument] = field(default_factory=list)
