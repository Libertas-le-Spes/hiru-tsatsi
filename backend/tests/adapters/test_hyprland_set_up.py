import json
import tempfile
import unittest
from pathlib import Path

from workbench.adapters.desktops.hyprland_set_up import HyprlandSetUp
from workbench.use_cases.ports import SetUpFailed
from workbench.work_apps.shortcut import Keys

BINDS = [{"modmask": 68, "key": "U", "submap": ""}, {"modmask": 64, "key": "return", "submap": ""},
         {"modmask": 72, "key": "U", "submap": "resize"}]


class FakeHyprctl:
    def __init__(self, errors: str = ""):
        self.errors = errors
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> str:
        self.calls.append(arguments)
        return {"binds": json.dumps(BINDS), "configerrors": self.errors}.get(arguments[0], "ok")


class SettingUpHyprland(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "hyprland.lua").write_text('require("hypr.bindings")\n')
        self.hyprctl = FakeHyprctl()
        self.set_up = HyprlandSetUp(self.folder, self.hyprctl)

    def test_reads_which_shortcuts_are_taken_outside_submaps(self):
        self.assertEqual(self.set_up.taken_keys(), {Keys.parse("SUPER + CTRL + U"), Keys.parse("SUPER + RETURN")})

    def test_writes_its_own_file_and_loads_it_once_from_the_main_config(self):
        keys = Keys.parse("SUPER + ALT + U")
        self.set_up.install(keys, "/bin/workbench start", "/bin/workbench ask")
        self.set_up.install(keys, "/bin/workbench start", "/bin/workbench ask")
        own = (self.folder / "workbench.lua").read_text()
        self.assertIn('hl.bind("SUPER + ALT + U", hl.dsp.exec_cmd("/bin/workbench start"), { description = "Start work apps" })', own)
        self.assertIn('hl.on("hyprland.start", function()\n  hl.exec_cmd("/bin/workbench ask")\nend)', own)
        main = (self.folder / "hyprland.lua").read_text()
        self.assertEqual(main.count(f'dofile("{self.folder / "workbench.lua"}")'), 1)
        self.assertTrue(main.startswith('require("hypr.bindings")\n'))
        self.assertIn(["reload"], self.hyprctl.calls)

    def test_remembers_the_shortcut_it_installed(self):
        self.set_up.install(Keys.parse("SUPER + ALT + U"), "w start", "w ask")
        self.assertEqual(self.set_up.installed_keys(), Keys.parse("SUPER + ALT + U"))

    def test_no_shortcut_still_adds_the_login_question(self):
        self.set_up.install(None, "w start", "w ask")
        own = (self.folder / "workbench.lua").read_text()
        self.assertNotIn("hl.bind", own)
        self.assertIsNone(self.set_up.installed_keys())

    def test_config_errors_after_reloading_are_reported(self):
        failing = HyprlandSetUp(self.folder, FakeHyprctl(errors="workbench.lua:1: bad"))
        with self.assertRaises(SetUpFailed):
            failing.install(None, "w start", "w ask")


if __name__ == "__main__":
    unittest.main()
