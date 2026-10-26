import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters.desktops.hyprland_set_up import HyprlandSetUp
from hiru_tsatsi.use_cases.ports import ConfigLeftAlone, SetUpFailed
from hiru_tsatsi.work_apps.shortcut import Keys

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
        self.set_up.install(keys, "/bin/hiru-tsatsi start", "/bin/hiru-tsatsi ask")
        self.set_up.install(keys, "/bin/hiru-tsatsi start", "/bin/hiru-tsatsi ask")
        own = (self.folder / "hiru-tsatsi.lua").read_text()
        self.assertIn('hl.bind("SUPER + ALT + U", hl.dsp.exec_cmd("/bin/hiru-tsatsi start"), { description = "Start work apps" })', own)
        self.assertIn('hl.on("hyprland.start", function()\n  hl.exec_cmd("/bin/hiru-tsatsi ask")\nend)', own)
        main = (self.folder / "hyprland.lua").read_text()
        self.assertEqual(main.count(f'dofile("{self.folder / "hiru-tsatsi.lua"}")'), 1)
        self.assertTrue(main.startswith('require("hypr.bindings")\n'))
        self.assertIn(["reload"], self.hyprctl.calls)

    def test_remembers_the_shortcut_it_installed(self):
        self.set_up.install(Keys.parse("SUPER + ALT + U"), "w start", "w ask")
        self.assertEqual(self.set_up.installed_keys(), Keys.parse("SUPER + ALT + U"))

    def test_no_shortcut_still_adds_the_login_question(self):
        self.set_up.install(None, "w start", "w ask")
        own = (self.folder / "hiru-tsatsi.lua").read_text()
        self.assertNotIn("hl.bind", own)
        self.assertIsNone(self.set_up.installed_keys())

    def test_a_linked_main_config_stays_a_link(self):
        kept = self.folder / "dotfiles" / "hyprland.lua"
        kept.parent.mkdir()
        (self.folder / "hyprland.lua").rename(kept)
        (self.folder / "hyprland.lua").symlink_to(kept)
        self.set_up.install(None, "w start", "w ask")
        self.assertTrue((self.folder / "hyprland.lua").is_symlink())
        self.assertIn("dofile(", kept.read_text())

    def test_a_main_config_edited_while_setting_up_is_left_alone(self):
        stale = "what set-up read before the owner saved an edit\n"
        with mock.patch("hiru_tsatsi.adapters.desktops.hyprland_set_up.text_or_nothing", return_value=stale), \
                self.assertRaises(ConfigLeftAlone):
            self.set_up.install(None, "w start", "w ask")
        self.assertEqual((self.folder / "hyprland.lua").read_text(), 'require("hypr.bindings")\n')
        self.assertNotIn(["reload"], self.hyprctl.calls)

    def test_config_errors_after_reloading_are_reported(self):
        failing = HyprlandSetUp(self.folder, FakeHyprctl(errors="hiru-tsatsi.lua:1: bad"))
        with self.assertRaises(SetUpFailed):
            failing.install(None, "w start", "w ask")


if __name__ == "__main__":
    unittest.main()
