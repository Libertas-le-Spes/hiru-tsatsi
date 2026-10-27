from dataclasses import dataclass, field

from hiru_tsatsi.work_apps.placement import Placement


@dataclass(frozen=True)
class Handover:
    stopped: list[Placement] = field(default_factory=list)
    taken: set[str] = field(default_factory=set)
