from workbench.presenters.outcome_text import details, summary
from workbench.presenters.status_lines import status_line
from workbench.use_cases.overview import WorkspaceView
from workbench.use_cases.starting import Outcome
from workbench.work_apps.windows import Window


def page_state(workspaces: list[WorkspaceView]) -> dict:
    return {
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
