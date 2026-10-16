from hiru_tsatsi.presenters.outcome_text import details, summary
from hiru_tsatsi.presenters.status_lines import status_line
from hiru_tsatsi.use_cases.overview import WorkspaceView
from hiru_tsatsi.use_cases.starting import Outcome
from hiru_tsatsi.work_apps.windows import Window


def page_state(workspaces: list[WorkspaceView], window_titles: bool) -> dict:
    return {
        "windowTitles": window_titles,
        "nextNumber": max((space.number for space in workspaces), default=0) + 1,
        "workspaces": [{
            "number": space.number,
            "label": space.label,
            "apps": [{"name": view.placement.app.name, "command": view.placement.app.command,
                      "status": status_line(view), "knowsWindow": view.placement.app.knows_window}
                     for view in space.apps],
        } for space in workspaces],
    }


def window_choices(windows: list[Window]) -> list[dict]:
    return [{"address": w.address, "title": w.title or w.window_class, "workspace": w.workspace} for w in windows]


def start_report(outcome: Outcome) -> dict:
    return {"summary": summary(outcome), "details": details(outcome)}
