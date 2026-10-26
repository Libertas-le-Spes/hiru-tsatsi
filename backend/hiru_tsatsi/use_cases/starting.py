from dataclasses import dataclass, field
from typing import Callable

from hiru_tsatsi.use_cases.overview import known_window
from hiru_tsatsi.use_cases.ports import AppListStore, Desktop, Launched, WindowNames
from hiru_tsatsi.work_apps.app_list import AppList, Placement
from hiru_tsatsi.work_apps.inside import Inside
from hiru_tsatsi.work_apps.windows import Window, guess_window, name_for

WATCH_SECONDS = 60.0
POLL_SECONDS = 0.5
TERMINAL_AFTER_SECONDS = 10.0


@dataclass
class Outcome:
    already_open: list[str] = field(default_factory=list)
    started: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    unseen: list[str] = field(default_factory=list)
    in_terminal: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OwnWindowStart:
    placement: Placement
    launched: Launched
    since: float

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "OwnWindowStart":
        return cls(placement, desktop.launch(placement.app.command, placement.workspace), now)

    def needs_terminal(self, now: float) -> bool:
        return now - self.since >= TERMINAL_AFTER_SECONDS and self.launched.stopped()


@dataclass(frozen=True)
class TerminalStart:
    placement: Placement

    @classmethod
    def begin(cls, desktop: Desktop, placement: Placement, now: float) -> "TerminalStart":
        desktop.launch_in_terminal(placement.app.command, placement.workspace, placement.app.learned_window)
        return cls(placement)

    def needs_terminal(self, now: float) -> bool:
        return False


Start = OwnWindowStart | TerminalStart


class Run:
    def __init__(self, desktop: Desktop, names: WindowNames, apps: AppList, known_before: set[str], home: str):
        self.desktop = desktop
        self.home = home
        self.names = names
        self.apps = apps
        self.known_before = known_before
        self.claimed: set[str] = set()
        self.found: list[Placement] = []
        self.moved: list[Placement] = []
        self.in_terminal: list[Placement] = []

    def place(self, placements: list[Placement], windows: list[Window]) -> list[Placement]:
        ordered = [p for p in placements if p.app.knows_window] + [p for p in placements if not p.app.knows_window]
        return [p for p in ordered if not self._placed(p, windows)]

    def to_terminal(self, placement: Placement) -> Placement:
        self.apps = self.apps.with_terminal(placement)
        switched = self.apps.placement(placement.workspace, placement.index)
        self.in_terminal.append(switched)
        return switched

    def _placed(self, placement: Placement, windows: list[Window]) -> bool:
        window = self._find(placement, windows)
        if window is None:
            return False
        self.claimed.add(window.address)
        self.found.append(placement)
        self.names.record(window, placement.app.name)
        if self._learns_a_name(placement):
            self.apps = self.apps.with_learned_window(placement, name_for(window, windows, placement.app.command))
        if window.workspace != placement.workspace:
            self.desktop.move(window, placement.workspace)
            self.moved.append(placement)
        return True

    def _learns_a_name(self, placement: Placement) -> bool:
        return not placement.app.knows_window and Inside.of(placement.app.command, self.home) is None

    def _find(self, placement: Placement, windows: list[Window]) -> Window | None:
        known = known_window(placement, self.home, windows, self.claimed)
        if known or placement.app.knows_window:
            return known
        fresh = [w for w in windows if w.address not in self.known_before and w.address not in self.claimed]
        return guess_window(placement.app.name, placement.app.command, fresh)


Announce = Callable[[list[str]], None]


class StartApps:
    def __init__(self, desktop: Desktop, store: AppListStore, names: WindowNames, clock: Callable[[], float],
                 wait: Callable[[float], None], announce: Announce, home: str, watch_seconds: float = WATCH_SECONDS):
        self.desktop = desktop
        self.home = home
        self.announce = announce
        self.names = names
        self.store = store
        self.clock = clock
        self.wait = wait
        self.watch_seconds = watch_seconds

    def run(self) -> Outcome:
        apps = self.store.load()
        windows = self.desktop.windows()
        run = Run(self.desktop, self.names, apps, {w.address for w in windows}, self.home)
        missing = run.place(apps.placements(), windows)
        already_open = list(run.found)
        if missing:
            self.announce(_names(missing))
        starts = [self._begin(placement) for placement in missing]
        unseen = self._watch(run, starts)
        if run.apps != apps:
            self.store.save(run.apps)
        return self._outcome(run, already_open, missing, unseen)

    def _begin(self, placement: Placement) -> Start:
        kind = TerminalStart if placement.app.in_terminal else OwnWindowStart
        return kind.begin(self.desktop, placement, self.clock())

    def _watch(self, run: Run, starts: list[Start]) -> list[Placement]:
        deadline = self.clock() + self.watch_seconds
        awaiting = starts
        while awaiting and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            awaiting = [self._in_terminal_if_needed(run, start) for start in awaiting]
            unplaced = run.place([start.placement for start in awaiting], self.desktop.windows())
            awaiting = [start for start in awaiting if start.placement in unplaced]
        return [start.placement for start in awaiting]

    def _in_terminal_if_needed(self, run: Run, start: Start) -> Start:
        if not start.needs_terminal(self.clock()):
            return start
        return TerminalStart.begin(self.desktop, run.to_terminal(start.placement), self.clock())

    def _outcome(self, run: Run, already_open: list[Placement], missing: list[Placement], unseen: list[Placement]) -> Outcome:
        return Outcome(_names(already_open), _names(missing), _names(run.moved), _names(unseen), _names(run.in_terminal))


def _names(placements: list[Placement]) -> list[str]:
    return [p.app.name for p in placements]
