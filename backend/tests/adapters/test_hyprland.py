import json
import unittest

from workbench.adapters.desktops.hyprland import ClassicDialect, Hyprland, LuaDialect
from workbench.work_apps.windows import Window

CLIENTS = [{"address": "0xa", "class": "steam", "title": "Steam", "workspace": {"id": 4}}]


class FakeHyprctl:
    def __init__(self, understands: str):
        self.understands = understands
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> str:
        self.calls.append(arguments)
        if arguments[:2] == ["clients", "-j"]:
            return json.dumps(CLIENTS)
        lua = arguments[1].startswith("hl.")
        return "ok" if lua == (self.understands == "lua") else "error"


class TalkingToHyprland(unittest.TestCase):
    def test_not_found_outside_hyprland(self):
        self.assertIsNone(Hyprland.found({}, FakeHyprctl("lua")))

    def test_the_dialect_hyprland_answers_to_is_chosen(self):
        for understands, dialect in (("lua", LuaDialect), ("classic", ClassicDialect)):
            with self.subTest(understands=understands):
                found = Hyprland.found({"HYPRLAND_INSTANCE_SIGNATURE": "x"}, FakeHyprctl(understands))
                self.assertIsInstance(found.dialect, dialect)

    def test_lists_windows(self):
        hyprland = Hyprland(LuaDialect(), FakeHyprctl("lua"))
        self.assertEqual(hyprland.windows(), [Window("0xa", "steam", "Steam", 4)])

    def test_lua_dialect_launches_and_moves_silently(self):
        hyprctl = FakeHyprctl("lua")
        hyprland = Hyprland(LuaDialect(), hyprctl)
        hyprland.launch('omarchy-launch-webapp "https://x"', 1)
        hyprland.move(Window("0xa", "steam", "Steam", 4), 6)
        self.assertEqual(hyprctl.calls, [
            ["dispatch", 'hl.dsp.exec_cmd("omarchy-launch-webapp \\"https://x\\"", { workspace = "1 silent" })'],
            ["dispatch", 'hl.dsp.window.move({ workspace = "6", follow = false, window = "address:0xa" })'],
        ])

    def test_classic_dialect_launches_and_moves_silently(self):
        hyprctl = FakeHyprctl("classic")
        hyprland = Hyprland(ClassicDialect(), hyprctl)
        hyprland.launch("steam", 6)
        hyprland.move(Window("0xa", "steam", "Steam", 4), 6)
        self.assertEqual(hyprctl.calls, [["dispatch", "exec [workspace 6 silent] steam"],
                                         ["dispatch", "movetoworkspacesilent 6,address:0xa"]])

    def test_unreadable_output_means_no_windows(self):
        hyprland = Hyprland(LuaDialect(), lambda arguments: "not json")
        self.assertEqual(hyprland.windows(), [])


if __name__ == "__main__":
    unittest.main()
