from hiru_tsatsi.work_apps.placement import Placement
from hiru_tsatsi.work_apps.recognising import Recognising
from hiru_tsatsi.work_apps.windows import Window


class ConfirmingTerminals:
    def __init__(self, recognising: Recognising):
        self.recognising = recognising
        self.on_trial: list[tuple[Placement, str]] = []
        self.confirmed: list[Placement] = []

    def try_out(self, placement: Placement, window: Window) -> None:
        self.on_trial.append((placement, window.address))

    @property
    def waiting(self) -> bool:
        return len(self.on_trial) > 0

    def unconfirmed(self) -> list[Placement]:
        placements = []
        for placement, _ in self.on_trial:
            placements.append(placement)
        return placements

    def newly_confirmed(self, windows: list[Window]) -> list[Placement]:
        confirmed_now = []
        still_on_trial = []
        for placement, address in self.on_trial:
            if self._runs_in_window_at(placement, address, windows):
                confirmed_now.append(placement)
            else:
                still_on_trial.append((placement, address))
        self.on_trial = still_on_trial
        self.confirmed += confirmed_now
        return confirmed_now

    def _runs_in_window_at(self, placement: Placement, address: str, windows: list[Window]) -> bool:
        for window in windows:
            if window.address == address:
                return self.recognising.runs_inside(placement.app, window)
        return False
