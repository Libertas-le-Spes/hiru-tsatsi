from dataclasses import dataclass

from hiru_tsatsi.work_apps.app import App


@dataclass(frozen=True)
class Placement:
    workspace: int
    index: int
    app: App


def names_of(placements: list[Placement]) -> list[str]:
    names = []
    for placement in placements:
        names.append(placement.app.name)
    return names
