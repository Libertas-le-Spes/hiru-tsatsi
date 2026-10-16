from dataclasses import dataclass, field
from typing import Callable

from workbench.use_cases.ports import AppListStore, Desktop
from workbench.work_apps.app_list import AppList, Placement
from workbench.work_apps.windows import Window, guess_window, name_for, window_named

WATCH_SECONDS = 60.0
POLL_SECONDS = 0.5


@dataclass
class Outcome:
    already_open: list[str] = field(default_factory=list)
    started: list[str] = field(default_factory=list)
    moved: list[str] = field(default_factory=list)
    unseen: list[str] = field(default_factory=list)


class Run:
    def __init__(self, desktop: Desktop, apps: AppList, known_before: set[str]):
        self.desktop = desktop
        self.apps = apps
        self.known_before = known_before
        self.claimed: set[str] = set()
        self.found: list[Placement] = []
        self.moved: list[Placement] = []

    def place(self, placements: list[Placement], windows: list[Window]) -> list[Placement]:
        ordered = [p for p in placements if p.app.knows_window] + [p for p in placements if not p.app.knows_window]
        return [p for p in ordered if not self._placed(p, windows)]

    def _placed(self, placement: Placement, windows: list[Window]) -> bool:
        window = self._find(placement, windows)
        if window is None:
            return False
        self.claimed.add(window.address)
        self.found.append(placement)
        if not placement.app.knows_window:
            self.apps = self.apps.with_learned_window(placement, name_for(window, windows, placement.app.command))
        if window.workspace != placement.workspace:
            self.desktop.move(window, placement.workspace)
            self.moved.append(placement)
        return True

    def _find(self, placement: Placement, windows: list[Window]) -> Window | None:
        if placement.app.knows_window:
            return window_named(placement.app.learned_window, windows, self.claimed)
        fresh = [w for w in windows if w.address not in self.known_before and w.address not in self.claimed]
        return guess_window(placement.app.name, placement.app.command, fresh)


class StartApps:
    def __init__(self, desktop: Desktop, store: AppListStore, clock: Callable[[], float], wait: Callable[[float], None],
                 watch_seconds: float = WATCH_SECONDS):
        self.desktop = desktop
        self.store = store
        self.clock = clock
        self.wait = wait
        self.watch_seconds = watch_seconds

    def run(self) -> Outcome:
        apps = self.store.load()
        windows = self.desktop.windows()
        run = Run(self.desktop, apps, {w.address for w in windows})
        missing = run.place(apps.placements(), windows)
        already_open = list(run.found)
        for placement in missing:
            self.desktop.launch(placement.app.command, placement.workspace)
        unseen = self._watch(run, missing)
        if run.apps != apps:
            self.store.save(run.apps)
        return self._outcome(run, already_open, missing, unseen)

    def _watch(self, run: Run, missing: list[Placement]) -> list[Placement]:
        deadline = self.clock() + self.watch_seconds
        awaiting = missing
        while awaiting and self.clock() < deadline:
            self.wait(POLL_SECONDS)
            awaiting = run.place(awaiting, self.desktop.windows())
        return awaiting

    def _outcome(self, run: Run, already_open: list[Placement], missing: list[Placement], unseen: list[Placement]) -> Outcome:
        return Outcome(_names(already_open), _names(missing), _names(run.moved), _names(unseen))


def _names(placements: list[Placement]) -> list[str]:
    return [p.app.name for p in placements]
