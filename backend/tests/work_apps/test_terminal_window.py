import unittest

from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.terminal_window import in_a_terminal, terminal_window_name


class NamingATerminalWindow(unittest.TestCase):
    def test_named_after_the_app_and_a_fingerprint_of_its_command(self):
        name = terminal_window_name(App("Main Helper!", "cd code && helper"))
        self.assertRegex(name, r"^hiru-tsatsi\.main-helper-[0-9a-f]{8}$")

    def test_the_same_app_gets_the_same_name_wherever_it_sits(self):
        self.assertEqual(terminal_window_name(App("Helper", "cd code && helper")),
                         terminal_window_name(App("Helper", "cd code && helper")))

    def test_two_apps_with_the_same_name_but_different_commands_get_different_names(self):
        self.assertNotEqual(terminal_window_name(App("Helper", "cd code && helper")),
                            terminal_window_name(App("Helper", "cd other && helper")))

    def test_an_app_in_a_terminal_remembers_that_name(self):
        app = in_a_terminal(App("Helper", "cd code && helper"))
        self.assertEqual((app.in_terminal, app.learned_window), (True, terminal_window_name(app)))


if __name__ == "__main__":
    unittest.main()
