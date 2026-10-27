from dataclasses import dataclass, field

from hiru_tsatsi.use_cases.handover import Handover


@dataclass
class Outcome:
    already_open: list[str] = field(default_factory=list)
    started: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    unseen: list[str] = field(default_factory=list)
    stopped_without_window: list[str] = field(default_factory=list)
    for_the_offer: Handover = field(default_factory=Handover)
