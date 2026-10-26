from dataclasses import dataclass

from hiru_tsatsi.work_apps.app import App


@dataclass(frozen=True)
class Placement:
    workspace: int
    index: int
    app: App
