import unittest
from unittest.mock import create_autospec

from hiru_tsatsi.use_cases.ports import DesktopSetUp
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.work_apps.shortcut import Keys

FIRST = Keys.parse("SUPER + CTRL + U")
SECOND = Keys.parse("SUPER + ALT + U")
THIRD = Keys.parse("SUPER + SHIFT + U")


def desktop_with(taken: set[Keys], installed: Keys | None = None):
    desktop = create_autospec(DesktopSetUp, instance=True)
    desktop.taken_keys.return_value = taken
    desktop.installed_keys.return_value = installed
    return desktop


class SettingUpTheDesktop(unittest.TestCase):
    def test_takes_the_first_free_shortcut_and_installs_it_once(self):
        desktop = desktop_with(taken={FIRST})
        set_up = SetUpDesktop(desktop, "/home/sam/.local/bin/hiru-tsatsi").run()
        self.assertEqual((set_up.keys, set_up.kept), (SECOND, False))
        desktop.install.assert_called_once_with(SECOND, "/home/sam/.local/bin/hiru-tsatsi start",
                                                "/home/sam/.local/bin/hiru-tsatsi ask")

    def test_running_it_again_keeps_the_shortcut_without_looking_at_taken_ones(self):
        desktop = desktop_with(taken={FIRST, SECOND}, installed=SECOND)
        set_up = SetUpDesktop(desktop, "hiru-tsatsi").run()
        self.assertEqual((set_up.keys, set_up.kept), (SECOND, True))
        desktop.taken_keys.assert_not_called()

    def test_with_every_shortcut_taken_only_the_login_question_is_added(self):
        desktop = desktop_with(taken={FIRST, SECOND, THIRD})
        self.assertIsNone(SetUpDesktop(desktop, "hiru-tsatsi").run().keys)
        desktop.install.assert_called_once_with(None, "hiru-tsatsi start", "hiru-tsatsi ask")

    def test_a_command_path_with_a_space_or_quote_reaches_the_shell_as_one_word(self):
        desktop = desktop_with(taken=set())
        SetUpDesktop(desktop, "/home/sam o'neil/.local/bin/hiru-tsatsi").run()
        quoted = "'/home/sam o'\"'\"'neil/.local/bin/hiru-tsatsi'"
        desktop.install.assert_called_once_with(FIRST, f"{quoted} start", f"{quoted} ask")


if __name__ == "__main__":
    unittest.main()
