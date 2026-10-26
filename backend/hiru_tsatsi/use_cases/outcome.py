from dataclasses import dataclass, field

from hiru_tsatsi.work_apps.placement import Placement


@dataclass
class Outcome:
    already_open: list[str] = field(default_factory=list)
    started: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    unseen: list[str] = field(default_factory=list)
    stopped_without_window: list[Placement] = field(default_factory=list)
