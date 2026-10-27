from tests.examples.windows import window
from tests.use_cases.starting_scene import HELPERS_TERMINAL
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.terminal_use import TerminalUse
from hiru_tsatsi.work_apps.windows import Window

KNOWN_HELPER = App("Helper", "cd code && helper", HELPERS_TERMINAL, terminal=TerminalUse.OPENS_IN_ONE)
EDITOR = App("Editor", "cd code && editor .")
RULED_OUT = App("Editor", "cd code && editor .", terminal=TerminalUse.RULED_OUT)
FAILING = App("Failing", "chromiun --app=https://example.org/")


def helper_running_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "✳ Helper", workspace, "helper", "/home/sam/code")


def a_shell_waiting_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "foot", workspace, "sh", "/home/sam")
