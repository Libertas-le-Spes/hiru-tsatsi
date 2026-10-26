import json
import unittest
from pathlib import Path

from tests.adapters.mocked_files import files_holding, written
from hiru_tsatsi.adapters.desktops.hyprland_set_up import HyprlandSetUp
from hiru_tsatsi.use_cases.failures import NotSaved, SetUpFailed
from hiru_tsatsi.work_apps.shortcut import Keys

FOLDER = Path("/home/sam/.config/hypr")
MAIN = FOLDER / "hyprland.lua"
OWN = FOLDER / "hiru-tsatsi.lua"
MAIN_BEFORE = 'require("hypr.bindings")\n'
LOADS_OWN = f'dofile("{OWN}")'
BINDS = [{"modmask": 68, "key": "U", "submap": ""}, {"modmask": 64, "key": "return", "submap": ""},
         {"modmask": 72, "key": "U", "submap": "resize"}]


class FakeHyprctl:
    def __init__(self, errors: str = ""):
        self.errors = errors
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> str:
        self.calls.append(arguments)
        if arguments[0] == "binds":
            return json.dumps(BINDS)
        if arguments[0] == "configerrors":
            return self.errors
        return "ok"


class SettingUpHyprland(unittest.TestCase):
    def setUp(self):
        self.files = files_holding({MAIN: MAIN_BEFORE})
        self.hyprctl = FakeHyprctl()
        self.set_up = HyprlandSetUp(FOLDER, self.files, self.hyprctl)

    def test_reads_which_shortcuts_are_taken_outside_submaps(self):
        self.assertEqual(self.set_up.taken_keys(), {Keys.parse("SUPER + CTRL + U"), Keys.parse("SUPER + RETURN")})

    def test_writes_the_shortcut_and_the_login_question_to_its_own_file(self):
        self.set_up.install(Keys.parse("SUPER + ALT + U"), "/bin/hiru-tsatsi")
        own = written(self.files, OWN)[0]
        self.assertIn('hl.bind("SUPER + ALT + U", hl.dsp.exec_cmd("/bin/hiru-tsatsi start"), '
                      '{ description = "Start work apps" })', own)
        self.assertIn('hl.on("hyprland.start", function()\n  hl.exec_cmd("/bin/hiru-tsatsi ask")\nend)', own)

    def test_adds_one_line_to_the_main_config_once_and_says_what_it_read(self):
        keys = Keys.parse("SUPER + ALT + U")
        self.set_up.install(keys, "w")
        self.files.write.assert_any_call(MAIN, MAIN_BEFORE + LOADS_OWN + "\n", read_before=MAIN_BEFORE, follow_link=True)
        self.assertEqual(len(written(self.files, MAIN)), 1)

    def test_leaves_the_main_config_alone_when_it_already_loads_its_file(self):
        files = files_holding({MAIN: MAIN_BEFORE + LOADS_OWN + "\n"})
        HyprlandSetUp(FOLDER, files, self.hyprctl).install(None, "w")
        self.assertEqual(written(files, MAIN), [])

    def test_reloads_hyprland_only_after_both_files_are_written(self):
        writes_seen_at_reload = []

        def reload_after_noting_writes(arguments: list[str]) -> str:
            writes_seen_at_reload.append(self.files.write.call_count)
            return self.hyprctl(arguments)

        HyprlandSetUp(FOLDER, self.files, reload_after_noting_writes).install(None, "w")
        self.assertEqual(self.hyprctl.calls, [["reload"], ["configerrors"]])
        self.assertEqual(writes_seen_at_reload[0], 2)

    def test_reads_back_the_shortcut_it_installed(self):
        own = 'hl.bind("SUPER + ALT + U", hl.dsp.exec_cmd("w start"), { description = "Start work apps" })\n'
        set_up = HyprlandSetUp(FOLDER, files_holding({OWN: own}), self.hyprctl)
        self.assertEqual(set_up.installed_keys(), Keys.parse("SUPER + ALT + U"))

    def test_no_shortcut_installed_yet(self):
        self.assertIsNone(self.set_up.installed_keys())

    def test_no_shortcut_still_adds_the_login_question(self):
        self.set_up.install(None, "w")
        own = written(self.files, OWN)[0]
        self.assertNotIn("hl.bind", own)
        self.assertIn('hl.on("hyprland.start"', own)

    def test_a_main_config_changed_meanwhile_leaves_hyprland_unreloaded(self):
        def refuse_the_main_config(path, text, read_before=None, follow_link=False):
            if path == MAIN:
                raise NotSaved("hyprland.lua changed meanwhile")
        self.files.write.side_effect = refuse_the_main_config
        with self.assertRaises(NotSaved):
            self.set_up.install(None, "w")
        self.assertEqual(len(written(self.files, OWN)), 1)
        self.assertEqual(self.hyprctl.calls, [])

    def test_config_errors_after_reloading_are_reported(self):
        failing = HyprlandSetUp(FOLDER, self.files, FakeHyprctl(errors="hiru-tsatsi.lua:1: bad"))
        with self.assertRaises(SetUpFailed):
            failing.install(None, "w")

    def test_a_command_path_with_a_space_or_quote_reaches_the_shell_as_one_word(self):
        self.set_up.install(None, "/home/sam o'neil/.local/bin/hiru-tsatsi")
        quoted = "'/home/sam o'\\\"'\\\"'neil/.local/bin/hiru-tsatsi'"
        self.assertIn(f'hl.exec_cmd("{quoted} ask")', written(self.files, OWN)[0])


if __name__ == "__main__":
    unittest.main()
