from hiru_tsatsi.work_apps.windows import Window


def window(address: str, window_class: str, title: str = "", workspace: int = 1, program: str = "", folder: str = "") -> Window:
    return Window(address, window_class, title, workspace, program, folder)
