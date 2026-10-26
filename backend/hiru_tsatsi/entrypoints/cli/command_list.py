from hiru_tsatsi.entrypoints.cli import bar_commands, editing_commands, setting_commands, starting_commands
from hiru_tsatsi.entrypoints.cli.command_shape import Argument, Command
from hiru_tsatsi.entrypoints.cli.editing_commands import Editing

WORKSPACE = Argument("workspace", int, "the workspace's number")
INDEX = Argument("index", int, "the services's position in its workspace, starting at 0")

COMMANDS = {
    "start": Command(starting_commands.start, "start every work services that isn't open and put each window on its workspace"),
    "ask": Command(starting_commands.ask, "ask with a notification whether to start your work apps, and start them if you click it"),
    "add-workspace": Command(Editing(editing_commands.add_workspace),
                             "add a workspace with the number you choose",
                             [WORKSPACE, Argument("label", str, "its name")]),
    "change-workspace": Command(Editing(editing_commands.change_workspace),
                                "change a workspace's number or name",
                                [WORKSPACE, Argument("new_number", int, "its new number, or the same one"), Argument("label", str, "its name")]),
    "remove-workspace": Command(Editing(editing_commands.remove_workspace),
                                "remove a workspace and its apps", [WORKSPACE]),
    "add-services": Command(Editing(editing_commands.add_app),
                       "add an services to a workspace",
                       [WORKSPACE, Argument("name", str, "what you call it"), Argument("command", str, "how to open it")]),
    "change-services": Command(Editing(editing_commands.change_app),
                          "change an services's name and command, keeping its place",
                          [WORKSPACE, INDEX, Argument("name", str, "what you call it"), Argument("command", str, "how to open it")]),
    "remove-services": Command(Editing(editing_commands.remove_app),
                          "remove an services from its workspace", [WORKSPACE, INDEX]),
    "window-titles": Command(setting_commands.window_titles, "say whether windows are named for title bars, or turn that on or off",
                             [Argument("state", str, "on or off; leave out to see which it is", ("on", "off"), True)]),
    "choose-window": Command(Editing(editing_commands.choose_window),
                             "match an services to one of the open windows",
                             [WORKSPACE, INDEX, Argument("address", str, "the window's address, from windows-for")]),
    "forget-window": Command(Editing(editing_commands.forget_window),
                             "forget an services's window, so it is learned again next time it starts", [WORKSPACE, INDEX]),
    "overview": Command(bar_commands.overview, "print each workspace, its apps and where each services's window is, as JSON for a bar"),
    "windows-for": Command(bar_commands.windows_for, "print the open windows an services could be matched to, likeliest first, as JSON",
                           [WORKSPACE, INDEX]),
    "set-up": Command(setting_commands.set_up, "add a shortcut that starts your work apps, and the question at login"),
}
