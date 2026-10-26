from hiru_tsatsi.entrypoints.cli import bar_commands, editing_commands, setting_commands, starting_commands
from hiru_tsatsi.entrypoints.cli.command_shape import Argument, Command

WORKSPACE = Argument("workspace", int, "the workspace's number")
INDEX = Argument("index", int, "the app's position in its workspace, starting at 0")
LABEL = Argument("label", str, "its name")
NAME = Argument("name", str, "what you call it")
HOW_TO_OPEN = Argument("command", str, "how to open it")
NEW_NUMBER = Argument("new_number", int, "its new number, or the same one")
ADDRESS = Argument("address", str, "the window's address, from windows-for")
ON_OR_OFF = Argument("state", str, "on or off; leave out to see which it is", choices=("on", "off"), optional=True)

COMMANDS = {
    "start": Command(
        starting_commands.start,
        "start every work app that isn't open and put each window on its workspace"),
    "ask": Command(
        starting_commands.ask,
        "ask with a notification whether to start your work apps, and start them if you click it"),
    "add-workspace": Command(
        editing_commands.add_workspace, "add a workspace with the number you choose", [WORKSPACE, LABEL]),
    "change-workspace": Command(
        editing_commands.change_workspace, "change a workspace's number or name", [WORKSPACE, NEW_NUMBER, LABEL]),
    "remove-workspace": Command(
        editing_commands.remove_workspace, "remove a workspace and its apps", [WORKSPACE]),
    "add-app": Command(
        editing_commands.add_app, "add an app to a workspace", [WORKSPACE, NAME, HOW_TO_OPEN]),
    "change-app": Command(
        editing_commands.change_app, "change an app's name and command, keeping its place",
        [WORKSPACE, INDEX, NAME, HOW_TO_OPEN]),
    "remove-app": Command(
        editing_commands.remove_app, "remove an app from its workspace", [WORKSPACE, INDEX]),
    "window-titles": Command(
        setting_commands.window_titles, "say whether windows are named for title bars, or turn that on or off",
        [ON_OR_OFF]),
    "choose-window": Command(
        editing_commands.choose_window, "match an app to one of the open windows", [WORKSPACE, INDEX, ADDRESS]),
    "forget-window": Command(
        editing_commands.forget_window, "forget an app's window, so it is learned again next time it starts",
        [WORKSPACE, INDEX]),
    "overview": Command(
        bar_commands.overview, "print each workspace, its apps and where each app's window is, as JSON for a bar"),
    "windows-for": Command(
        bar_commands.windows_for, "print the open windows an app could be matched to, likeliest first, as JSON",
        [WORKSPACE, INDEX]),
    "set-up": Command(
        setting_commands.set_up, "add a shortcut that starts your work apps, and the question at login"),
}
