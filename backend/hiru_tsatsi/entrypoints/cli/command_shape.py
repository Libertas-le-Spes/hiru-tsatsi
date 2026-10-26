import argparse
from dataclasses import dataclass, field
from typing import Callable

from hiru_tsatsi.use_cases.services import Services


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
    run: Callable[[Services, argparse.Namespace], int]
    help: str
    arguments: list[Argument] = field(default_factory=list)
