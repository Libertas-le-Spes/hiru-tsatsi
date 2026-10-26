from dataclasses import dataclass, field


@dataclass
class Outcome:
    already_open: list[str] = field(default_factory=list)
    started: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    unseen: list[str] = field(default_factory=list)
