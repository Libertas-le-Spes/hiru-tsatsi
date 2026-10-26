import unittest
from unittest.mock import create_autospec

from hiru_tsatsi.use_cases.launching import Launcher
from hiru_tsatsi.use_cases.ports import Desktop, Launches, Terminal
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.placement import Placement

HELPER = Placement(2, 0, App("Helper", "cd code && helper", "hiru-tsatsi.helper-1a2b3c4d", opens_in_terminal=True))


class LaunchingAnApp(unittest.TestCase):
    def setUp(self):
        self.desktop = create_autospec(Desktop, instance=True)
        self.launches = create_autospec(Launches, instance=True)
        self.terminal = create_autospec(Terminal, instance=True)
        self.launcher = Launcher(self.desktop, self.launches, self.terminal)

    def test_plainly_hands_the_command_to_the_desktop_as_it_is(self):
        self.launcher.launch_plainly(HELPER)
        self.desktop.launch.assert_called_once_with("cd code && helper", 2)

    def test_watched_hands_over_the_command_wrapped_by_a_new_launch_and_returns_that_launch(self):
        launch = self.launches.new.return_value
        self.assertIs(self.launcher.launch_watched(HELPER), launch)
        launch.wrapped.assert_called_once_with("cd code && helper")
        self.desktop.launch.assert_called_once_with(launch.wrapped.return_value, 2)

    def test_in_a_terminal_hands_over_the_command_wrapped_for_the_apps_own_terminal_window(self):
        self.launcher.launch_in_terminal(HELPER)
        self.terminal.command_for.assert_called_once_with("cd code && helper", "hiru-tsatsi.helper-1a2b3c4d")
        self.desktop.launch.assert_called_once_with(self.terminal.command_for.return_value, 2)


if __name__ == "__main__":
    unittest.main()
