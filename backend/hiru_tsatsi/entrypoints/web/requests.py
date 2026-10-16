from typing import Callable

from hiru_tsatsi.presenters.page_state import page_state, start_report, window_choices

Request = Callable[[dict], dict]


def _number(body: dict, key: str) -> int:
    return int(body[key])


def _switch(body: dict, key: str) -> bool:
    if not isinstance(body[key], bool):
        raise ValueError(key)
    return body[key]


def reads(app) -> dict[str, Request]:
    return {
        "/api/list": lambda query: page_state(app.overview.run(), app.window_titles.wanted()),
        "/api/windows": lambda query: {"windows": window_choices(
            app.overview.candidates(_number(query, "workspace"), _number(query, "index")))},
    }


def changes(app) -> dict[str, Callable[[dict], object]]:
    edit = app.edit
    return {
        "/api/workspace/add": lambda b: edit.add_workspace(_number(b, "number"), str(b.get("label", ""))),
        "/api/workspace/change": lambda b: edit.change_workspace(_number(b, "number"), _number(b, "newNumber"), str(b.get("label", ""))),
        "/api/workspace/remove": lambda b: edit.remove_workspace(_number(b, "number")),
        "/api/app/add": lambda b: edit.add_app(_number(b, "workspace"), str(b.get("name", "")), str(b.get("command", ""))),
        "/api/app/change": lambda b: edit.change_app(_number(b, "workspace"), _number(b, "index"), str(b.get("name", "")), str(b.get("command", ""))),
        "/api/app/remove": lambda b: edit.remove_app(_number(b, "workspace"), _number(b, "index")),
        "/api/app/window": lambda b: edit.choose_window(_number(b, "workspace"), _number(b, "index"), str(b.get("address", ""))),
        "/api/app/forget": lambda b: edit.forget_window(_number(b, "workspace"), _number(b, "index")),
        "/api/window-titles": lambda b: app.window_titles.turn(_switch(b, "on")),
    }


def actions(app) -> dict[str, Request]:
    return {
        "/api/alive": lambda body: {},
        "/api/start": lambda body: start_report(app.start.run()),
    }
