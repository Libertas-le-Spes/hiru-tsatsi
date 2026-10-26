from hiru_tsatsi.presenters.status_lines import status_line
from hiru_tsatsi.use_cases.overview import AppView, WorkspaceView
from hiru_tsatsi.work_apps.windows import Window


def _next_number(workspaces: list[WorkspaceView]) -> int:
    highest = 0
    for space in workspaces:
        highest = max(highest, space.number)
    return highest + 1


def _app_state(view: AppView) -> dict:
    app = view.placement.app
    return {"name": app.name, "command": app.command, "status": status_line(view), "knowsWindow": app.knows_window}


def _workspace_state(space: WorkspaceView) -> dict:
    apps = []
    for view in space.apps:
        apps.append(_app_state(view))
    return {"number": space.number, "label": space.label, "apps": apps}


def bar_state(workspaces: list[WorkspaceView], window_titles: bool) -> dict:
    spaces = []
    for space in workspaces:
        spaces.append(_workspace_state(space))
    return {"windowTitles": window_titles, "nextNumber": _next_number(workspaces), "workspaces": spaces}


def _shown_title(window: Window) -> str:
    if window.title:
        return window.title
    return window.window_class


def window_choices(windows: list[Window]) -> list[dict]:
    choices = []
    for window in windows:
        choices.append({"address": window.address, "title": _shown_title(window), "workspace": window.workspace})
    return choices
