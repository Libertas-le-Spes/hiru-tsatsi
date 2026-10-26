import unittest

from tests.fakes import FakeSetUp
from hiru_tsatsi.use_cases.setting_up import SetUpDesktop
from hiru_tsatsi.work_apps.shortcut import Keys

FIRST = Keys.parse("SUPER + CTRL + U")
SECOND = Keys.parse("SUPER + ALT + U")


class SettingUpTheDesktop(unittest.TestCase):
    def test_takes_the_first_free_shortcut_and_points_it_at_start(self):
        desktop = FakeSetUp(taken={FIRST})
        set_up = SetUpDesktop(desktop, "/home/me/.local/bin/hiru-tsatsi").run()
        self.assertEqual((set_up.keys, set_up.kept), (SECOND, False))
        self.assertEqual(desktop.installs, [(SECOND, "/home/me/.local/bin/hiru-tsatsi start", "/home/me/.local/bin/hiru-tsatsi ask")])

    def test_running_it_again_keeps_the_shortcut_it_already_has(self):
        desktop = FakeSetUp(taken={FIRST, SECOND}, installed=SECOND)
        set_up = SetUpDesktop(desktop, "hiru-tsatsi").run()
        self.assertEqual((set_up.keys, set_up.kept), (SECOND, True))

    def test_with_every_shortcut_taken_only_the_login_question_is_added(self):
        desktop = FakeSetUp(taken={FIRST, SECOND, Keys.parse("SUPER + SHIFT + U")})
        self.assertIsNone(SetUpDesktop(desktop, "hiru-tsatsi").run().keys)
        self.assertEqual(desktop.installs, [(None, "hiru-tsatsi start", "hiru-tsatsi ask")])

    def test_a_command_path_with_a_space_or_quote_reaches_the_shell_as_one_word(self):
        desktop = FakeSetUp(taken=set())
        SetUpDesktop(desktop, "/home/sam o'neil/.local/bin/hiru-tsatsi").run()
        quoted = "'/home/sam o'\"'\"'neil/.local/bin/hiru-tsatsi'"
        self.assertEqual(desktop.installs, [(FIRST, f"{quoted} start", f"{quoted} ask")])


if __name__ == "__main__":
    unittest.main()
